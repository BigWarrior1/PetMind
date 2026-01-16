"""
初始化向量数据库
批量加载知识库文档并建立向量索引
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.logging import logger
from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextSplitter
from app.rag.vectorstore import VectorStoreManager


def initialize_vectorstore(
    data_dir: str = None,
    clean: bool = False,
):
    """
    初始化向量数据库

    Args:
        data_dir: 数据目录路径
        clean: 是否清空现有数据
    """
    try:
        logger.info("=" * 60)
        logger.info("开始初始化向量数据库")
        logger.info("=" * 60)

        # 数据目录
        if data_dir is None:
            data_dir = settings.data_dir / "raw"
        else:
            data_dir = Path(data_dir)

        logger.info(f"数据目录: {data_dir}")

        # 检查数据目录
        if not data_dir.exists():
            logger.error(f"数据目录不存在: {data_dir}")
            return

        # 初始化向量数据库管理器
        vectorstore = VectorStoreManager()

        # 清空现有数据
        if clean:
            logger.warning("清空现有向量数据库...")
            vectorstore.delete_collection()
            vectorstore = VectorStoreManager()  # 重新初始化

        # 加载文档
        logger.info("加载文档...")
        documents = DocumentLoader.load_directory(
            directory_path=data_dir,
            glob_pattern="**/*.txt",
            show_progress=True,
        )

        if not documents:
            logger.warning("未找到任何文档")
            return

        logger.info(f"成功加载 {len(documents)} 个文档")

        # 切分文档
        logger.info("切分文档...")
        text_splitter = TextSplitter()
        split_docs = text_splitter.split_documents(documents)

        logger.info(f"切分后共 {len(split_docs)} 个文档块")

        # 添加到向量库
        logger.info("添加文档到向量库（此过程可能需要几分钟）...")
        ids = vectorstore.add_documents(split_docs)

        logger.info(f"成功添加 {len(ids)} 个文档块到向量库")

        # 验证
        count = vectorstore.get_collection_count()
        logger.info(f"向量库中共有 {count} 个文档")

        logger.info("=" * 60)
        logger.info("向量数据库初始化完成！")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"初始化向量数据库时发生错误: {str(e)}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="初始化向量数据库")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="数据目录路径（默认: data/raw）",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="清空现有数据",
    )

    args = parser.parse_args()

    initialize_vectorstore(
        data_dir=args.data_dir,
        clean=args.clean,
    )
