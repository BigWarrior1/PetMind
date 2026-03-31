"""
Embedding 模型封装
使用阿里 DashScope text-embedding-v3 API
"""
from langchain_community.embeddings import DashScopeEmbeddings
from app.core.config import DASHSCOPE_API_KEY


def get_embedding_model():
    """
    获取 Embedding 模型

    使用阿里 text-embedding-v3，费用低（0.0007元/千tokens），中文效果好
    """
    return DashScopeEmbeddings(
        model="text-embedding-v3",
        dashscope_api_key=DASHSCOPE_API_KEY,
    )


# 全局单例
_embedding_model = None


def get_embeddings():
    """获取全局 Embedding 实例"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = get_embedding_model()
    return _embedding_model
