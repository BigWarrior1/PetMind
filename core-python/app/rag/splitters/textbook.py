"""
教材分割器
针对兽医教科书优化，识别章节结构，按语义边界分割
"""
import re
from typing import List, Tuple
from langchain_core.documents import Document

from app.rag.splitters.base import SemanticTextSplitter


# 教材章节标题正则模式（按优先级排序）
CHAPTER_PATTERNS = [
    # 第X章、第X节、第X篇、第X部
    (r"^第[一二三四五六七八九十百千\d]+[章节篇部]", "chapter"),
    # 【标题】格式（病因、症状、治疗等小节）
    (r"^【([^】]+)》", "section"),
    # A. B. C. 大写字母序号
    (r"^[A-Z][\.\)】]", "alpha"),
    # 1.2.3 数字序号
    (r"^\d+\.\d+", "numeral"),
    # （一）（二）（三）括号中文序号
    (r"^[\（\(][^）\)]+[\）\)][\.\、\，]", "cn_paren"),
    # 1、2、3、 中文明数字序号
    (r"^[一二三四五六七八九十百千\d+][、\.、，]", "cn_numeral"),
]


def detect_chapter_heading(line: str) -> Tuple[bool, str, str]:
    """
    检测行是否为章节标题

    Returns:
        (是否标题, 标题类型, 标题内容)
    """
    line = line.strip()
    if not line or len(line) > 100:  # 标题不会太长
        return False, "", ""

    for pattern, heading_type in CHAPTER_PATTERNS:
        if re.match(pattern, line):
            return True, heading_type, line
    return False, "", ""


def split_by_chapters(text: str) -> List[Tuple[str, str]]:
    """
    按章节分割文本

    Returns:
        [(章节标题, 章节内容), ...]
    """
    lines = text.split("\n")
    chapters = []
    current_title = ""
    current_content = []
    current_type = ""

    for line in lines:
        is_heading, heading_type, heading_text = detect_chapter_heading(line)

        if is_heading:
            # 保存上一章节
            if current_content:
                chapters.append((current_title, "\n".join(current_content)))

            current_title = heading_text
            current_type = heading_type
            current_content = []
        else:
            current_content.append(line)

    # 保存最后一章
    if current_content:
        chapters.append((current_title, "\n".join(current_content)))

    return chapters


def split_by_paragraphs(text: str) -> List[str]:
    """
    按段落分割（双换行分隔）
    """
    paragraphs = text.split("\n\n")
    return [p.strip() for p in paragraphs if p.strip()]


class TextbookSplitter(SemanticTextSplitter):
    """
    教材分割器

    分割策略（按优先级）：
    1. 识别章节标题，按章节分割
    2. 章节过大时，按段落分割
    3. 段落过大时，按句子分割
    4. 句子仍超限时，按字符数硬切 + overlap
    """

    def __init__(
        self,
        max_tokens: int = None,
        overlap: int = 200,
        chunk_size_chars: int = 3000,
    ):
        """
        Args:
            max_tokens: 最大 token 数上限
            overlap: 块之间重叠字符数
            chunk_size_chars: 目标 chunk 字符数（默认 3000）
        """
        super().__init__(max_tokens, overlap)
        self.chunk_size_chars = chunk_size_chars

    def split_document(self, doc: Document) -> List[Document]:
        """分割教材文档"""
        text = doc.page_content
        metadata = doc.metadata.copy()

        # 提取章节信息
        chapter = metadata.get("chapter", "")
        source = metadata.get("source", "unknown")

        # 按章节分割
        chapters = split_by_chapters(text)

        if not chapters:
            # 无法识别章节，整体作为一个 chunk
            return [doc]

        chunks = []
        for title, content in chapters:
            if not content.strip():
                continue

            # 检查内容大小
            tokens = self.estimate_tokens(content)

            if tokens <= self.max_tokens:
                # 大小合适，整体作为一个 chunk
                chunk_meta = metadata.copy()
                chunk_meta["chapter"] = title
                chunks.append(Document(page_content=content, metadata=chunk_meta))
            else:
                # 内容过大，按段落继续分割
                sub_chunks = self._split_large_content(content, metadata, title)

                # 如果段落分割仍超限，按句子
                final_chunks = []
                for sub_chunk in sub_chunks:
                    if self.estimate_tokens(sub_chunk.page_content) > self.max_tokens:
                        sentence_chunks = self._split_by_sentences_fallback(
                            sub_chunk.page_content, sub_chunk.metadata
                        )
                        final_chunks.extend(sentence_chunks)
                    else:
                        final_chunks.append(sub_chunk)

                chunks.extend(final_chunks)

        # 如果没有成功分割，返回原文档
        if not chunks:
            return [doc]

        return chunks

    def _split_large_content(
        self, content: str, metadata: dict, chapter_title: str
    ) -> List[Document]:
        """处理大内容块的分割（按段落）"""
        paragraphs = split_by_paragraphs(content)
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self.estimate_tokens(para)

            if current_tokens + para_tokens <= self.max_tokens:
                current_chunk.append(para)
                current_tokens += para_tokens
            else:
                # 保存当前 chunk
                if current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    chunk_meta = metadata.copy()
                    chunk_meta["chapter"] = chapter_title
                    chunks.append(Document(page_content=chunk_text, metadata=chunk_meta))

                # 开始新 chunk（如果段落本身就超限，按句子切）
                if para_tokens > self.max_tokens:
                    sentence_chunks = self._split_by_sentences_fallback(para, metadata)
                    chunks.extend(sentence_chunks)
                    current_chunk = []
                    current_tokens = 0
                else:
                    current_chunk = [para]
                    current_tokens = para_tokens

        # 保存最后一个 chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunk_meta = metadata.copy()
            chunk_meta["chapter"] = chapter_title
            chunks.append(Document(page_content=chunk_text, metadata=chunk_meta))

        return chunks

    def _split_by_sentences_fallback(
        self, text: str, metadata: dict
    ) -> List[Document]:
        """按句子分割（当段落也超限时）"""
        # 句子分隔符
        separators = ["。", "！", "？", "；", "\n"]
        sentences = [text]
        for sep in separators:
            new_sentences = []
            for s in sentences:
                if self.estimate_tokens(s) <= self.max_tokens:
                    new_sentences.append(s)
                else:
                    new_sentences.extend(s.split(sep))
            sentences = new_sentences

        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return [Document(page_content=text, metadata=metadata)]

        chunks = []
        current_chunk = []
        current_tokens = 0

        for sent in sentences:
            sent_tokens = self.estimate_tokens(sent)

            if current_tokens + sent_tokens <= self.max_tokens:
                current_chunk.append(sent)
                current_tokens += sent_tokens
            else:
                if current_chunk:
                    chunk_text = "。".join(current_chunk) + "。" if current_chunk[-1] not in "！？" else "".join(current_chunk)
                    chunks.append(Document(page_content=chunk_text, metadata=metadata))
                current_chunk = [sent]
                current_tokens = sent_tokens

        if current_chunk:
            chunk_text = "。".join(current_chunk) + "。" if current_chunk[-1] not in "！？" else "".join(current_chunk)
            chunks.append(Document(page_content=chunk_text, metadata=metadata))

        return chunks
