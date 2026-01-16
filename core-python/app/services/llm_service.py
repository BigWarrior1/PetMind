"""
LLM 服务
封装阿里百炼大语言模型调用
"""

from typing import Optional

import dashscope
from dashscope import Generation

from app.core.config import settings
from app.core.logging import logger


class LLMService:
    """大语言模型服务"""

    def __init__(
        self,
        model: str = settings.llm_model,
        api_key: str = settings.dashscope_api_key,
        temperature: float = settings.llm_temperature,
        max_tokens: int = settings.llm_max_tokens,
    ):
        """
        初始化 LLM 服务

        Args:
            model: 模型名称
            api_key: API 密钥
            temperature: 温度参数
            max_tokens: 最大生成 token 数
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        dashscope.api_key = api_key

        logger.info(
            f"初始化 LLM 服务: model={model}, temperature={temperature}, "
            f"max_tokens={max_tokens}"
        )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        生成回答

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数（覆盖默认值）
            max_tokens: 最大 token 数（覆盖默认值）

        Returns:
            生成的文本
        """
        try:
            temperature = temperature or self.temperature
            max_tokens = max_tokens or self.max_tokens

            logger.debug(f"生成回答: prompt_length={len(prompt)}")

            # 构造消息
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            # 调用阿里百炼 API
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format="message",
                temperature=temperature,
                max_tokens=max_tokens,
            )

            if response.status_code != 200:
                error_msg = f"LLM 调用失败: {response.message}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            # 提取生成内容
            answer = response.output.choices[0].message.content

            logger.debug(f"成功生成回答: length={len(answer)}")
            return answer

        except Exception as e:
            logger.error(f"生成回答时发生错误: {str(e)}")
            raise

    async def agenerate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        异步生成回答（目前使用同步实现，后续可优化）

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            生成的文本
        """
        # TODO: 实现真正的异步调用
        return self.generate(prompt, system_prompt, temperature, max_tokens)


def get_llm_service() -> LLMService:
    """获取 LLM 服务实例"""
    return LLMService()
