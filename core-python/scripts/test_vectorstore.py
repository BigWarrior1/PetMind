#!/usr/bin/env python3
"""
向量库效果测试脚本

展示语义分割的效果：
1. 查看分割后的 chunk 内容
2. 测试不同查询的检索结果
3. 对比新旧分割策略的差异

使用方法：
    python scripts/test_vectorstore.py
"""
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.vectorstore import get_vectorstore_manager
from app.rag.text_splitter import split_documents
from app.rag.document_loader import load_documents_from_directory
from app.rag.splitters import AdaptiveTextSplitter


def print_chunk(doc, index, max_content_len=300):
    """格式化打印 chunk"""
    content = doc.page_content
    if len(content) > max_content_len:
        content = content[:max_content_len] + "..."

    metadata = doc.metadata
    print(f"\n--- Chunk {index} ---")
    print(f"来源: {metadata.get('source', 'unknown')}")
    print(f"类型: {metadata.get('source_type', 'unknown')}")
    print(f"置信度: {metadata.get('confidence', 0):.2f}")
    if metadata.get('chapter'):
        print(f"章节: {metadata['chapter']}")
    if metadata.get('is_qa'):
        print(f"问答: 是")
    print(f"长度: {len(doc.page_content)} 字符")
    print(f"内容: {content}")


def test_view_chunks():
    """查看向量库中的 chunks"""
    print("=" * 60)
    print("测试 1: 查看向量库中的 chunks")
    print("=" * 60)

    vectorstore_manager = get_vectorstore_manager()

    # 获取所有文档
    collection = vectorstore_manager.collection
    total = collection.count()

    print(f"\n向量库中共有 {total} 个 chunks\n")

    if total == 0:
        print("向量库为空！请先运行: python scripts/init_vectorstore.py --rebuild")
        return

    # 随机查看几个 chunks
    import random

    # 获取所有数据的 sample
    sample_size = min(5, total)
    print(f"随机查看 {sample_size} 个 chunks:\n")

    # 按来源类型统计
    all_data = collection.get(include=["metadatas"])
    source_types = {}
    for meta in all_data["metadatas"]:
        source_type = meta.get("source_type", "unknown")
        source_types[source_type] = source_types.get(source_type, 0) + 1

    print("来源类型统计:")
    for stype, count in sorted(source_types.items(), key=lambda x: -x[1]):
        print(f"  {stype}: {count} 个")

    print("\n" + "-" * 60)


def test_split_effect():
    """测试分割效果"""
    print("\n" + "=" * 60)
    print("测试 2: 语义分割效果对比")
    print("=" * 60)

    docs_path = Path(__file__).parent.parent / "data" / "raw"

    if not docs_path.exists():
        print(f"\n知识库目录不存在: {docs_path}")
        return

    # 加载一个 PDF 和一个 CSV 文档
    from app.rag.document_loader import get_loader

    # 找一个 PDF
    pdf_files = list(docs_path.glob("*.pdf"))
    if pdf_files:
        pdf_path = pdf_files[0]
        loader = get_loader(str(pdf_path))
        pdf_docs = loader.load()
        print(f"\n测试 PDF: {pdf_path.name}")
        print(f"原始页面数: {len(pdf_docs)}")

        # 用新的语义分割
        splitter = AdaptiveTextSplitter()
        chunks = splitter.split_documents(pdf_docs[:3])  # 只测试前3页

        print(f"语义分割后 chunks: {len(chunks)}")
        print(f"平均长度: {sum(len(c.page_content) for c in chunks) / len(chunks):.0f} 字符")

        # 显示前2个 chunks
        print("\n分割示例:")
        for i, chunk in enumerate(chunks[:2]):
            print_chunk(chunk, i + 1)

    # 测试 CSV
    csv_files = list(docs_path.glob("*.csv"))
    if csv_files:
        csv_path = csv_files[0]
        loader = get_loader(str(csv_path))
        csv_docs = loader.load()
        print(f"\n\n测试 CSV: {csv_path.name}")
        print(f"原始问答对数: {len(csv_docs)}")

        # 用新的语义分割
        splitter = AdaptiveTextSplitter()
        chunks = splitter.split_documents(csv_docs)

        print(f"语义分割后 chunks: {len(chunks)}")
        print(f"是否整体保留: {'是' if len(chunks) == len(csv_docs) else '否'}")

        # 显示前2个 chunks
        print("\n分割示例:")
        for i, chunk in enumerate(chunks[:2]):
            print_chunk(chunk, i + 1)


