"""
RAG 服务
整合检索与生成
"""
from typing import Optional, Dict, List
from app.rag.retriever import RAGRetriever
from app.services.llm_service import get_llm_service
from app.core.config import RAG_TOP_K


# 默认系统提示词
DEFAULT_SYSTEM_PROMPT = """你是一个专业的宠物健康顾问。

你的职责：
1. 基于提供的知识库内容，准确回答用户关于宠物健康的问题
2. 当情况危急时（如高烧，呼吸困难、严重出血等），提醒用户立即就医
3. 始终强调：你的建议仅供参考，不能替代执业兽医的诊断

回答模式（自动判断）：
1. 如果用户询问的是知识性/科普性问题（如"能不能吃"、"有哪些"、"是什么"），直接回答
2. 如果用户描述的是症状但缺少关键信息（如只说"狗吐了"没说颜色频率），**先追问关键信息再回答**
3. 如果用户描述的症状信息充分（如说了颜色、频率、精神状态等），直接给出分析和建议

追问规则：
- 每次追问不超过 3 个问题
- 问题要具体：颜色、形状、频率、持续时间、精神状态等
- 保持友好、专业的语气，像真实问诊一样

综合回答时要包含：
- 可能的原因分析
- 严重程度评估（轻微/中等/严重）
- 建议的护理措施
- 何时必须就医

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

# 摘要生成系统提示词
SUMMARIZE_SYSTEM_PROMPT = """你是一个宠物对话摘要助手。

你的任务是将用户与助手的对话历史压缩成一个简洁的摘要。

摘要要求：
1. 提取并记录：宠物名字、种类（猫/狗）、品种、年龄，体重等基本信息
2. 记录讨论过的健康问题、症状或疾病（如果有）
3. 记录用户的特殊偏好或要求（如果有）
4. 记录正在进行的讨论话题或未解决的问题
5. 摘要应该简洁，最多5-6句话

输出格式：
- 使用中文
- 使用自然段落，不要使用列表或结构化格式
- 只需输出摘要内容，不要有任何前缀或解释

示例：
"用户有一只3岁的金毛犬叫旺财，体重30公斤。讨论过狗狗最近食欲下降的问题，怀疑可能是消化不良。用户提到旺财最近有点嗜睡。正在等待用户反馈喂食益生菌后的效果。"
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
        history: Optional[List[str]] = None,
        session_summary: Optional[str] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> Dict:
        """
        问答接口

        Args:
            question: 用户问题
            pet_info: 宠物信息（可选）
            history: 对话历史（可选），格式 ["user:xxx", "assistant:xxx"]
            session_summary: 会话摘要（可选），包含之前对话的重要信息
            system_prompt: 系统提示词

        Returns:
            {
                "answer": "回答内容",
                "sources": [{"source": "来源", "score": 0.9}, ...],
                "warning": "就医警示（如有）"
            }
        """
        # 0. 构建上下文（按优先级）
        context_parts = []

        # 优先添加 session summary
        if session_summary:
            context_parts.append(f"会话摘要：\n{session_summary}")

        # 添加对话历史
        if history:
            context_parts.append("对话历史：\n" + "\n".join(history))

        history_context = "\n\n".join(context_parts)
        if history_context:
            history_context = "\n\n" + history_context + "\n"

        # 1. 检索相关文档
        documents, sources = self.retriever.retrieve_with_sources(question)

        # 2. 构建宠物信息上下文
        pet_context = ""
        if pet_info:
            pet_context = f"\n\n用户宠物信息：\n- 种类：{pet_info.get('species', '未知')}\n- 品种：{pet_info.get('breed', '未知')}\n- 年龄：{pet_info.get('age', '未知')}\n- 体重：{pet_info.get('weight', '未知')}\n"

        if not documents:
            # 降级方案：知识库没有相关内容时，让 LLM 用通用知识回答
            fallback_prompt = f"""{history_context}用户问题：{question}
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
        full_prompt = f"""{history_context}基于以下知识库内容回答用户问题：

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
            "sources": [{"source": s["source"], "score": s.get("semantic_score", 0)} for s in sources],
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

    def summarize(self, messages: List[str]) -> str:
        """
        生成会话摘要

        Args:
            messages: 对话历史，格式 ["user:xxx", "assistant:xxx", ...]

        Returns:
            压缩后的摘要字符串
        """
        if not messages:
            return ""

        # 构建对话历史文本
        history_text = "\n".join(messages)

        # 构建提示词
        prompt = f"""对话历史：
{history_text}

请生成上述对话的摘要："""

        # 调用 LLM 生成摘要
        summary = self.llm_service.chat_with_prompt(
            system_prompt=SUMMARIZE_SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        return summary.strip()


# 全局单例
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """获取全局 RAG 服务实例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
