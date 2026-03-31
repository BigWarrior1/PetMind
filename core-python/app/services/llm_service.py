"""
LLM 服务
调用阿里百炼 qwen3.5-plus 模型（统一多模态：文本 + 图片）
"""
import base64
from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from app.core.config import DASHSCOPE_API_KEY

# 模型配置
DEFAULT_MODEL = "qwen3.5-plus"  # 统一多模态模型

# API 配置
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


class LLMService:
    """LLM 服务类"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        base_url: str = DASHSCOPE_BASE_URL,
    ):
        self.api_key = api_key or DASHSCOPE_API_KEY
        self.model = model
        self.base_url = base_url
        self._chat_model: Optional[ChatOpenAI] = None

    def get_chat_model(self) -> ChatOpenAI:
        """获取聊天模型实例"""
        if self._chat_model is None:
            self._chat_model = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                base_url=self.base_url,
                temperature=0.7,
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

    def _load_image_as_base64(self, image_path: str) -> str:
        """
        将图片转换为 base64 编码

        Args:
            image_path: 图片路径

        Returns:
            base64 编码字符串
        """
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            # 获取图片类型
            ext = image_path.lower().split(".")[-1]
            if ext == "jpg":
                ext = "jpeg"
            return f"data:image/{ext};base64,{encoded_string}"

    def analyze_image(
        self,
        image_path: str,
        user_prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        图片分析接口 (多模态)

        Args:
            image_path: 图片路径
            user_prompt: 关于图片的问题
            system_prompt: 系统提示词（可选）

        Returns:
            分析结果
        """
        # 加载图片为 base64
        image_data = self._load_image_as_base64(image_path)

        # 构建多模态消息
        content = [
            {
                "type": "text",
                "text": user_prompt,
            },
            {
                "type": "image_url",
                "image_url": {"url": image_data},
            },
        ]

        messages = [HumanMessage(content=content)]

        if system_prompt:
            messages.insert(0, SystemMessage(content=system_prompt))

        return self.chat(messages)

    def analyze_images(
        self,
        image_paths: List[str],
        user_prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        多图分析接口

        Args:
            image_paths: 图片路径列表
            user_prompt: 关于图片的问题
            system_prompt: 系统提示词（可选）

        Returns:
            分析结果
        """
        content = [
            {
                "type": "text",
                "text": user_prompt,
            },
        ]

        # 添加多张图片
        for image_path in image_paths:
            image_data = self._load_image_as_base64(image_path)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": image_data},
                }
            )

        messages = [HumanMessage(content=content)]

        if system_prompt:
            messages.insert(0, SystemMessage(content=system_prompt))

        return self.chat(messages)


# 全局单例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取全局 LLM 服务实例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
