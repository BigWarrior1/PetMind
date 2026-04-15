"""
问答分割器
针对 CSV 问答数据优化，整体保留 Q&A 对，超限时按句子分割
"""
import re
from typing import List, Tuple
from langchain_core.documents import Document

from app.rag.splitters.base import SemanticTextSplitter


class QASplitter(SemanticTextSplitter):
    """
    问答分割器

    分割策略：
    1. 整体保留 Q&A pair（问 + 答）
    2. 如果单个 Q&A 超限，按句子分割
    3. 分割时保持问和答的完整性
    """

    def __init__(self, max_tokens: int = None, overlap: int = 0):
        """
        Args:
            max_tokens: 最大 token 数上限
            overlap: 重叠字符数（Q&A 场景默认 0）
        """
        super().__init__(max_tokens, overlap)

    def split_document(self, doc: Document) -> List[Document]:
        """
        分割问答文档

        支持格式：
        - "问：xxx\n答：xxx"
        - "Q: xxx\nA: xxx"
        - "问题: xxx\n答案: xxx"
        """
        text = doc.page_content
        metadata = doc.metadata.copy()

        # 尝试提取问答对
        qa_pairs = self._extract_qa_pairs(text)

        if not qa_pairs:
            # 无法识别格式，整体作为一个 chunk
            return [doc]

        chunks = []
        for question, answer in qa_pairs:
            qa_content = f"问：{question}\n答：{answer}"
            tokens = self.estimate_tokens(qa_content)

            if tokens <= self.max_tokens:
                # 大小合适，整体保留
                chunk_meta = metadata.copy()
                chunk_meta["question"] = question[:100]  # 保存问题摘要
                chunks.append(Document(page_content=qa_content, metadata=chunk_meta))
            else:
                # 超限时，按句子分割 Q 或 A
                sub_chunks = self._split_large_qa(question, answer, metadata)
                chunks.extend(sub_chunks)

        if not chunks:
            return [doc]

        return chunks

    def _extract_qa_pairs(self, text: str) -> List[Tuple[str, str]]:
        """
        从文本中提取问答对

        Returns:
            [(问题, 回答), ...]
        """
        qa_pairs = []

        # 问答分隔符组合
        separators = [
            ("问", "答"),
            ("Q", "A"),
            ("问题", "答案"),
            ("question", "answer"),
        ]

        for q_sep, a_sep in separators:
            pairs = self._extract_by_separators(text, q_sep, a_sep)
            if pairs:
                return pairs

        return qa_pairs

    def _extract_by_separators(
        self, text: str, q_mark: str, a_mark: str
    ) -> List[Tuple[str, str]]:
        """使用指定分隔符提取问答对"""
        pairs = []

        # 尝试找到所有问和答的位置
        q_pattern = rf"{q_mark}[：:]\s*(.+?)(?=\n{a_mark}[：:]|$)"
        a_pattern = rf"{a_mark}[：:]\s*(.+?)(?=\n{q_mark}[：:]|$)"

        # 简化处理：按换行分割，每段包含问和答
        lines = text.split("\n")
        current_q = None
        current_a = []
        in_answer = False

        q_prefixes = [f"{q_mark}：", f"{q_mark}:", f"【{q_mark}】", f"{q_mark} "]
        a_prefixes = [f"{a_mark}：", f"{a_mark}:", f"【{a_mark}】", f"{a_mark} "]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测问题行
            is_question = any(line.startswith(p) for p in q_prefixes)
            is_answer = any(line.startswith(p) for p in a_prefixes)

            if is_question:
                # 保存上一个问答对
                if current_q is not None:
                    answer_text = "\n".join(current_a).strip()
                    if answer_text:
                        pairs.append((current_q, answer_text))

                # 提取问题内容
                for prefix in q_prefixes:
                    if line.startswith(prefix):
                        current_q = line[len(prefix) :].strip()
                        break

                current_a = []
                in_answer = True
            elif is_answer and in_answer:
                # 提取回答内容
                for prefix in a_prefixes:
                    if line.startswith(prefix):
                        current_a.append(line[len(prefix) :].strip())
                        break
            elif in_answer and current_a:
                # 继续上一条回答（多行回答）
                current_a.append(line)

        # 保存最后一个问答对
        if current_q is not None:
            answer_text = "\n".join(current_a).strip()
            if answer_text:
                pairs.append((current_q, answer_text))

        return pairs

    def _split_large_qa(
        self, question: str, answer: str, metadata: dict
    ) -> List[Document]:
        """
        分割过大的问答对（按句子）

        优先保持问题和回答各自的完整性
        """
        chunks = []

        # 检查问题是否超限
        q_tokens = self.estimate_tokens(question)
        a_tokens = self.estimate_tokens(answer)

        if q_tokens > self.max_tokens:
            # 问题本身超限，按句子分割问题
            q_chunks = self._split_text_by_sentences(question)
            for i, q_chunk in enumerate(q_chunks):
                chunk_meta = metadata.copy()
                chunk_meta["question"] = f"[问题片段{i+1}] {q_chunk[:50]}..."
                chunk_meta["is_partial_question"] = True
                content = f"问：{q_chunk}\n答：{answer}"
                chunks.append(Document(page_content=content, metadata=chunk_meta))
        else:
            # 问题和回答组合超限，只分割回答
            a_chunks = self._split_text_by_sentences(answer)
            for i, a_chunk in enumerate(a_chunks):
                chunk_meta = metadata.copy()
                chunk_meta["question"] = question[:100]
                content = f"问：{question}\n答：{a_chunk}"
                chunks.append(Document(page_content=content, metadata=chunk_meta))

        return chunks if chunks else [Document(page_content=f"问：{question}\n答：{answer}", metadata=metadata)]

    def _split_text_by_sentences(self, text: str) -> List[str]:
        """按句子分割文本"""
        separators = ["。", "！", "？", "；"]
        parts = [text]

        for sep in separators:
            new_parts = []
            for part in parts:
                if self.estimate_tokens(part) <= self.max_tokens:
                    new_parts.append(part)
                else:
                    new_parts.extend([s.strip() for s in part.split(sep) if s.strip()])
            parts = new_parts

        return [p for p in parts if p.strip()]
