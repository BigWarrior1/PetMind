"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PetMind AI Service",
    description="宠物健康智能问答系统 - AI 核心服务",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "petmind-ai"}


# 路由导入
from app.api.v1 import router as api_v1
app.include_router(api_v1.router, prefix="/api/v1")
