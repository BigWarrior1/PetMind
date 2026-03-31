"""
向量数据库封装
使用 Chroma 向量库
"""
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME
from app.rag.embeddings import get_embeddings


class VectorStoreManager:
    """向量库管理器"""

    def __init__(self):
        self.embeddings = get_embeddings()
        self._vectorstore: Optional[Chroma] = None

    def get_vectorstore(self) -> Chroma:
        """获取或创建向量库实例"""
        if self._vectorstore is None:
            self._vectorstore = Chroma(
                persist_directory=CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings,
                collection_name=CHROMA_COLLECTION_NAME,
            )
        return self._vectorstore

    def add_documents(self, documents: List[Document]) -> None:
        """添加文档到向量库"""
        vectorstore = self.get_vectorstore()
        vectorstore.add_documents(documents)
        # Chroma 0.4.x 自动持久化，无需手动调用 persist()

    def similarity_search(
        self, query: str, k: int = 5, filter: Optional[dict] = None
    ) -> List[Document]:
        """相似度搜索"""
        vectorstore = self.get_vectorstore()
        return vectorstore.similarity_search(query, k=k, filter=filter)

    def similarity_search_with_score(
        self, query: str, k: int = 5, filter: Optional[dict] = None
    ) -> List[tuple]:
        """相似度搜索（带分数）"""
        vectorstore = self.get_vectorstore()
        return vectorstore.similarity_search_with_score(query, k=k, filter=filter)

    def delete_collection(self) -> None:
        """删除向量库集合"""
        vectorstore = self.get_vectorstore()
        vectorstore.delete_collection()
        self._vectorstore = None


# 全局单例
_vectorstore_manager: Optional[VectorStoreManager] = None


def get_vectorstore_manager() -> VectorStoreManager:
    """获取全局向量库管理器"""
    global _vectorstore_manager
    if _vectorstore_manager is None:
        _vectorstore_manager = VectorStoreManager()
    return _vectorstore_manager
