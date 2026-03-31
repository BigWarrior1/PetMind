# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

PetMind 是一个基于 LLM + RAG 技术的宠物健康智能问答系统，旨在为宠物主人提供可追溯的、专业权威的健康信息参考。

**核心目标**：减少通用大语言模型的"幻觉"问题，提供基于兽医知识库的可靠回答，并引导用户及时联系执业兽医。

## 技术架构

### 微服务架构

```
Vue 3 Frontend → Go Gin Gateway → Python FastAPI (RAG Engine) → Chroma DB / 阿里qwen
```

### 三大核心模块

| 模块 | 技术栈 | 状态 |
|------|--------|------|
| `frontend/` | Vue 3 + Vite + TailwindCSS | 规划中 |
| `backend-go/` | Go + Gin + GORM + MySQL/PostgreSQL | 规划中 |
| `core-python/` | Python + FastAPI + LangChain + Chroma | **当前开发重点** |

### AI 服务架构 (core-python/)

```
API Layer (FastAPI)
    ↓
Service Layer (RAGService, LLMService, MultiModalService)
    ↓
RAG Components (Embeddings, VectorStore, Retriever)
    ↓
Model Layer (阿里百炼 API: qwen-plus, qwen-vl-plus)
```

## 当前开发重点

**Phase 1**: Python 核心 AI 引擎原型验证 (RAG 流程)

核心文件结构：
```
core-python/
├── app/
│   ├── api/v1/endpoints/    # API 路由
│   ├── core/                # 核心配置
│   ├── models/              # 数据模型
│   ├── rag/                 # RAG 组件
│   │   ├── document_loader.py
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   ├── text_splitter.py
│   │   └── vectorstore.py
│   ├── services/            # 业务服务
│   │   ├── llm_service.py
│   │   └── rag_service.py
│   └── utils/               # 工具函数
├── data/raw/                # 原始兽医知识库文档
├── prompts/                 # Prompt 模板
├── scripts/                 # 初始化脚本
│   ├── init_vectorstore.py  # 向量库初始化
│   └── test_rag.py          # RAG 测试脚本
└── requirements.txt
```

## 关键配置

**必需的环境变量**:
- `DASHSCOPE_API_KEY`: 阿里百炼平台密钥

**向量数据库**: Chroma (本地持久化, SQLite 后端)

**Embedding 模型**: bge-large-zh-v1.5 (LangChain 本地运行，3060可用)

**LLM 模型**: qwen-plus (问答), qwen-vl-plus (多模态图片分析)

## 开发命令

### core-python 模块

```bash
cd core-python

# 安装依赖
pip install -r requirements.txt

# 初始化向量数据库
python scripts/init_vectorstore.py

# 运行 RAG 测试
python scripts/test_rag.py

# 启动 FastAPI 服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API 文档
# http://localhost:8000/docs
```

## 重要设计决策

### RAG 检索策略
- Top-K 相似度检索
- 支持按宠物类型、疾病类别等元数据过滤
- 检索结果与 Prompt 组合时包含安全警示

### 安全风控
- 识别宠物危急重症，优先输出就医警示
- 系统定位是**健康信息辅助与风险提示**，不替代执业兽医诊断

### 开发阶段技术选型
- 向量库: Chroma (生产可选 Qdrant/Milvus)
- 用户数据库: SQLite → PostgreSQL
- Embedding: **bge-large-zh-v1.5 (LangChain 本地部署，3060可用，完全免费)**

## 项目阶段

- [x] ~~Phase 0~~: 需求分析与技术选型 ✅
- [ ] **Phase 1**: Python 核心 AI 引擎 (RAG 问答流程)
- [ ] **Phase 1.5**: 多模态扩展 (图片分析)
- [ ] **Phase 2**: Go 后端基础框架搭建
- [ ] **Phase 3**: 前端 MVP 版本开发
- [ ] **Phase 4**: 前后端联调与完整链路测试
