"""
检索器
封装向量数据库的检索功能
"""

from typing import List, Optional

from langchain_core.documents import Document

from app.core.config import settings
from app.core.logging import logger
from app.rag.vectorstore import VectorStoreManager


class Retriever:
    """检索器"""

    def __init__(
        self,
        vectorstore: Optional[VectorStoreManager] = None,
        k: int = settings.retriever_k,
    ):
        """
        初始化检索器

        Args:
            vectorstore: 向量数据库管理器
            k: 返回结果数量
        """
        from app.rag.vectorstore import get_vectorstore

        self.vectorstore = vectorstore or get_vectorstore()
        self.k = k

        logger.info(f"初始化检索器: k={k}")

    def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        filter: Optional[dict] = None,
    ) -> List[Document]:
        """
        检索相关文档

        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件

        Returns:
            相关文档列表
        """
        k = k or self.k

        try:
            logger.info(f"检索相关文档: query={query[:50]}..., k={k}")

            documents = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter,
            )

            logger.info(f"检索到 {len(documents)} 个相关文档")
            return documents

        except Exception as e:
            logger.error(f"检索时发生错误: {str(e)}")
            raise

    def retrieve_with_scores(
        self,
        query: str,
        k: Optional[int] = None,
        filter: Optional[dict] = None,
    ) -> List[tuple[Document, float]]:
        """
        带相似度分数的检索

        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件

        Returns:
            (文档, 相似度分数) 列表
        """
        k = k or self.k

        try:
            logger.info(f"检索相关文档（带分数）: query={query[:50]}..., k={k}")

            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter,
            )

            logger.info(f"检索到 {len(results)} 个相关文档")
            return results

        except Exception as e:
            logger.error(f"检索时发生错误: {str(e)}")
            raise

    def format_documents(self, documents: List[Document]) -> str:
        """
        格式化文档为字符串

        Args:
            documents: 文档列表

        Returns:
            格式化后的文档内容
        """
        formatted_docs = []

        for i, doc in enumerate(documents, 1):
            content = doc.page_content
            source = doc.metadata.get("source", "未知来源")

            formatted_docs.append(f"【文档 {i}】\n来源: {source}\n内容: {content}\n")

        return "\n".join(formatted_docs)


def get_retriever() -> Retriever:
    """获取检索器实例"""
    return Retriever()