def test_query_retrieval():
    """测试查询检索效果"""
    print("\n" + "=" * 60)
    print("测试 3: 查询检索效果")
    print("=" * 60)

    from app.rag.retriever import RAGRetriever

    retriever = RAGRetriever(top_k=3)

    test_queries = [
        "犬瘟热的症状有哪些？",
        "如何给猫咪接种疫苗？",
        "狗狗咳嗽怎么办？",
        "猫瘟热的治疗方法",
    ]

    for query in test_queries:
        print(f"\n\n查询: {query}")
        print("-" * 40)

        docs = retriever.retrieve(query)

        if not docs:
            print("未找到相关结果")
            continue

        print(f"找到 {len(docs)} 个相关 chunks:\n")

        for i, doc in enumerate(docs, 1):
            content = doc.page_content
            if len(content) > 200:
                content = content[:200] + "..."

            print(f"[{i}] {doc.metadata.get('source', 'unknown')}")
            print(f"    置信度: {doc.metadata.get('confidence', 0):.2f}, "
                  f"类型: {doc.metadata.get('source_type', 'unknown')}")
            if doc.metadata.get('chapter'):
                print(f"    章节: {doc.metadata['chapter']}")
            print(f"    内容: {content}")
            print()


def test_old_vs_new():
    """对比旧策略和新策略的分割差异"""
    print("\n" + "=" * 60)
    print("测试 4: 旧策略 vs 新策略对比")
    print("=" * 60)

    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from app.rag.document_loader import load_documents_from_directory

    docs_path = Path(__file__).parent.parent / "data" / "raw"

    if not docs_path.exists():
        print(f"\n知识库目录不存在: {docs_path}")
        return

    # 加载一个示例 PDF
    pdf_files = list(docs_path.glob("*.pdf"))
    if not pdf_files:
        print("没有找到 PDF 文件")
        return

    from app.rag.document_loader import get_loader

    pdf_path = pdf_files[0]
    loader = get_loader(str(pdf_path))
    pdf_docs = loader.load()

    # 取第一页测试
    test_doc = pdf_docs[0] if pdf_docs else None
    if not test_doc:
        print("无法加载文档")
        return

    print(f"\n测试文档: {pdf_path.name} (第1页)")
    print(f"原始长度: {len(test_doc.page_content)} 字符")

    # 旧策略 (固定大小 500 字符)
    old_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],
    )
    old_chunks = old_splitter.split_documents([test_doc])

    # 新策略 (语义分割)
    new_splitter = AdaptiveTextSplitter()
    new_chunks = new_splitter.split_document(test_doc)

    print(f"\n旧策略 (chunk_size=500):")
    print(f"  分割块数: {len(old_chunks)}")
    print(f"  平均长度: {sum(len(c.page_content) for c in old_chunks) / len(old_chunks):.0f} 字符")

    print(f"\n新策略 (语义分割):")
    print(f"  分割块数: {len(new_chunks)}")
    if new_chunks:
        print(f"  平均长度: {sum(len(c.page_content) for c in new_chunks) / len(new_chunks):.0f} 字符")

    print("\n旧策略示例 (前2个 chunks):")
    for i, c in enumerate(old_chunks[:2]):
        content = c.page_content[:150] + "..." if len(c.page_content) > 150 else c.page_content
        print(f"  [{i+1}] {content}")

    print("\n新策略示例 (前2个 chunks):")
    for i, c in enumerate(new_chunks[:2]):
        content = c.page_content[:150] + "..." if len(c.page_content) > 150 else c.page_content
        print(f"  [{i+1}] {content}")


def main():
    print("=" * 60)
    print("PetMind 向量库效果测试")
    print("=" * 60)

    # 测试1: 查看向量库 chunks
    test_view_chunks()

    # 测试2: 分割效果
    test_split_effect()

    # 测试3: 查询检索
    test_query_retrieval()

    # 测试4: 策略对比
    test_old_vs_new()

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n提示:")
    print("  - 如果向量库为空，先运行: python scripts/init_vectorstore.py --rebuild")
    print("  - 查看更多详情可以修改 max_content_len 参数")
    print("  - 可以修改 test_queries 添加自己的测试问题")


if __name__ == "__main__":
    main()
