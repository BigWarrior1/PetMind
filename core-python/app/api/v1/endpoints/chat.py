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
