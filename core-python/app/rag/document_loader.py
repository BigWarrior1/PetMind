"""
文档加载器
负责加载各类兽医知识文档 (PDF, TXT, DOCX, CSV)

使用 LangChain 的 DocumentLoader 统一接口
"""
import re
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document

# 文档来源类型 → 置信度映射
SOURCE_RELIABILITY = {
    # 权威手册
    "兽医教材": 0.95,
    "权威手册": 0.95,
    "教科书": 0.95,
    "手册": 0.90,
    "指南": 0.90,
    "百科": 0.90,
    # 学术论文
    "论文": 0.85,
    "学术": 0.85,
    "研究": 0.85,
    "期刊": 0.85,
    "conference": 0.85,
    "journal": 0.85,
    # 官方网站
    "官方": 0.80,
    "医院": 0.75,
    "cdc": 0.85,
    "who": 0.90,
    "gov": 0.85,
    "农业": 0.80,
    # 开源/社区
    "kaggle": 0.60,
    "github": 0.55,
    "stackoverflow": 0.50,
    "社区": 0.50,
    "wiki": 0.55,
    # LLM生成
    "gpt": 0.40,
    "llm": 0.40,
    "生成": 0.35,
    "ai": 0.35,
    # 问答数据
    "qa": 0.65,
    "问答": 0.65,
    "faq": 0.60,
    "question": 0.60,
    # 默认
    "unknown": 0.50,
}

# 最低置信度阈值
MIN_CONFIDENCE_THRESHOLD = 0.30


def infer_source_confidence(filename: str) -> tuple:
    """
    根据文件名推断来源类型和置信度
    """
    filename_lower = filename.lower()

    if any(keyword in filename_lower for keyword in ["教材", "教科书", "手册", "指南", "百科", "权威"]):
        return "权威手册", SOURCE_RELIABILITY["权威手册"]
    elif any(keyword in filename_lower for keyword in ["论文", "学术", "研究", "期刊", "conference", "journal"]):
        return "学术论文", SOURCE_RELIABILITY["学术论文"]
    elif any(keyword in filename_lower for keyword in ["who", "cdc", "gov", "官方", "农业", "农业农村"]):
        return "官方网站", SOURCE_RELIABILITY["官方网站"]
    elif any(keyword in filename_lower for keyword in ["医院", "诊所", "医疗"]):
        return "医疗机构", SOURCE_RELIABILITY["医院"]
    elif any(keyword in filename_lower for keyword in ["kaggle", "github", "社区", "wiki", "stackoverflow"]):
        return "开源社区", SOURCE_RELIABILITY["github"]
    elif any(keyword in filename_lower for keyword in ["gpt", "llm", "ai", "生成", "chat"]):
        return "AI生成", SOURCE_RELIABILITY["AI生成"]
    elif any(keyword in filename_lower for keyword in ["qa", "faq", "问答", "question"]):
        return "问答数据", SOURCE_RELIABILITY["qa"]
    else:
        return "通用文档", SOURCE_RELIABILITY["unknown"]


# ==================== 数据清洗函数 ====================

def clean_text(text: str) -> str:
    """
    清洗文本，去除乱码和规范化格式

    处理内容：
    - 去除非打印字符
    - 规范化空白字符
    - 去除页眉页脚（简单版）
    - 去除多余换行
    """
    if not text:
        return ""

    # 去除非打印字符（保留中文、英文、数字、常用标点）
    # \x00-\x08, \x0b-\x0c, \x0e-\x1f, \x7f
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # 规范化换行（多个换行变成两个）
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 去除行首行尾空白
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    # 去除多余空格（多个空格变一个）
    text = re.sub(r' {2,}', ' ', text)

    # 去除Tab
    text = text.replace('\t', ' ')

    # 去除常见页眉页脚模式
    page_header_patterns = [
        r'第\s*\d+\s*页',  # 第 1 页
        r'共\s*\d+\s*页',  # 共 10 页
        r'第\s*\d+\s*页/共\s*\d+\s*页',
        r'Page\s+\d+',  # Page 1
        r'\d+/\d+',  # 1/10
    ]
    for pattern in page_header_patterns:
        text = re.sub(pattern, '', text)

    return text.strip()


def clean_pdf_text(text: str) -> str:
    """
    专门清洗PDF提取的文本
    PDF提取经常有奇怪的问题
    """
    text = clean_text(text)

    # 去除孤立的一个字（通常是PDF识别错误）
    # 但这可能误杀，所以保守处理

    # 去除 "•" "-" 等开头的不完整行
    lines = text.split('\n')
    cleaned_lines = []
    consecutive_short_lines = 0

    for line in lines:
        stripped = line.strip()

        # 跳过只有1-2个字符的行（很可能是识别错误），但统计连续短行
        if len(stripped) <= 2 and not stripped.isdigit():
            consecutive_short_lines += 1
            if consecutive_short_lines >= 3:
                continue  # 跳过可疑的连续短行（可能是页眉/页脚）
            continue
        else:
            consecutive_short_lines = 0

        # 检测表格行（用 | 或 空格 分隔的多列数据）
        # 保留表格但转换为简洁格式
        if '|' in stripped or (len(stripped) > 20 and ' ' in stripped and stripped.count(' ') >= 3):
            # 可能是表格行，规范化空格
            parts = stripped.split()
            if len(parts) >= 2:
                stripped = ' | '.join(parts)
            # 跳过仅含分隔符的行
            if stripped.strip('| \t') == '':
                continue

        cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    return text


