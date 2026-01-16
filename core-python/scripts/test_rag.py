"""
测试 RAG 问答功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.logging import logger
from app.services.rag_service import RAGService


async def test_rag():
    """测试 RAG 问答"""
    try:
        logger.info("=" * 60)
        logger.info("测试 RAG 问答功能")
        logger.info("=" * 60)

        # 初始化 RAG 服务
        rag_service = RAGService()

        # 测试问题列表
        test_questions = [
            "狗狗出现高烧和咳嗽怎么办？",
            "猫传腹有哪些症状？",
            "幼犬什么时候开始打疫苗？",
            "犬瘟热的治疗方法有哪些？",
        ]

        for i, question in enumerate(test_questions, 1):
            logger.info(f"\n{'=' * 60}")
            logger.info(f"问题 {i}: {question}")
            logger.info(f"{'=' * 60}")

            # 执行问答
            result = await rag_service.answer_question(question=question)

            # 打印结果
            print(f"\n问题: {question}")
            print(f"\n回答:\n{result['answer']}")
            print(f"\n置信度: {result.get('confidence', 0):.2f}")
            print(f"\n知识来源:")
            for j, source in enumerate(result.get('sources', []), 1):
                print(f"  [{j}] {source.source} (相似度: {source.score:.2f})")
                print(f"      {source.content[:100]}...")

            if result.get('warning'):
                print(f"\n⚠️ {result['warning']}")

            print("\n")

        logger.info("=" * 60)
        logger.info("测试完成")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"测试时发生错误: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(test_rag())
