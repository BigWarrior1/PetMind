"""
分割器模块
提供针对不同文档类型的语义感知分割策略
"""
from app.rag.splitters.base import SemanticTextSplitter
from app.rag.splitters.textbook import TextbookSplitter
from app.rag.splitters.qa import QASplitter
from app.rag.splitters.adaptive import AdaptiveTextSplitter

__all__ = [
    "SemanticTextSplitter",
    "TextbookSplitter",
    "QASplitter",
    "AdaptiveTextSplitter",
]
