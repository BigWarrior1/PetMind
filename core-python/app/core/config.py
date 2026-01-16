"""
应用配置管理
使用 pydantic-settings 从环境变量加载配置
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =============================================
    # 阿里百炼平台配置
    # =============================================
    dashscope_api_key: str = Field(
        ...,
        description="阿里百炼 API 密钥",
        alias="DASHSCOPE_API_KEY",
    )

    # =============================================
    # 模型配置
    # =============================================
    llm_model: str = Field(
        default="qwen-plus",
        description="LLM 模型名称",
        alias="LLM_MODEL",
    )

    vl_model: str = Field(
        default="qwen-vl-plus",
        description="多模态模型名称",
        alias="VL_MODEL",
    )

    embedding_model: str = Field(
        default="text-embedding-v3",
        description="嵌入模型名称",
        alias="EMBEDDING_MODEL",
    )

    # =============================================
    # 向量数据库配置
    # =============================================
    chroma_persist_dir: str = Field(
        default="./data/vectorstore/chroma_db",
        description="Chroma 持久化目录",
        alias="CHROMA_PERSIST_DIR",
    )

    chroma_collection_name: str = Field(
        default="pet_health_kb",
        description="Chroma 集合名称",
    )

    # =============================================
    # 数据库配置
    # =============================================
    database_url: str = Field(
        default="sqlite:///./pet_health.db",
        description="数据库连接 URL",
        alias="DATABASE_URL",
    )

    # =============================================
    # 服务配置
    # =============================================
    api_port: int = Field(
        default=8000,
        description="FastAPI 服务端口",
        alias="API_PORT",
    )

    api_host: str = Field(
        default="0.0.0.0",
        description="FastAPI 服务地址",
        alias="API_HOST",
    )

    log_level: str = Field(
        default="INFO",
        description="日志级别",
        alias="LOG_LEVEL",
    )

    # =============================================
    # RAG 配置
    # =============================================
    chunk_size: int = Field(
        default=500,
        description="文档切分大小",
    )

    chunk_overlap: int = Field(
        default=50,
        description="文档切分重叠大小",
    )

    retriever_k: int = Field(
        default=5,
        description="检索返回的文档数量",
    )

    # =============================================
    # LLM 配置
    # =============================================
    llm_temperature: float = Field(
        default=0.7,
        description="LLM 温度参数",
    )

    llm_max_tokens: int = Field(
        default=1500,
        description="LLM 最大生成 token 数",
    )

    # =============================================
    # 路径配置
    # =============================================
    @property
    def project_root(self) -> Path:
        """项目根目录"""
        return Path(__file__).parent.parent.parent

    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return self.project_root / "data"

    @property
    def prompts_dir(self) -> Path:
        """Prompt 模板目录"""
        return self.project_root / "prompts"


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings()
