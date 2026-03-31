"""
LLM 服务
调用阿里百炼 qwen-plus / qwen-vl-plus 模型
"""
import os
from typing import Optional, List, Dict
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from app.core.config import DASHSCOPE_API_KEY

# 默认模型
DEFAULT_MODEL = "qwen-plus"
VL_MODEL = "qwen-vl-plus"


class LLMService:
    """LLM 服务类"""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or DASHSCOPE_API_KEY
        self.model = model
        self._chat_model: Optional[ChatTongyi] = None

    def get_chat_model(self) -> ChatTongyi:
        """获取聊天模型实例"""
        if self._chat_model is None:
            self._chat_model = ChatTongyi(
                model=self.model,
            )
        return self._chat_model

    def chat(self, messages: List[BaseMessage]) -> str:
        """
        聊天接口

        Args:
            messages: 消息列表

        Returns:
            AI 回复文本
        """
        chat_model = self.get_chat_model()
        response = chat_model.invoke(messages)
        return response.content

    def chat_with_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """
        简易聊天接口

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户输入

        Returns:
            AI 回复文本
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        return self.chat(messages)

    def analyze_image(self, image_path: str, user_prompt: str) -> str:
        """
        图片分析接口 (多模态)

        Args:
            image_path: 图片路径
            user_prompt: 关于图片的问题

        Returns:
            分析结果
        """
        # TODO: 实现多模态图片分析
        raise NotImplementedError("多模态分析待实现")


# 全局单例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取全局 LLM 服务实例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
