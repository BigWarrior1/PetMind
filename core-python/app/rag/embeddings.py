"""
嵌入模型封装
使用阿里百炼 text-embedding-v3 模型
"""

from typing import List

import dashscope
from langchain_core.embeddings import Embeddings

from app.core.config import settings
from app.core.logging import logger


class DashScopeEmbeddings(Embeddings):
    """阿里百炼嵌入模型封装"""

    def __init__(
        self,
        model: str = settings.embedding_model,
        api_key: str = settings.dashscope_api_key,
    ):
        """
        初始化嵌入模型

        Args:
            model: 模型名称，默认为 text-embedding-v3
            api_key: API 密钥
        """
        self.model = model
        dashscope.api_key = api_key
        logger.info(f"初始化 DashScope 嵌入模型: {model}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量嵌入文档

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表
        """
        try:
            logger.debug(f"嵌入 {len(texts)} 个文档")

            # 阿里百炼 API 限制每次最多 10 个文本，需要分批处理
            batch_size = 10
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i : i + batch_size]
                logger.debug(f"处理批次 {i // batch_size + 1}, 包含 {len(batch)} 个文档")

                # 调用阿里百炼 API
                response = dashscope.TextEmbedding.call(
                    model=self.model,
                    input=batch,
                )

                if response.status_code != 200:
                    error_msg = f"嵌入失败: {response.message}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)

                # 提取嵌入向量
                embeddings = [item["embedding"] for item in response.output["embeddings"]]
                all_embeddings.extend(embeddings)

            logger.debug(f"成功嵌入 {len(all_embeddings)} 个文档")

            return all_embeddings

            return embeddings

        except Exception as e:
            logger.error(f"嵌入文档时发生错误: {str(e)}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """
        嵌入单个查询文本

        Args:
            text: 查询文本

        Returns:
            嵌入向量
        """
        try:
            logger.debug(f"嵌入查询: {text[:50]}...")

            # 调用阿里百炼 API
            response = dashscope.TextEmbedding.call(
                model=self.model,
                input=text,
            )

            if response.status_code != 200:
                error_msg = f"嵌入失败: {response.message}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            # 提取嵌入向量
            embedding = response.output["embeddings"][0]["embedding"]
            logger.debug("成功嵌入查询")

            return embedding

        except Exception as e:
            logger.error(f"嵌入查询时发生错误: {str(e)}")
            raise


def get_embeddings() -> DashScopeEmbeddings:
    """获取嵌入模型实例"""
    return DashScopeEmbeddings()
