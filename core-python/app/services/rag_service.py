"""
RAG 服务
实现检索增强生成的完整流程
"""

from pathlib import Path
from typing import Dict, List, Optional

from app.core.config import settings
from app.core.logging import logger
from app.models.response import DocumentSource
from app.rag.retriever import Retriever, get_retriever
from app.services.llm_service import LLMService, get_llm_service


class RAGService:
    """RAG 检索增强生成服务"""

    def __init__(
        self,
        retriever: Optional[Retriever] = None,
        llm_service: Optional[LLMService] = None,
    ):
        """
        初始化 RAG 服务

        Args:
            retriever: 检索器
            llm_service: LLM 服务
        """
        self.retriever = retriever or get_retriever()
        self.llm_service = llm_service or get_llm_service()

        # 加载 Prompt 模板
        self.rag_prompt_template = self._load_prompt_template()

        logger.info("初始化 RAG 服务")

    def _load_prompt_template(self) -> str:
        """加载 RAG Prompt 模板"""
        try:
            prompt_path = settings.prompts_dir / "rag_prompt.txt"

            if prompt_path.exists():
                with open(prompt_path, "r", encoding="utf-8") as f:
                    template = f.read()
                logger.info(f"加载 Prompt 模板: {prompt_path}")
                return template
            else:
                # 默认模板
                logger.warning("Prompt 模板文件不存在，使用默认模板")
                return self._get_default_prompt_template()

        except Exception as e:
            logger.error(f"加载 Prompt 模板失败: {str(e)}")
            return self._get_default_prompt_template()

    @staticmethod
    def _get_default_prompt_template() -> str:
        """获取默认 Prompt 模板"""
        return """你是一个专业的宠物健康助手，基于权威的兽医资料为用户提供信息参考。

【重要提示】
1. 你只能基于提供的知识库内容回答问题，不要编造信息
2. 如果知识库中没有相关信息，请明确告知用户
3. 你的回答仅供参考，不能替代执业兽医的诊断
4. 遇到严重症状，务必建议用户及时就医

【知识库内容】
{context}

【用户问题】
{question}

{pet_profile}

【回答要求】
1. 基于知识库内容给出专业、客观的答案
2. 明确指出信息来源
3. 如果涉及严重症状或紧急情况，提醒用户立即就医
4. 使用清晰、易懂的语言，避免过于专业的术语

请回答："""

    def _format_pet_profile(self, pet_profile: Optional[dict]) -> str:
        """格式化宠物档案信息"""
        if not pet_profile:
            return ""

        profile_str = "\n【宠物档案】\n"

        if "species" in pet_profile:
            profile_str += f"物种: {pet_profile['species']}\n"
        if "breed" in pet_profile:
            profile_str += f"品种: {pet_profile['breed']}\n"
        if "age" in pet_profile:
            profile_str += f"年龄: {pet_profile['age']}岁\n"
        if "weight" in pet_profile:
            profile_str += f"体重: {pet_profile['weight']}kg\n"
        if "medical_history" in pet_profile:
            profile_str += f"病史: {pet_profile['medical_history']}\n"

        return profile_str

    async def answer_question(
        self,
        question: str,
        pet_profile: Optional[dict] = None,
        k: int = 5,
    ) -> Dict:
        """
        回答用户问题（RAG 完整流程）

        Args:
            question: 用户问题
            pet_profile: 宠物档案信息
            k: 检索文档数量

        Returns:
            包含答案、来源、置信度等信息的字典
        """
        try:
            logger.info(f"RAG 问答: question={question[:50]}...")

            # 1. 检索相关文档
            results = self.retriever.retrieve_with_scores(query=question, k=k)

            if not results:
                logger.warning("未检索到相关文档")
                return {
                    "answer": "抱歉，我的知识库中暂时没有与您问题相关的信息。建议您咨询专业兽医获取帮助。",
                    "sources": [],
                    "confidence": 0.0,
                    "warning": "⚠️ 请及时联系执业兽医进行专业诊断",
                }

            # 2. 格式化检索到的文档
            context_parts = []
            sources = []

            for i, (doc, score) in enumerate(results, 1):
                content = doc.page_content
                source = doc.metadata.get("source", "未知来源")

                context_parts.append(f"【文档 {i}】（相似度: {score:.2f}）\n{content}")

                sources.append(
                    DocumentSource(
                        content=content[:200] + "..." if len(content) > 200 else content,
                        source=source,
                        score=float(score),
                    )
                )

            context = "\n\n".join(context_parts)

            # 3. 构造完整 Prompt
            pet_profile_str = self._format_pet_profile(pet_profile)

            prompt = self.rag_prompt_template.format(
                context=context,
                question=question,
                pet_profile=pet_profile_str,
            )

            # 4. 调用 LLM 生成答案
            answer = await self.llm_service.agenerate(prompt=prompt)

            # 5. 计算置信度（基于检索结果的平均相似度）
            avg_score = sum(score for _, score in results) / len(results)
            confidence = float(avg_score)

            # 6. 生成安全警告
            warning = self._generate_warning(question, answer)

            logger.info("RAG 问答完成")

            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence,
                "warning": warning,
            }

        except Exception as e:
            logger.error(f"RAG 问答时发生错误: {str(e)}")
            raise

    def _generate_warning(self, question: str, answer: str) -> Optional[str]:
        """
        生成安全警告
        检测关键词，提醒用户及时就医
        """
        # 紧急症状关键词
        emergency_keywords = [
            "高烧",
            "呕吐",
            "腹泻",
            "出血",
            "呼吸困难",
            "休克",
            "抽搐",
            "中毒",
            "昏迷",
            "骨折",
            "严重",
            "急性",
        ]

        question_lower = question.lower()
        answer_lower = answer.lower()

        for keyword in emergency_keywords:
            if keyword in question_lower or keyword in answer_lower:
                return (
                    "⚠️ 重要提示：检测到可能的紧急症状，建议您立即联系执业兽医进行专业诊断和治疗。"
                    "本系统提供的信息仅供参考，不能替代专业医疗服务。"
                )

        # 默认警告
        return "💡 提示：本系统提供的信息仅供参考，如有疑问请咨询专业兽医。"


def get_rag_service() -> RAGService:
    """获取 RAG 服务实例"""
    return RAGService()
