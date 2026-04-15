"""
文本分割器
将长文档分割成适合检索的小片段

使用自适应分割策略，根据文档类型自动选择最佳分割方式：
- 教材/手册：按章节结构分割
- 问答数据：整体保留
- 其他文档：语义段落分割
"""
from typing import List
from langchain_core.documents import Document

from app.rag.splitters import AdaptiveTextSplitter


# 向后兼容的配置（保持原有接口）
DEFAULT_CHUNK_SIZE = 3000  # 字符数（提升自旧的 500，教材内容连贯适合大chunk）
DEFAULT_CHUNK_OVERLAP = 200


def get_text_splitter(
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> AdaptiveTextSplitter:
    """
    获取文本分割器

    使用 AdaptiveTextSplitter，根据文档类型自动选择策略
    """
    return AdaptiveTextSplitter(
        max_tokens=7000,  # text-embedding-v3 安全上限
        overlap=chunk_overlap,
        chunk_size_chars=chunk_size,
    )


def split_documents(
    documents: List[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[Document]:
    """
    分割文档列表

    使用自适应分割策略，自动识别：
    - 问答数据（CSV）：整体保留 Q&A 对
    - 教材文档：按章节结构分割
    - 其他文档：语义段落分割

    Args:
        documents: 原始文档列表
        chunk_size: 目标 chunk 字符数（默认 2000）
        chunk_overlap: 块之间重叠字符数（默认 200）

    Returns:
        分割后的文档列表
    """
    splitter = AdaptiveTextSplitter(
        max_tokens=7000,
        overlap=chunk_overlap,
        chunk_size_chars=chunk_size,
    )
    return splitter.split_documents(documents)
