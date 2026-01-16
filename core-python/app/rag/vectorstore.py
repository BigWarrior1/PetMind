"""
向量数据库管理
使用 Chroma 进行向量存储和检索
"""

from pathlib import Path
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import settings
from app.core.logging import logger
from app.rag.embeddings import get_embeddings


class VectorStoreManager:
    """向量数据库管理器"""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        """
        初始化向量数据库管理器

        Args:
            persist_directory: 持久化目录
            collection_name: 集合名称
        """
        self.persist_directory = persist_directory or settings.chroma_persist_dir
        self.collection_name = collection_name or settings.chroma_collection_name
        self.embeddings = get_embeddings()
        self._vectorstore: Optional[Chroma] = None

        # 确保持久化目录存在
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        logger.info(
            f"初始化向量数据库管理器: collection={self.collection_name}, "
            f"persist_dir={self.persist_directory}"
        )

    @property
    def vectorstore(self) -> Chroma:
        """获取向量数据库实例（懒加载）"""
        if self._vectorstore is None:
            self._vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
            logger.info("向量数据库实例已创建")

        return self._vectorstore

    def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100,
    ) -> List[str]:
        """
        批量添加文档到向量库

        Args:
            documents: 文档列表
            batch_size: 批处理大小

        Returns:
            文档 ID 列表
        """
        try:
            logger.info(f"开始添加 {len(documents)} 个文档到向量库")

            # 分批处理
            all_ids = []
            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]
                ids = self.vectorstore.add_documents(batch)
                all_ids.extend(ids)
                logger.debug(f"已处理 {i + len(batch)}/{len(documents)} 个文档")

            logger.info(f"成功添加 {len(all_ids)} 个文档")
            return all_ids

        except Exception as e:
            logger.error(f"添加文档时发生错误: {str(e)}")
            raise

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None,
    ) -> List[Document]:
        """
        相似度搜索

        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件

        Returns:
            相关文档列表
        """
        try:
            logger.debug(f"执行相似度搜索: query={query[:50]}..., k={k}")

            results = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter,
            )

            logger.debug(f"搜索到 {len(results)} 个相关文档")
            return results

        except Exception as e:
            logger.error(f"相似度搜索时发生错误: {str(e)}")
            raise

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None,
    ) -> List[tuple[Document, float]]:
        """
        带相似度分数的搜索

        Args:
            query: 查询文本
            k: 返回结果数量
            filter: 元数据过滤条件

        Returns:
            (文档, 相似度分数) 列表
        """
        try:
            logger.debug(f"执行带分数的相似度搜索: query={query[:50]}..., k={k}")

            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter,
            )

            logger.debug(f"搜索到 {len(results)} 个相关文档")
            return results

        except Exception as e:
            logger.error(f"相似度搜索时发生错误: {str(e)}")
            raise

    def delete_collection(self) -> None:
        """删除集合"""
        try:
            logger.warning(f"删除集合: {self.collection_name}")
            self.vectorstore.delete_collection()
            self._vectorstore = None
            logger.info("集合已删除")

        except Exception as e:
            logger.error(f"删除集合时发生错误: {str(e)}")
            raise

    def get_collection_count(self) -> int:
        """获取集合中的文档数量"""
        try:
            count = self.vectorstore._collection.count()
            logger.debug(f"集合中有 {count} 个文档")
            return count

        except Exception as e:
            logger.error(f"获取文档数量时发生错误: {str(e)}")
            return 0


def get_vectorstore() -> VectorStoreManager:
    """获取向量数据库管理器实例"""
    return VectorStoreManager()
