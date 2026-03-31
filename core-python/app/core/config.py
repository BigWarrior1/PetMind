"""
应用配置管理
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# API 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# 向量数据库配置
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "data" / "chroma_db"))

# 知识库配置
KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", str(BASE_DIR / "data" / "raw"))

# Embedding 配置
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-large-zh-v1.5")
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cuda")  # cuda 或 cpu

# RAG 配置
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_SCORE_THRESHOLD = float(os.getenv("RAG_SCORE_THRESHOLD", "0.5"))

# 集合名称
CHROMA_COLLECTION_NAME = "pet_health_kb"
