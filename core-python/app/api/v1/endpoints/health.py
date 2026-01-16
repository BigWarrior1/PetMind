"""
健康检查端点
"""

from fastapi import APIRouter

from app.core.logging import logger
from app.models.response import HealthCheckResponse
from app.rag.vectorstore import get_vectorstore

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="健康检查",
    description="检查服务状态和向量库连接",
)
async def health_check() -> HealthCheckResponse:
    """
    健康检查接口

    Returns:
        健康状态响应
    """
    try:
        logger.debug("执行健康检查")

        # 检查向量库
        vectorstore = get_vectorstore()
        count = vectorstore.get_collection_count()

        return HealthCheckResponse(
            status="healthy",
            version="0.1.0",
            vectorstore_count=count,
        )

    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            version="0.1.0",
            vectorstore_count=0,
        )
