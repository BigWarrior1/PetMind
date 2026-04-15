#!/usr/bin/env python3
"""
向量库初始化脚本

使用方法：
    python scripts/init_vectorstore.py          # 增量添加（不清空）
    python scripts/init_vectorstore.py --rebuild  # 重建（先清空再添加）
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.vectorstore import get_vectorstore_manager
from app.rag.text_splitter import split_documents
from app.rag.document_loader import load_documents_from_directory
from app.core.config import KNOWLEDGE_BASE_DIR
from langchain_core.documents import Document


def deduplicate_documents(documents: list) -> list:
    """
    基于内容 hash 对文档去重

    即使文件名不同，如果内容完全一样也只保留一份
    """
    import hashlib

    seen_hashes = set()
    unique_docs = []
    duplicate_count = 0
    duplicate_sources: dict = {}

    for doc in documents:
        # 用内容生成hash（加入来源防止误判）
        content_for_hash = f"{doc.page_content}|{doc.metadata.get('source', '')}"
        content_hash = hashlib.md5(content_for_hash.encode()).hexdigest()

        if content_hash not in seen_hashes:
            unique_docs.append(doc)
            seen_hashes.add(content_hash)
        else:
            duplicate_count += 1
            source = doc.metadata.get('source', 'unknown')
            duplicate_sources[source] = duplicate_sources.get(source, 0) + 1

    if duplicate_count > 0:
        print(f"  已去除 {duplicate_count} 个重复文档")
        for source, count in duplicate_sources.items():
            print(f"    - {source}: {count} 个重复")

    return unique_docs


def load_raw_documents():
    """加载原始文档"""
    docs_path = Path(KNOWLEDGE_BASE_DIR)

    # 如果目录不存在，创建它
    if not docs_path.exists():
        docs_path.mkdir(parents=True, exist_ok=True)
        print(f"创建知识库目录: {docs_path}")
        return []

    # 检查目录下是否有支持的文档
    supported_extensions = [".pdf", ".txt", ".docx"]
    has_files = any(
        list(docs_path.glob(f"**/*{ext}")) for ext in supported_extensions
    )

    if not has_files:
        print(f"目录 {docs_path} 中没有找到 PDF/TXT/DOCX 文档")
        return []

    # 加载所有文档
    print(f"\n从 {docs_path} 加载文档...")
    documents = load_documents_from_directory(str(docs_path))

    return documents


def init_vectorstore(rebuild: bool = False):
    """初始化向量库

    Args:
        rebuild: 是否重建（先清空再添加）
    """
    print("=" * 50)
    print("PetMind 向量库初始化")
    print("=" * 50)

    # 加载文档
    print("\n[1/3] 加载原始文档...")
    raw_docs = load_raw_documents()

    if not raw_docs:
        print("\n未找到文档，使用示例数据进行测试...")
        # 创建示例文档用于测试（带置信度元数据）
        sample_docs = [
            Document(
                page_content="犬瘟热是一种高度传染性的病毒性疾病，主要症状包括：发热、咳嗽、眼鼻分泌物、呕吐、腹泻、抽搐等。预防方法是接种犬瘟热疫苗。",
                metadata={
                    "source": "犬瘟热防治指南.txt",
                    "source_type": "权威手册",
                    "confidence": 0.95,
                    "type": "disease"
                },
            ),
            Document(
                page_content="猫传染性腹膜炎(FIP)是由猫冠状病毒变异引起的疾病，分为干性和湿性两种类型。湿性FIP表现为腹水或胸水，干性FIP表现为器官损伤。",
                metadata={
                    "source": "猫传染性腹膜炎防治手册.txt",
                    "source_type": "权威手册",
                    "confidence": 0.90,
                    "type": "disease"
                },
            ),
            Document(
                page_content="宠物疫苗接种指南：\n- 犬：狂犬疫苗、犬瘟热疫苗、犬细小病毒疫苗、犬腺病毒疫苗\n- 猫：狂犬疫苗、猫瘟疫苗、猫杯状病毒疫苗、猫疱疹病毒疫苗\n幼崽首免时间：6-8周龄，每隔2-3周加强一次，直到16周龄。",
                metadata={
                    "source": "宠物疫苗接种指南.txt",
                    "source_type": "学术论文",
                    "confidence": 0.85,
                    "type": "vaccine"
                },
            ),
        ]
        print(f"创建 {len(sample_docs)} 个示例文档用于测试")
        raw_docs = sample_docs

    print(f"共加载 {len(raw_docs)} 个文档")

    # 过滤空文档
    print("\n[检查空文档...]")
    non_empty_docs = []
    empty_count = 0
    empty_files = {}
    for doc in raw_docs:
        content = doc.page_content.strip()
        if not content or len(content) < 10:  # 少于10字符的视为无效内容
            empty_count += 1
            source = doc.metadata.get('source', 'unknown')
            empty_files[source] = empty_files.get(source, 0) + 1
            continue
        doc.page_content = content  # 更新为清洗后的内容
        non_empty_docs.append(doc)

    if empty_count > 0:
        print(f"  发现 {empty_count} 个空/无效文档已过滤")
        for source, count in empty_files.items():
            print(f"    - {source}: {count} 个空文档")
        print(f"  有效文档: {len(non_empty_docs)} 个")
    raw_docs = non_empty_docs

    # 去重
    print("\n[检查重复文档...]")
    raw_docs = deduplicate_documents(raw_docs)
    print(f"去重后剩余 {len(raw_docs)} 个文档")

    # 分割文档
    print("\n[2/3] 分割文档...")
    chunks = split_documents(raw_docs)
    print(f"分割成 {len(chunks)} 个文本块")

    # 写入向量库
    print("\n[3/3] 写入向量库...")
    vectorstore_manager = get_vectorstore_manager()

    if rebuild:
        print("  [重建模式] 先清空现有向量库...")
        vectorstore_manager.delete_collection()

    vectorstore_manager.add_documents(chunks)
    print("向量库初始化完成！")

    print("\n" + "=" * 50)
    print("下一步：运行 python scripts/test_rag.py 测试 RAG 流程")
    print("=" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PetMind 向量库初始化脚本")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="重建模式：先清空向量库再重新添加文档",
    )
    args = parser.parse_args()

    init_vectorstore(rebuild=args.rebuild)
