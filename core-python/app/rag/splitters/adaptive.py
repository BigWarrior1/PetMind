"""
自适应分割器
根据文档类型自动选择最合适的分割策略
"""
from typing import List
from langchain_core.documents import Document

from app.rag.splitters.base import SemanticTextSplitter
from app.rag.splitters.textbook import TextbookSplitter
from app.rag.splitters.qa import QASplitter


class AdaptiveTextSplitter(SemanticTextSplitter):
    """
    自适应文本分割器

    根据文档 metadata 自动选择分割策略：
    - is_qa=True → QASplitter（整体保留问答对）
    - source_type 包含"教材"/"手册"/"指南" → TextbookSplitter（语义结构感知）
    - 其他 → TextbookSplitter（通用文档也用教材策略）
    """

    def __init__(
        self,
        max_tokens: int = 7000,
        overlap: int = 200,
        chunk_size_chars: int = 2000,
    ):
        """
        Args:
            max_tokens: 最大 token 数上限
            overlap: 块之间重叠字符数
            chunk_size_chars: 目标 chunk 字符数
        """
        super().__init__(max_tokens, overlap)
        self.chunk_size_chars = chunk_size_chars

        # 初始化各类分割器
        self.textbook_splitter = TextbookSplitter(
            max_tokens=max_tokens,
            overlap=overlap,
            chunk_size_chars=chunk_size_chars,
        )
        self.qa_splitter = QASplitter(max_tokens=max_tokens, overlap=overlap)

    def split_document(self, doc: Document) -> List[Document]:
        """根据文档类型选择分割策略"""
        metadata = doc.metadata

        # 判断文档类型
        is_qa = metadata.get("is_qa", False)
        source = metadata.get("source", "")
        source_type = metadata.get("source_type", "")

        # CSV 文件默认是 QA 类型
        if source.endswith(".csv"):
            is_qa = True

        # 判断是否为教材类文档
        is_textbook = any(
            keyword in source_type or keyword in source
            for keyword in ["教材", "手册", "指南", "教科书", "百科", "学术"]
        )

        # 根据类型选择分割器
        if is_qa:
            return self.qa_splitter.split_document(doc)
        elif is_textbook:
            return self.textbook_splitter.split_document(doc)
        else:
            # 默认使用教材分割器（对通用文档也有较好效果）
            return self.textbook_splitter.split_document(doc)

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        批量分割文档，自动选择策略

        返回分割统计信息
        """
        result = []
        stats = {"qa": 0, "textbook": 0, "other": 0, "total_input": len(documents)}

        for doc in documents:
            metadata = doc.metadata
            is_qa = metadata.get("is_qa", False) or metadata.get("source", "").endswith(".csv")
            source_type = metadata.get("source_type", "")
            is_textbook = any(
                k in source_type for k in ["教材", "手册", "指南", "教科书", "百科", "学术"]
            )

            if is_qa:
                stats["qa"] += 1
            elif is_textbook:
                stats["textbook"] += 1
            else:
                stats["other"] += 1

            chunks = self.split_document(doc)
            result.extend(chunks)

        # 打印统计
        total_output = len(result)
        print(f"\n  📊 分割统计:")
        print(f"     输入文档: {stats['total_input']} 个")
        print(f"     - 问答文档: {stats['qa']} 个")
        print(f"     - 教材文档: {stats['textbook']} 个")
        print(f"     - 其他文档: {stats['other']} 个")
        print(f"     输出 chunks: {total_output} 个")

        if total_output > 0:
            avg_len = sum(len(c.page_content) for c in result) / total_output
            max_len = max(len(c.page_content) for c in result)
            print(f"     平均长度: {avg_len:.0f} 字符")
            print(f"     最大长度: {max_len} 字符")

        return result
