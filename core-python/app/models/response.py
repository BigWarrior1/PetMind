"""
响应数据模型
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentSource(BaseModel):
    """文档来源模型"""

    content: str = Field(..., description="文档内容")
    source: str = Field(..., description="文档来源")
    score: Optional[float] = Field(None, description="相似度分数")


class ChatResponse(BaseModel):
    """聊天响应模型"""

    answer: str = Field(..., description="回答内容")

    sources: List[DocumentSource] = Field(
        default_factory=list,
        description="知识来源（可追溯）",
    )

    confidence: Optional[float] = Field(
        None,
        description="置信度（0-1）",
        ge=0.0,
        le=1.0,
    )

    warning: Optional[str] = Field(
        None,
        description="安全提示（如建议就医）",
    )

    session_id: Optional[str] = Field(
        None,
        description="会话 ID",
    )


class HealthCheckResponse(BaseModel):
    """健康检查响应"""

    status: str = Field(default="healthy", description="服务状态")
    version: str = Field(default="0.1.0", description="服务版本")
    vectorstore_count: int = Field(default=0, description="向量库文档数量")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细信息")
