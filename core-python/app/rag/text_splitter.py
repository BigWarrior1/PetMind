"""
文本切分器
将文档切分为适合嵌入的块
"""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.core.config import settings
from app.core.logging import logger


class TextSplitter:
    """文本切分器"""

    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ):
        """
        初始化文本切分器

        Args:
            chunk_size: 块大小
            chunk_overlap: 块重叠大小
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " ", ""],
        )

        logger.info(
            f"初始化文本切分器: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        切分文档列表

        Args:
            documents: 原始文档列表

        Returns:
            切分后的文档列表
        """
        try:
            logger.info(f"开始切分 {len(documents)} 个文档")

            split_docs = self.splitter.split_documents(documents)

            logger.info(f"切分完成，生成 {len(split_docs)} 个文档块")
            return split_docs

        except Exception as e:
            logger.error(f"切分文档时发生错误: {str(e)}")
            raise

    def split_text(self, text: str) -> List[str]:
        """
        切分文本

        Args:
            text: 原始文本

        Returns:
            切分后的文本列表
        """
        try:
            logger.debug(f"切分文本，长度: {len(text)}")

            chunks = self.splitter.split_text(text)

            logger.debug(f"切分完成，生成 {len(chunks)} 个文本块")
            return chunks

        except Exception as e:
            logger.error(f"切分文本时发生错误: {str(e)}")
            raise


def get_text_splitter() -> TextSplitter:
    """获取文本切分器实例"""
    return TextSplitter()
