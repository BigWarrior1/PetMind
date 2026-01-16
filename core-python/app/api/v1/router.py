"""
API v1 路由聚合
"""

from fastapi import APIRouter

from app.api.v1.endpoints import chat, health

api_router = APIRouter()

# 注册端点
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(health.router, tags=["health"])