def detect_chapter_from_content(text: str) -> str:
    """
    从PDF内容中检测章节标题（用于补充 metadata）

    检测模式：
    - "第X章"
    - "【标题】"
    - "X. 标题"
    """
    import re

    patterns = [
        r'第[一二三四五六七八九十百千\d]+[章节篇部][^\n]{0,50}',
        r'【([^】]+)》',
        r'^([A-Z][\.\)][^\n]{0,50})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(0)[:100]  # 限制长度

    return ""


# ==================== 文档加载器基类 ====================

class DocumentLoader:
    """文档加载器基类"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load(self) -> List[Document]:
        """加载文档，返回 Document 列表"""
        raise NotImplementedError

    def get_metadata(self) -> dict:
        """获取文档元数据，包含来源和置信度"""
        source_type, confidence = infer_source_confidence(self.file_path.name)
        return {
            "source": self.file_path.name,
            "source_type": source_type,
            "confidence": confidence,
            "file_path": str(self.file_path),
        }

    def clean_content(self, content: str) -> str:
        """清洗文档内容，子类可以重写"""
        return clean_text(content)


# ==================== 各类型文档加载器 ====================

class PDFLoader(DocumentLoader):
    """PDF 文档加载"""

    def load(self) -> List[Document]:
        try:
            from langchain_community.document_loaders import PyPDFLoader
        except ImportError:
            raise ImportError("请安装 PyPDFLoader: pip install pypdf")

        loader = PyPDFLoader(str(self.file_path))
        documents = loader.load()

        for doc in documents:
            doc.page_content = self.clean_content(doc.page_content)
            doc.metadata.update(self.get_metadata())

            # 检测章节标题并添加到 metadata
            chapter = detect_chapter_from_content(doc.page_content)
            if chapter:
                doc.metadata["chapter"] = chapter

        return documents

    def clean_content(self, content: str) -> str:
        return clean_pdf_text(content)


class TXTLoader(DocumentLoader):
    """TXT 文档加载"""

    def load(self) -> List[Document]:
        try:
            from langchain_community.document_loaders import TextLoader
        except ImportError:
            raise ImportError("请安装 TextLoader: pip install langchain-community")

        loader = TextLoader(str(self.file_path), encoding="utf-8")
        documents = loader.load()

        for doc in documents:
            doc.page_content = self.clean_content(doc.page_content)
            doc.metadata.update(self.get_metadata())

        return documents


class DOCXLoader(DocumentLoader):
    """DOCX 文档加载"""

    def load(self) -> List[Document]:
        try:
            from langchain_community.document_loaders import UnstructuredWordDocumentLoader
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")

        loader = UnstructuredWordDocumentLoader(str(self.file_path))
        documents = loader.load()

        for doc in documents:
            doc.page_content = self.clean_content(doc.page_content)
            doc.metadata.update(self.get_metadata())

        return documents


class CSVLoader(DocumentLoader):
    """
    CSV 问答数据加载器

    支持的 CSV 格式：
    - question, answer
    - Q, A
    - question, answer, source
    - 问, 答
    """

    def load(self) -> List[Document]:
        import csv

        documents = []
        source_type, confidence = infer_source_confidence(self.file_path.name)

        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row_num, row in enumerate(reader, 1):
                # 尝试匹配常见的列名
                question = self._find_column(row, ['question', 'q', '问', '问题'])
                answer = self._find_column(row, ['answer', 'a', '答', '答案'])
                source = self._find_column(row, ['source', '来源', '出处'])
                conf = self._find_column(row, ['confidence', '置信度', '可信度'])

                if not question or not answer:
                    continue

                # 清洗内容
                question = self.clean_content(question)
                answer = self.clean_content(answer)

                # 构建文档
                metadata = {
                    "source": source or self.file_path.name,
                    "source_type": source_type,
                    "confidence": float(conf) if conf else confidence,
                    "file_path": str(self.file_path),
                    "row_num": row_num,
                    "is_qa": True,  # 标记为问答数据，分割时整体保留
                }

                # 问答格式：问题和答案作为一个chunk
                content = f"问：{question}\n答：{answer}"

                documents.append(Document(page_content=content, metadata=metadata))

        return documents

    def _find_column(self, row: dict, candidates: List[str]) -> Optional[str]:
        """从多个可能的列名中找到存在的那个"""
        row_lower = {k.lower().strip(): v for k, v in row.items()}
        for candidate in candidates:
            if candidate.lower() in row_lower:
                return row_lower[candidate.lower()]
        return None


class CSVQALoader(CSVLoader):
    """CSV 问答加载器的别名（语义更明确）"""
    pass


# ==================== 工厂函数 ====================

def get_loader(file_path: str) -> DocumentLoader:
    """
    根据文件扩展名获取对应的加载器
    """
    suffix = Path(file_path).suffix.lower()

    loaders = {
        ".pdf": PDFLoader,
        ".txt": TXTLoader,
        ".docx": DOCXLoader,
        ".csv": CSVLoader,
    }

    if suffix not in loaders:
        raise ValueError(f"不支持的文件类型: {suffix}，支持的类型: {list(loaders.keys())}")

    return loaders[suffix](file_path)


def load_document(file_path: str) -> List[Document]:
    """加载单个文档"""
    loader = get_loader(file_path)
    return loader.load()


def load_documents_from_directory(directory: str, extensions: List[str] = None) -> List[Document]:
    """
    从目录加载所有支持的文档
    """
    if extensions is None:
        extensions = [".pdf", ".txt", ".docx", ".csv"]

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
                    print(f"  ✅ 加载成功: {file_path.name} ({len(documents)} 个文档)")
                except Exception as e:
                    print(f"  ❌ 加载失败: {file_path.name}, 错误: {e}")

    return all_documents
