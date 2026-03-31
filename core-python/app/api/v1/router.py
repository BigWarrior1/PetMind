"""
API v1 路由
"""
from fastapi import APIRouter

router = APIRouter()

# 路由导入
from app.api.v1.endpoints import chat, health, multimodal
router.include_router(chat.router, tags=["chat"])
router.include_router(health.router, tags=["health"])
router.include_router(multimodal.router, tags=["multimodal"])
