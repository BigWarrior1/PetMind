"""
文档加载器
支持加载多种格式的文档
"""

from pathlib import Path
from typing import List, Union

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document

from app.core.logging import logger


class DocumentLoader:
    """文档加载器"""

    @staticmethod
    def load_text(file_path: Union[str, Path]) -> List[Document]:
        """
        加载文本文件

        Args:
            file_path: 文件路径

        Returns:
            文档列表
        """
        try:
            logger.info(f"加载文本文件: {file_path}")
            loader = TextLoader(str(file_path), encoding="utf-8")
            documents = loader.load()
            logger.info(f"成功加载 {len(documents)} 个文档")
            return documents

        except Exception as e:
            logger.error(f"加载文本文件失败: {str(e)}")
            raise

    @staticmethod
    def load_pdf(file_path: Union[str, Path]) -> List[Document]:
        """
        加载 PDF 文件

        Args:
            file_path: 文件路径

        Returns:
            文档列表
        """
        try:
            logger.info(f"加载 PDF 文件: {file_path}")
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
            logger.info(f"成功加载 {len(documents)} 个文档")
            return documents

        except Exception as e:
            logger.error(f"加载 PDF 文件失败: {str(e)}")
            raise

    @staticmethod
    def load_markdown(file_path: Union[str, Path]) -> List[Document]:
        """
        加载 Markdown 文件

        Args:
            file_path: 文件路径

        Returns:
            文档列表
        """
        try:
            logger.info(f"加载 Markdown 文件: {file_path}")
            loader = UnstructuredMarkdownLoader(str(file_path))
            documents = loader.load()
            logger.info(f"成功加载 {len(documents)} 个文档")
            return documents

        except Exception as e:
            logger.error(f"加载 Markdown 文件失败: {str(e)}")
            raise

    @staticmethod
    def load_directory(
        directory_path: Union[str, Path],
        glob_pattern: str = "**/*.txt",
        show_progress: bool = True,
    ) -> List[Document]:
        """
        加载目录中的所有文档

        Args:
            directory_path: 目录路径
            glob_pattern: 文件匹配模式
            show_progress: 是否显示进度

        Returns:
            文档列表
        """
        try:
            logger.info(f"加载目录: {directory_path}, pattern={glob_pattern}")

            loader = DirectoryLoader(
                str(directory_path),
                glob=glob_pattern,
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"},
                show_progress=show_progress,
            )

            documents = loader.load()
            logger.info(f"成功从目录加载 {len(documents)} 个文档")
            return documents

        except Exception as e:
            logger.error(f"加载目录失败: {str(e)}")
            raise

    @staticmethod
    def load_file(file_path: Union[str, Path]) -> List[Document]:
        """
        根据文件扩展名自动选择加载器

        Args:
            file_path: 文件路径

        Returns:
            文档列表
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        if suffix == ".txt":
            return DocumentLoader.load_text(file_path)
        elif suffix == ".pdf":
            return DocumentLoader.load_pdf(file_path)
        elif suffix in [".md", ".markdown"]:
            return DocumentLoader.load_markdown(file_path)
        else:
            logger.warning(f"未知文件类型 {suffix}，尝试作为文本加载")
            return DocumentLoader.load_text(file_path)
