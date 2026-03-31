"""
检索器
封装 RAG 检索逻辑

综合考虑语义相似度和来源置信度
"""
from typing import List, Optional
from langchain_core.documents import Document

from app.core.config import RAG_TOP_K, RAG_SCORE_THRESHOLD
from app.rag.vectorstore import get_vectorstore_manager

# 置信度权重配置
CONFIDENCE_WEIGHT = 0.3  # 置信度占总评分的权重
SEMANTIC_WEIGHT = 0.7    # 语义相似度占总评分的权重


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

    def _calculate_combined_score(self, semantic_score: float, confidence: float) -> float:
        """
        计算综合评分

        Args:
            semantic_score: 语义相似度分数 (0-1, Chroma的距离转成相似度)
            confidence: 来源置信度 (0-1)

        Returns:
            综合评分 (0-1)
        """
        # Chroma 返回的是距离（越小越好），转成相似度
        # 距离 0 -> 相似度 1, 距离 1 -> 相似度 0
        semantic_similarity = 1 - semantic_score

        # 综合评分 = 语义相似度 * 权重 + 置信度 * 权重
        combined = (
            semantic_similarity * SEMANTIC_WEIGHT +
            confidence * CONFIDENCE_WEIGHT
        )
        return combined

    def retrieve(self, query: str, filter: Optional[dict] = None) -> List[Document]:
        """
        检索相关文档（按综合评分排序）

        Args:
            query: 查询文本
            filter: 元数据过滤条件

        Returns:
            相关文档列表
        """
        results = self.vectorstore_manager.similarity_search_with_score(
            query=query,
            k=self.top_k * 2,  # 多检索一些，后面按综合评分筛选
            filter=filter,
        )

        # 计算综合评分并排序
        scored_results = []
        for doc, distance in results:
            confidence = doc.metadata.get("confidence", 0.5)
            combined_score = self._calculate_combined_score(distance, confidence)
            scored_results.append((doc, combined_score, confidence))

        # 按综合评分排序，取 Top-K
        scored_results.sort(key=lambda x: x[1], reverse=True)
        top_results = scored_results[:self.top_k]

        # 过滤低于阈值的
        filtered = [
            (doc, score, conf) for doc, score, conf in top_results
            if score >= self.score_threshold
        ]

        return [doc for doc, _, _ in filtered]

    def retrieve_with_sources(self, query: str, filter: Optional[dict] = None) -> tuple:
        """
        检索并返回来源信息

        Returns:
            (documents, sources) 元组
        """
        results = self.vectorstore_manager.similarity_search_with_score(
            query=query,
            k=self.top_k * 2,
            filter=filter,
        )

        # 计算综合评分
        scored_results = []
        for doc, distance in results:
            confidence = doc.metadata.get("confidence", 0.5)
            combined_score = self._calculate_combined_score(distance, confidence)
            scored_results.append((doc, distance, combined_score, confidence))

        # 按综合评分排序
        scored_results.sort(key=lambda x: x[2], reverse=True)
        top_results = scored_results[:self.top_k]

        # 过滤低于阈值
        filtered = [
            (doc, dist, score, conf)
            for doc, dist, score, conf in top_results
            if score >= self.score_threshold
        ]

        documents = [doc for doc, _, _, _ in filtered]
        sources = [
            {
                "content": doc.page_content[:100] + "...",
                "source": doc.metadata.get("source", "unknown"),
                "source_type": doc.metadata.get("source_type", "通用文档"),
                "confidence": conf,
                "semantic_score": 1 - dist,  # 转成相似度
                "combined_score": score,
            }
            for doc, dist, score, conf in filtered
        ]

        return documents, sources
