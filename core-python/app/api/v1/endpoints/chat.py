"""
聊天端点
提供基于 RAG 的问答接口
"""

from fastapi import APIRouter, HTTPException, status

from app.core.logging import logger
from app.models.request import ChatRequest
from app.models.response import ChatResponse, ErrorResponse
from app.services.rag_service import get_rag_service

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        500: {"model": ErrorResponse, "description": "服务器内部错误"},
    },
    summary="智能问答",
    description="基于 RAG 的宠物健康问答，支持个性化宠物档案",
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    智能问答接口

    Args:
        request: 聊天请求

    Returns:
        聊天响应
    """
    try:
        logger.info(f"收到问答请求: question={request.question[:50]}...")

        # 获取 RAG 服务
        rag_service = get_rag_service()

        # 执行 RAG 问答
        result = await rag_service.answer_question(
            question=request.question,
            pet_profile=request.pet_profile,
        )

        # 构造响应
        response = ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result.get("confidence"),
            warning=result.get("warning"),
            session_id=request.session_id,
        )

        logger.info("问答请求处理完成")
        return response

    except Exception as e:
        logger.error(f"处理问答请求时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理请求时发生错误: {str(e)}",
        )
