"""
请求数据模型
"""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求模型"""

    question: str = Field(
        ...,
        description="用户问题",
        min_length=1,
        max_length=500,
        examples=["我家狗狗出现高烧和咳嗽怎么办？"],
    )

    pet_profile: Optional[dict] = Field(
        default=None,
        description="宠物档案信息（可选）",
        examples=[
            {
                "species": "犬",
                "breed": "金毛",
                "age": 3,
                "weight": 30,
                "medical_history": "无",
            }
        ],
    )

    use_history: bool = Field(
        default=False,
        description="是否使用对话历史",
    )

    session_id: Optional[str] = Field(
        default=None,
        description="会话 ID（用于多轮对话）",
    )


class HealthCheckRequest(BaseModel):
    """健康检查请求（用于服务监控）"""

    pass
