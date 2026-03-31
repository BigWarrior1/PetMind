"""
RAG 服务
整合检索与生成
"""
from typing import Optional, Dict
from app.rag.retriever import RAGRetriever
from app.services.llm_service import get_llm_service
from app.core.config import RAG_TOP_K


# 默认系统提示词
DEFAULT_SYSTEM_PROMPT = """你是一个专业的宠物健康顾问。

你的职责：
1. 基于提供的知识库内容，准确回答用户关于宠物健康的问题
2. 当情况危急时（如高烧，呼吸困难、严重出血等），提醒用户立即就医
3. 始终强调：你的建议仅供参考，不能替代执业兽医的诊断

回答要求：
- 基于事实，不要编造信息
- 引用知识库中的来源
- 语言通俗易懂，适合普通宠物主人理解
"""

# 降级方案的系统提示词（知识库没有相关内容时使用）
FALLBACK_SYSTEM_PROMPT = """你是一个专业的宠物健康顾问。

重要说明：
1. 知识库中没有找到与用户问题相关的专业资料
2. 请基于你的通用知识回答用户关于宠物健康的问题
3. 回答时必须明确告知用户"以下回答基于通用知识，知识库中未找到相关资料"
4. 当情况危急时（如高烧，呼吸困难、严重出血等），提醒用户立即就医
5. 始终强调：你的建议仅供参考，不能替代执业兽医的诊断

回答要求：
- 尽量准确，但承认知识的局限性
- 语言通俗易懂，适合普通宠物主人理解
- 如果不确定，明确告知用户建议咨询专业兽医
"""


class RAGService:
    """RAG 服务类"""

    def __init__(self, top_k: int = RAG_TOP_K):
        self.retriever = RAGRetriever(top_k=top_k)
        self.llm_service = get_llm_service()

    def ask(
        self,
        question: str,
        pet_info: Optional[Dict] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> Dict:
        """
        问答接口

        Args:
            question: 用户问题
            pet_info: 宠物信息（可选）
            system_prompt: 系统提示词

        Returns:
            {
                "answer": "回答内容",
                "sources": [{"source": "来源", "score": 0.9}, ...],
                "warning": "就医警示（如有）"
            }
        """
        # 1. 检索相关文档
        documents, sources = self.retriever.retrieve_with_sources(question)

        # 2. 构建宠物信息上下文
        pet_context = ""
        if pet_info:
            pet_context = f"\n\n用户宠物信息：\n- 种类：{pet_info.get('species', '未知')}\n- 品种：{pet_info.get('breed', '未知')}\n- 年龄：{pet_info.get('age', '未知')}\n- 体重：{pet_info.get('weight', '未知')}\n"

        if not documents:
            # 降级方案：知识库没有相关内容时，让 LLM 用通用知识回答
            fallback_prompt = f"""用户问题：{question}
{pet_context}

请回答用户的问题。"""
            answer = self.llm_service.chat_with_prompt(
                system_prompt=FALLBACK_SYSTEM_PROMPT,
                user_prompt=fallback_prompt,
            )
            warning = self._check_warning(question, answer)
            return {
                "answer": answer,
                "sources": [],
                "warning": warning,
            }

        # 3. 构建上下文（知识库有相关内容时）
        context = "\n\n".join([doc.page_content for doc in documents])

        # 4. 构建完整提示词
        full_prompt = f"""基于以下知识库内容回答用户问题：

知识库内容：
{context}
{pet_context}

用户问题：{question}

请根据知识库内容回答用户问题。"""

        # 5. 调用 LLM
        answer = self.llm_service.chat_with_prompt(
            system_prompt=system_prompt,
            user_prompt=full_prompt,
        )

        # 6. 检查是否需要就医警示
        warning = self._check_warning(question, answer)

        return {
            "answer": answer,
            "sources": sources,
            "warning": warning,
        }

    def _check_warning(self, question: str, answer: str) -> Optional[str]:
        """检查是否需要就医警示"""
        keywords = ["高烧", "呼吸困难", "严重出血", "昏迷", "中毒", "骨折", "休克"]
        answer_lower = answer.lower()

        for keyword in keywords:
            if keyword in question or keyword in answer:
                return "⚠️ 根据您描述的症状，建议立即带宠物前往最近的宠物医院就诊！"

        return None


# 全局单例
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """获取全局 RAG 服务实例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
