"""
检索器
封装 RAG 检索逻辑
"""
from typing import List, Optional
from langchain_core.documents import Document

from app.core.config import RAG_TOP_K, RAG_SCORE_THRESHOLD
from app.rag.vectorstore import get_vectorstore_manager


class RAGRetriever:
    """RAG 检索器"""

    def __init__(
        self,
        top_k: int = RAG_TOP_K,
        score_threshold: float = RAG_SCORE_THRESHOLD,
    ):
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.vectorstore_manager = get_vectorstore_manager()

    def retrieve(self, query: str, filter: Optional[dict] = None) -> List[Document]:
        """
        检索相关文档

        Args:
            query: 查询文本
            filter: 元数据过滤条件

        Returns:
            相关文档列表
        """
        results = self.vectorstore_manager.similarity_search_with_score(
            query=query,
            k=self.top_k,
            filter=filter,
        )

        # 过滤低分结果
        filtered = [
            (doc, score) for doc, score in results if score <= self.score_threshold
        ]

        return [doc for doc, _ in filtered]

    def retrieve_with_sources(self, query: str, filter: Optional[dict] = None) -> tuple:
        """
        检索并返回来源信息

        Returns:
            (documents, sources) 元组
        """
        results = self.vectorstore_manager.similarity_search_with_score(
            query=query,
            k=self.top_k,
            filter=filter,
        )

        filtered = [
            (doc, score) for doc, score in results if score <= self.score_threshold
        ]

        documents = [doc for doc, _ in filtered]
        sources = [
            {
                "content": doc.page_content[:100] + "...",
                "source": doc.metadata.get("source", "unknown"),
                "score": score,
            }
            for doc, score in filtered
        ]

        return documents, sources
