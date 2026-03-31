#!/usr/bin/env python3
"""
RAG 测试脚本

使用方法：
    python scripts/test_rag.py
"""
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.rag_service import get_rag_service


def test_rag():
    """测试 RAG 问答"""
    print("=" * 50)
    print("PetMind RAG 测试")
    print("=" * 50)

    # 测试问题
    test_questions = [
        "狗狗咳嗽怎么办？",
        "猫瘟有什么症状？",
        "宠物疫苗怎么接种？",
    ]

    rag_service = get_rag_service()

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 50}")
        print(f"测试 {i}: {question}")
        print("-" * 50)

        result = rag_service.ask(question)

        print(f"回答：\n{result['answer']}")
        print(f"\n来源数量：{len(result['sources'])}")
        for j, source in enumerate(result['sources'], 1):
            print(f"  [{j}] {source['source']}")
            print(f"      类型: {source.get('source_type', 'N/A')}, 置信度: {source.get('confidence', 0):.2f}")
            print(f"      语义相似度: {source.get('semantic_score', 0):.4f}, 综合评分: {source.get('combined_score', 0):.4f}")

        if result['warning']:
            print(f"\n警示：{result['warning']}")

    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    test_rag()
