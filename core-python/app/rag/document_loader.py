"""
文档加载器
负责加载各类兽医知识文档 (PDF, TXT, DOCX)

使用 LangChain 的 DocumentLoader 统一接口
"""
from pathlib import Path
from typing import List, Union
from langchain_core.documents import Document


class DocumentLoader:
    """文档加载器基类"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load(self) -> List[Document]:
        """加载文档，返回 Document 列表"""
        raise NotImplementedError

    def get_metadata(self) -> dict:
        """获取文档元数据"""
        return {
            "source": self.file_path.name,
            "file_path": str(self.file_path),
        }


class PDFLoader(DocumentLoader):
    """PDF 文档加载"""

    def load(self) -> List[Document]:
        """加载 PDF 文档"""
        try:
            from langchain_community.document_loaders import PyPDFLoader
        except ImportError:
            raise ImportError("请安装 PyPDFLoader: pip install pypdf")

        loader = PyPDFLoader(str(self.file_path))
        documents = loader.load()

        # 添加元数据
        for doc in documents:
            doc.metadata.update(self.get_metadata())

        return documents


class TXTLoader(DocumentLoader):
    """TXT 文档加载"""

    def load(self) -> List[Document]:
        """加载 TXT 文档"""
        try:
            from langchain_community.document_loaders import TextLoader
        except ImportError:
            raise ImportError("请安装 TextLoader: pip install langchain-community")

        loader = TextLoader(str(self.file_path), encoding="utf-8")
        documents = loader.load()

        # 添加元数据
        for doc in documents:
            doc.metadata.update(self.get_metadata())

        return documents


class DOCXLoader(DocumentLoader):
    """DOCX 文档加载"""

    def load(self) -> List[Document]:
        """加载 DOCX 文档"""
        try:
            from langchain_community.document_loaders import UnstructuredWordDocumentLoader
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")

        loader = UnstructuredWordDocumentLoader(str(self.file_path))
        documents = loader.load()

        # 添加元数据
        for doc in documents:
            doc.metadata.update(self.get_metadata())

        return documents


def get_loader(file_path: str) -> DocumentLoader:
    """
    根据文件扩展名获取对应的加载器

    Args:
        file_path: 文件路径

    Returns:
        对应的 DocumentLoader 实例

    Raises:
        ValueError: 不支持的文件类型
    """
    suffix = Path(file_path).suffix.lower()

    loaders = {
        ".pdf": PDFLoader,
        ".txt": TXTLoader,
        ".docx": DOCXLoader,
    }

    if suffix not in loaders:
        raise ValueError(f"不支持的文件类型: {suffix}，支持的类型: {list(loaders.keys())}")

    return loaders[suffix](file_path)


def load_document(file_path: str) -> List[Document]:
    """
    加载单个文档

    Args:
        file_path: 文件路径

    Returns:
        Document 列表
    """
    loader = get_loader(file_path)
    return loader.load()


def load_documents_from_directory(directory: str, extensions: List[str] = None) -> List[Document]:
    """
    从目录加载所有支持的文档

    Args:
        directory: 目录路径
        extensions: 要加载的文件扩展名列表，如 [".pdf", ".txt", ".docx"]

    Returns:
        所有文档的 Document 列表
    """
    if extensions is None:
        extensions = [".pdf", ".txt", ".docx"]

    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"目录不存在: {directory}")

    all_documents = []

    for ext in extensions:
        for file_path in dir_path.glob(f"**/*{ext}"):
            if file_path.is_file():
                try:
                    documents = load_document(str(file_path))
                    all_documents.extend(documents)
                    print(f"  ✅ 加载成功: {file_path.name} ({len(documents)} 页/段)")
                except Exception as e:
                    print(f"  ❌ 加载失败: {file_path.name}, 错误: {e}")

    return all_documents
