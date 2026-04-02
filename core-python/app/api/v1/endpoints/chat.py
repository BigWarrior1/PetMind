"""
聊天问答 API
"""
from typing import Optional, Dict, List, AsyncGenerator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio

from app.services.rag_service import get_rag_service
from app.services.llm_service import get_llm_service

router = APIRouter()


class PetInfo(BaseModel):
    """宠物信息"""
    species: Optional[str] = None  # 种类（狗、猫）
    breed: Optional[str] = None  # 品种
    age: Optional[str] = None  # 年龄
    weight: Optional[str] = None  # 体重


class ChatRequest(BaseModel):
    """聊天请求"""
    question: str
    pet_info: Optional[PetInfo] = None
    history: Optional[List[str]] = None  # 对话历史 ["user:xxx", "assistant:xxx", ...]
    session_summary: Optional[str] = None  # 会话摘要


class Source(BaseModel):
    """来源信息"""
    source: str
    score: float


class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str
    sources: List[Source]
    warning: Optional[str] = None


class SummarizeRequest(BaseModel):
    """摘要请求"""
    messages: List[str]  # 对话历史 ["user:xxx", "assistant:xxx", ...]


class SummarizeResponse(BaseModel):
    """摘要响应"""
    summary: str


class GenerateTitleRequest(BaseModel):
    """生成标题请求"""
    message: str  # 第一条用户消息


class GenerateTitleResponse(BaseModel):
    """生成标题响应"""
    title: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    RAG 智能问答接口

    - 输入问题，返回基于知识库的回答
    - 可选提供宠物信息以获得更精准的回答
    - 可选提供对话历史以支持多轮对话
    - 可选提供会话摘要以记住重要信息
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    rag_service = get_rag_service()

    pet_info_dict = None
    if request.pet_info:
        pet_info_dict = request.pet_info.model_dump()

    result = rag_service.ask(
        question=request.question,
        pet_info=pet_info_dict,
        history=request.history,
        session_summary=request.session_summary,
    )

    return ChatResponse(
        answer=result["answer"],
        sources=[Source(**s) for s in result["sources"]],
        warning=result["warning"],
    )


# 流式问答系统提示词
STREAM_CHAT_SYSTEM_PROMPT = """你是 PetMind，一个专业的宠物健康顾问。

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
- 语言通俗易懂，适合普通宠物主人理解
"""


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式 RAG 智能问答接口

    - 输入问题，流式返回基于知识库的回答
    - 可选提供宠物信息以获得更精准的回答
    - 可选提供对话历史以支持多轮对话
    - 可选提供会话摘要以记住重要信息
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    async def generate():
        # 构建上下文
        context_parts = []

        if request.session_summary:
            context_parts.append(f"会话摘要：\n{request.session_summary}")

        if request.history:
            context_parts.append("对话历史：\n" + "\n".join(request.history))

        history_context = "\n\n".join(context_parts)
        if history_context:
            history_context = "\n\n" + history_context + "\n"

        # 检索知识库
        rag_service = get_rag_service()
        documents, sources = rag_service.retriever.retrieve_with_sources(request.question)

        # 构建宠物信息上下文
        pet_context = ""
        if request.pet_info:
            pet_info = request.pet_info.model_dump() if request.pet_info else {}
            pet_context = f"\n\n用户宠物信息：\n- 种类：{pet_info.get('species', '未知')}\n- 品种：{pet_info.get('breed', '未知')}\n- 年龄：{pet_info.get('age', '未知')}\n- 体重：{pet_info.get('weight', '未知')}\n"

        # 构建提示词
        if documents:
            context = "\n\n".join([doc.page_content for doc in documents])
            full_prompt = f"""{history_context}基于以下知识库内容回答用户问题：

知识库内容：
{context}
{pet_context}

用户问题：{request.question}

请根据知识库内容回答用户问题。"""
            system_prompt = STREAM_CHAT_SYSTEM_PROMPT
        else:
            full_prompt = f"""{history_context}用户问题：{request.question}
{pet_context}

请回答用户的问题。"""
            system_prompt = """你是 PetMind，一个专业的宠物健康顾问。

请基于你的知识回答用户关于宠物健康的问题。

当情况危急时（如高烧，呼吸困难、严重出血等），提醒用户立即就医。

始终强调：你的建议仅供参考，不能替代执业兽医的诊断。

回答要求：
- 语言通俗易懂，适合普通宠物主人理解
- 如果不确定，明确告知用户建议咨询专业兽医
"""

        # 使用 LLM 流式生成
        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=full_prompt),
        ]

        llm_service = get_llm_service()

        # 流式 yield 每个 token
        for chunk in llm_service.chat_stream(messages):
            yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            await asyncio.sleep(0)  # 让出控制权

        # 流式结束后，发送 sources 和 warning
        warning = None
        if documents:
            # 检查是否需要就医警示
            warning_keywords = ["高烧", "呼吸困难", "严重出血", "昏迷", "中毒", "骨折", "休克"]
            for keyword in warning_keywords:
                if keyword in request.question:
                    warning = "⚠️ 根据您描述的症状，建议立即带宠物前往最近的宠物医院就诊！"
                    break

        yield f"data: {json.dumps({'type': 'done', 'sources': sources, 'warning': warning})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    """
    会话摘要接口

    将对话历史压缩为简洁的摘要，提取关键信息：
    - 宠物信息（名字、种类、品种等）
    - 讨论的健康问题或症状
    - 用户偏好或特殊要求
    - 正在进行的讨论话题
    """
    rag_service = get_rag_service()

    summary = rag_service.summarize(request.messages)

    return SummarizeResponse(summary=summary)


# 生成标题的系统提示词
TITLE_SYSTEM_PROMPT = """你是一个会话标题生成助手。

你的任务是根据用户的第一条消息生成一个简短的会话标题。

要求：
1. 标题长度：10-20个字
2. 标题应该概括用户询问的核心主题
3. 只返回标题，不要有任何解释、前缀或标点符号

示例：
- 用户消息："我的狗最近食欲不振怎么办" → 生成标题：狗狗食欲不振咨询
- 用户消息："猫咪掉毛很严重" → 生成标题：猫咪掉毛问题
- 用户消息："请教我如何给狗洗澡" → 生成标题：狗狗洗澡方法"""


@router.post("/generate_title", response_model=GenerateTitleResponse)
async def generate_title(request: GenerateTitleRequest):
    """
    生成会话标题接口

    根据用户的第一条消息生成简短的会话标题（10-20字）
    """
    from app.services.llm_service import get_llm_service

    llm_service = get_llm_service()
    title = llm_service.chat_with_prompt(
        system_prompt=TITLE_SYSTEM_PROMPT,
        user_prompt=f"用户第一条消息：{request.message}\n\n请生成会话标题：",
    )

    return GenerateTitleResponse(title=title.strip())
