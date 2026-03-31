"""
文本分割器
将长文档分割成适合检索的小片段
"""
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import EMBEDDING_MODEL


# 根据 embedding 模型的最大输入长度设置 chunk_size
# bge-large-zh-v1.5 最大输入为 512 tokens
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50


def get_text_splitter(
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> RecursiveCharacterTextSplitter:
    """
    获取文本分割器

    使用 RecursiveCharacterTextSplitter，按段落分割
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],
    )


def split_documents(documents: List, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> List:
    """分割文档列表"""
    splitter = get_text_splitter(chunk_size, chunk_overlap)
    return splitter.split_documents(documents)
