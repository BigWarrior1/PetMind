# PetMind Core Python

宠物健康智能问答系统 - AI 核心服务

## 环境准备

### 1. 创建并激活虚拟环境

```bash
cd core-python

# 创建虚拟环境
python -m venv venv

# Windows 激活
venv\Scripts\activate

# Linux/Mac 激活
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env_example .env
# 编辑 .env，填入你的 DASHSCOPE_API_KEY
```

### 4. 初始化向量库

```bash
python scripts/init_vectorstore.py
```

### 5. 测试 RAG 流程

```bash
python scripts/test_rag.py
```

### 6. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

## 项目结构

```
core-python/
├── app/
│   ├── api/              # API 路由
│   ├── core/             # 核心配置
│   ├── models/           # 数据模型
│   ├── rag/              # RAG 组件
│   │   ├── document_loader.py   # 文档加载
│   │   ├── embeddings.py        # Embedding 模型
│   │   ├── vectorstore.py       # 向量数据库
│   │   ├── text_splitter.py     # 文本分割
│   │   └── retriever.py         # 检索器
│   ├── services/         # 业务服务
│   │   ├── llm_service.py       # LLM 调用
│   │   └── rag_service.py       # RAG 服务
│   └── main.py           # FastAPI 入口
├── data/
│   ├── raw/              # 原始知识库文档
│   └── chroma_db/        # 向量数据库文件
├── prompts/              # Prompt 模板
├── scripts/              # 工具脚本
│   ├── init_vectorstore.py      # 向量库初始化
│   └── test_rag.py             # RAG 测试
├── tests/                # 测试
├── requirements.txt
└── .env_example
```

## 技术栈

- **Web 框架**: FastAPI + Uvicorn
- **LangChain**: 最新版本 (0.3+)
- **Embedding**: bge-large-zh-v1.5 (本地运行，3060 可用)
- **向量库**: Chroma
- **LLM**: 阿里百炼 qwen-plus / qwen-vl-plus
