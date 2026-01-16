"""
FastAPI 应用入口
宠物健康智能问答系统 - AI 服务
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("=" * 60)
    logger.info("宠物健康智能问答系统 - AI 服务启动")
    logger.info(f"服务地址: http://{settings.api_host}:{settings.api_port}")
    logger.info(f"API 文档: http://{settings.api_host}:{settings.api_port}/docs")
    logger.info(f"LLM 模型: {settings.llm_model}")
    logger.info(f"嵌入模型: {settings.embedding_model}")
    logger.info("=" * 60)

    yield

    # 关闭时
    logger.info("服务关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="宠物健康智能问答系统",
    description="基于 LLM + RAG 的宠物健康信息辅助系统",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未捕获的异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "服务器内部错误",
            "detail": str(exc),
        },
    )


# 注册路由
app.include_router(api_router, prefix="/api/v1")


# 根路径
@app.get("/", tags=["root"])
async def root():
    """根路径"""
    return {
        "message": "宠物健康智能问答系统 API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
