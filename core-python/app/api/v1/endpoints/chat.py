"""
聊天问答 API
"""
from typing import Optional, Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.rag_service import get_rag_service

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
