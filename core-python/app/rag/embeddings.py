"""
Embedding 模型封装
使用阿里 DashScope text-embedding-v3 API

包含修复版的 DashScope Embeddings，解决 dashscope 库在 HTTP 错误处理时的 bug：
- 当 API 返回非 200 状态码时，HTTPError 尝试访问 response.request
- 但 dashscope 的 resp 对象没有 request 属性，导致 KeyError
"""
import logging
from typing import List
from langchain_community.embeddings import DashScopeEmbeddings
from app.core.config import DASHSCOPE_API_KEY, EMBEDDING_MODEL

logger = logging.getLogger(__name__)


def get_embedding_model():
    """
    获取 Embedding 模型

    使用阿里 text-embedding-v3，费用低（0.0007元/千tokens），中文效果好
    支持通过 EMBEDDING_MODEL 环境变量切换模型
    """
    return DashScopeEmbeddings(
        model=EMBEDDING_MODEL,
        dashscope_api_key=DASHSCOPE_API_KEY,
    )


class PatchedDashScopeEmbeddings(DashScopeEmbeddings):
    """
    修复版的 DashScope Embeddings

    修复 dashscope 库在 HTTP 错误处理时的 bug：
    - 当 API 返回非 200 状态码时，HTTPError 尝试访问 response.request
    - 但 dashscope 的 resp 对象没有 request 属性，导致 KeyError
    """

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """重写 embed_documents，修复错误处理"""
        from tenacity import retry, stop_after_attempt, wait_exponential

        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=10))
        def _embed_with_retry():
            try:
                return self._embed_documents_impl(texts)
            except Exception as e:
                # 捕获 KeyError 并重试
                if "KeyError" in str(type(e).__name__) or "'request'" in str(e):
                    logger.warning(f"DashScope API 返回错误，尝试重试: {e}")
                    raise
                raise

        return _embed_with_retry()

    def _embed_documents_impl(self, texts: List[str]) -> List[List[float]]:
        """实际的 embed_documents 实现"""
        embeddings = []
        batch_size = 8  # text-embedding-v3 每批不超过 10
        total_batches = (len(texts) + batch_size - 1) // batch_size

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_no = i // batch_size + 1
            print(f"  Embedding 进度: {batch_no}/{total_batches} ({batch_no*100//total_batches}%)", end="\r", flush=True)
            result = self.client.call(
                model=self.model,
                input=batch,
                text_type="document"
            )

            if result.status_code == 200:
                # 成功
                embeddings.extend([item["embedding"] for item in result.output["embeddings"]])
            else:
                # 批次失败，抛出错误
                error_msg = (
                    f"DashScope API 批次 {i//batch_size + 1} 返回错误: "
                    f"status_code={result.status_code}, "
                    f"code={getattr(result, 'code', 'N/A')}, "
                    f"message={getattr(result, 'message', 'N/A')}"
                )
                logger.error(error_msg)
                raise Exception(error_msg)

        print()  # 换行
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """重写 embed_query"""
        try:
            return self._embed_query_impl(text)
        except Exception as e:
            if "KeyError" in str(type(e).__name__) or "'request'" in str(e):
                logger.warning(f"DashScope embed_query 错误: {e}")
                raise
            raise

    def _embed_query_impl(self, text: str) -> List[float]:
        """实际的 embed_query 实现"""
        result = self.client.call(
            model=self.model,
            input=text,
            text_type="query"
        )

        if result.status_code == 200:
            return result.output["embeddings"][0]["embedding"]
        else:
            logger.warning(
                f"DashScope embed_query 返回错误: "
                f"status_code={result.status_code}"
            )
            # 返回零向量作为降级方案
            return [0.0] * 1024  # text-embedding-v3 输出 1024 维


# 全局单例
_embedding_model = None


def get_embeddings():
    """获取全局 Embedding 实例（使用修复版）"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = PatchedDashScopeEmbeddings(
            model=EMBEDDING_MODEL,
            dashscope_api_key=DASHSCOPE_API_KEY,
        )
    return _embedding_model
