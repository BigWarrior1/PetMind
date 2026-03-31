"""
健康检查 API
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "petmind-ai",
        "version": "1.0.0",
    }
