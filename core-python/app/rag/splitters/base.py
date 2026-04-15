"""
分割器基类
定义语义感知分割器的接口
"""
from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document


class SemanticTextSplitter(ABC):
    """
    语义感知分割器基类

    子类实现按文档类型定制分割策略：
    - 教材：按章节段落
    - 问答：整体保留
    - 通用：自适应
    """

    # Embedding 模型安全上限（text-embedding-v3 = 8192 tokens，留 10% buffer）
    MAX_TOKENS = 7000

    # 重叠字符数（用于保持上下文连续性）
    DEFAULT_OVERLAP = 200

    def __init__(self, max_tokens: int = None, overlap: int = None):
        """
        Args:
            max_tokens: 最大 token 数上限，默认 7000（安全线）
            overlap: 块之间重叠字符数，默认 200
        """
        self.max_tokens = max_tokens or self.MAX_TOKENS
        self.overlap = overlap if overlap is not None else self.DEFAULT_OVERLAP

    @abstractmethod
    def split_document(self, doc: Document) -> List[Document]:
        """
        分割单个文档

        Args:
            doc: 原始文档

        Returns:
            分割后的文档列表
        """
        pass

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        批量分割文档

        Args:
            documents: 原始文档列表

        Returns:
            分割后的文档列表
        """
        result = []
        for doc in documents:
            chunks = self.split_document(doc)
            result.extend(chunks)
        return result

    def estimate_tokens(self, text: str) -> int:
        """
        估算文本 token 数（中文字符约 1.5 tokens，英文约 4 字符/token）

        Args:
            text: 输入文本

        Returns:
            估算的 token 数
        """
        # 简化估算：中文按 1.5 token/字符，英文/数字按 4 字符/token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return int(chinese_chars * 1.5 + other_chars / 4)

    def split_by_sentences(self, text: str, separators: str = None) -> List[str]:
        """
        按句子分割（中文优先）

        Args:
            text: 输入文本
            separators: 分隔符列表，按优先级排序

        Returns:
            句子列表
        """
        if separators is None:
            separators = ["。", "！", "？", "；", "\n"]

        parts = [text]
        for sep in separators:
            new_parts = []
            for part in parts:
                if self.estimate_tokens(part) <= self.max_tokens:
                    new_parts.append(part)
                else:
                    new_parts.extend(part.split(sep))
            parts = new_parts

        # 过滤空字符串
        return [p.strip() for p in parts if p.strip()]

    def split_with_overlap(
        self, text: str, max_chars: int, overlap: int = None
    ) -> List[str]:
        """
        带重叠的分段（当文本超限时 fallback）

        Args:
            text: 输入文本
            max_chars: 最大字符数
            overlap: 重叠字符数

        Returns:
            分段列表
        """
        overlap = overlap or self.overlap
        if len(text) <= max_chars:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + max_chars
            if start > 0:
                start = start - overlap  # 向前重叠
            chunk = text[start:end]
            chunks.append(chunk)
            start = end

        return chunks
