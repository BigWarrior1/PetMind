# 宠物健康问答系统 - Python AI 服务项目结构设计方案

> **生成时间**: 2026年1月16日  
> **项目类型**: FastAPI + LangChain + RAG (检索增强生成)  
> **应用场景**: 宠物健康智能问答系统

---

## 📊 一、当前项目状态分析

### 1.1 目录结构现状

```
d:\Develop\Code\projects\graduation_project\demo\python_api\
├── .env                    # 环境变量文件（已配置 DASHSCOPE_API_KEY）
├── .env.example            # 环境变量示例
├── 技术选型决策.md         # 技术选型文档
├── 项目整体介绍.md         # 项目需求与功能说明
└── rule.md                 # AI 编码规范与安全规则
```

### 1.2 关键发现

✅ **已完成**:
- 技术选型已明确（FastAPI + LangChain + 阿里百炼平台）
- API 密钥已配置（`.env` 文件中的 `DASHSCOPE_API_KEY`）
- 项目背景、功能需求、技术规范文档齐全

❌ **缺失**:
- 无任何 Python 代码文件（`.py`）
- 无依赖管理文件（`requirements.txt` / `pyproject.toml`）
- 无项目目录结构（app/, services/ 等）
- 无配置管理模块
- 无测试文件

### 1.3 核心功能需求（基于项目介绍.md）

| 功能模块 | 技术要求 | 优先级 |
|---------|---------|--------|
| **RAG 智能问答** | LangChain + Chroma + 阿里 text-embedding-v3 + qwen-plus | 🔴 P0 |
| **多模态辅助诊断** | qwen-vl-plus（图片理解） | 🟡 P1 |
| **主动问诊 Agent** | LangChain Agent + CoT（思维链） | 🟡 P1 |
| **用户/宠物档案管理** | 个性化 Prompt 注入 | 🟢 P2 |

---

## 🏗️ 二、推荐的项目结构（FastAPI + LangChain 最佳实践）

### 2.1 完整目录树

```
python_api/
│
├── app/                              # 核心应用代码
│   ├── __init__.py
│   │
│   ├── main.py                       # FastAPI 应用入口（路由注册、中间件）
│   │
│   ├── api/                          # API 路由层
│   │   ├── __init__.py
│   │   ├── v1/                       # API v1 版本
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/            # 具体端点
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py           # 对话问答接口
│   │   │   │   ├── multimodal.py     # 多模态图片分析接口
│   │   │   │   ├── agent.py          # 主动问诊 Agent 接口
│   │   │   │   └── health.py         # 健康检查接口
│   │   │   └── router.py             # 路由聚合
│   │   └── deps.py                   # 依赖注入（数据库会话、向量库等）
│   │
│   ├── core/                         # 核心配置与工具
│   │   ├── __init__.py
│   │   ├── config.py                 # pydantic-settings 配置管理
│   │   ├── security.py               # 安全相关（API Key 验证等）
│   │   └── logging.py                # 日志配置（Loguru）
│   │
│   ├── models/                       # 数据模型（Pydantic）
│   │   ├── __init__.py
│   │   ├── request.py                # 请求模型
│   │   ├── response.py               # 响应模型
│   │   └── domain.py                 # 业务领域模型（宠物、问诊记录）
│   │
│   ├── services/                     # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── rag_service.py            # RAG 检索增强生成服务
│   │   ├── llm_service.py            # LLM 调用封装（qwen-plus）
│   │   ├── multimodal_service.py     # 多模态服务（qwen-vl-plus）
│   │   ├── agent_service.py          # 主动问诊 Agent 服务
│   │   └── prompt_service.py         # Prompt 工程与模板管理
│   │
│   ├── rag/                          # RAG 核心组件
│   │   ├── __init__.py
│   │   ├── embeddings.py             # 嵌入模型封装（text-embedding-v3）
│   │   ├── vectorstore.py            # 向量库管理（Chroma）
│   │   ├── retriever.py              # 检索器（相似度搜索、混合检索）
│   │   ├── document_loader.py        # 文档加载（PDF、DOCX、TXT）
│   │   ├── text_splitter.py          # 文本切分策略
│   │   └── chain.py                  # LangChain 链组装
│   │
│   ├── agents/                       # Agent 实现模块
│   │   ├── __init__.py
│   │   ├── diagnosis_agent.py        # 主动问诊 Agent
│   │   ├── tools.py                  # Agent 工具定义
│   │   └── prompts.py                # Agent 专用 Prompt
│   │
│   ├── schemas/                      # 数据验证模式
│   │   ├── __init__.py
│   │   ├── chat.py                   # 对话相关 Schema
│   │   ├── pet.py                    # 宠物档案 Schema
│   │   └── diagnosis.py              # 诊断记录 Schema
│   │
│   ├── db/                           # 数据库相关（如需与 Golang 后端协同）
│   │   ├── __init__.py
│   │   └── models.py                 # ORM 模型（SQLAlchemy，可选）
│   │
│   └── utils/                        # 工具函数
│       ├── __init__.py
│       ├── text_processor.py         # 文本预处理
│       ├── image_processor.py        # 图片处理
│       └── validators.py             # 输入验证工具
│
├── data/                             # 数据目录
│   ├── raw/                          # 原始知识库文档（PDF、DOCX）
│   ├── processed/                    # 预处理后的数据
│   └── vectorstore/                  # Chroma 向量库持久化目录
│       └── chroma_db/
│
├── prompts/                          # Prompt 模板文件
│   ├── rag_prompt.txt                # RAG 问答 Prompt
│   ├── agent_prompt.txt              # 主动问诊 Prompt
│   └── multimodal_prompt.txt         # 多模态分析 Prompt
│
├── scripts/                          # 脚本工具
│   ├── init_vectorstore.py           # 初始化向量库（批量加载文档）
│   ├── test_api.py                   # API 测试脚本
│   └── benchmark.py                  # 性能基准测试
│
├── tests/                            # 测试代码
│   ├── __init__.py
│   ├── test_api/                     # API 端到端测试
│   │   ├── test_chat.py
│   │   └── test_multimodal.py
│   ├── test_services/                # 服务层单元测试
│   │   ├── test_rag_service.py
│   │   └── test_llm_service.py
│   └── test_rag/                     # RAG 组件测试
│       ├── test_embeddings.py
│       └── test_retriever.py
│
├── .env                              # 环境变量（已存在，包含 API Key）
├── .env.example                      # 环境变量示例（已存在）
├── .gitignore                        # Git 忽略文件
├── requirements.txt                  # Python 依赖（pip）
├── pyproject.toml                    # 项目元信息（可选，Poetry/Rye）
├── README.md                         # 项目说明文档
├── Dockerfile                        # Docker 镜像定义（后期容器化）
└── docker-compose.yml                # 多容器编排（可选）
```

---

## 📦 三、核心模块职责说明

### 3.1 API 层（`app/api/`）

**职责**: 接收 HTTP 请求，参数验证，调用服务层，返回响应

| 文件 | 功能 | 关键技术 |
|------|------|---------|
| `chat.py` | 单轮/多轮对话问答 | FastAPI Router，依赖注入 |
| `multimodal.py` | 图片上传与分析 | UploadFile，异步处理 |
| `agent.py` | 主动问诊流式对话 | Server-Sent Events (SSE) |
| `health.py` | 服务健康检查 | 返回版本、状态、依赖健康 |

**示例代码片段**:
```python
# app/api/v1/endpoints/chat.py
from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends()
):
    """基于 RAG 的智能问答"""
    result = await rag_service.answer_question(
        question=request.question,
        pet_profile=request.pet_profile  # 个性化宠物档案
    )
    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],  # 可追溯的知识来源
        confidence=result["confidence"]
    )
```

---

### 3.2 核心配置（`app/core/`）

**职责**: 统一管理配置、日志、安全策略

#### `config.py` - 基于 pydantic-settings 的配置管理

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 阿里百炼 API
    DASHSCOPE_API_KEY: str
    
    # 模型配置
    EMBEDDING_MODEL: str = "text-embedding-v3"
    LLM_MODEL: str = "qwen-plus"
    MULTIMODAL_MODEL: str = "qwen-vl-plus"
    
    # 向量库配置
    CHROMA_PERSIST_DIR: str = "./data/vectorstore/chroma_db"
    CHROMA_COLLECTION_NAME: str = "pet_health_knowledge"
    
    # RAG 参数
    RETRIEVAL_TOP_K: int = 5
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # API 配置
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "宠物健康问答系统"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

#### `logging.py` - 日志配置

```python
from loguru import logger
import sys

def setup_logging():
    logger.remove()  # 移除默认处理器
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 每天轮转
        retention="30 days",
        compression="zip"
    )
```

---

### 3.3 RAG 核心组件（`app/rag/`）

#### 3.3.1 嵌入模型封装（`embeddings.py`）

**职责**: 封装阿里 text-embedding-v3 API 调用

```python
from langchain.embeddings.base import Embeddings
import dashscope
from typing import List

class DashScopeEmbeddings(Embeddings):
    """阿里云 DashScope 嵌入模型封装"""
    
    def __init__(self, model: str = "text-embedding-v3"):
        self.model = model
        dashscope.api_key = settings.DASHSCOPE_API_KEY
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量文档嵌入"""
        response = dashscope.TextEmbedding.call(
            model=self.model,
            input=texts
        )
        return [item["embedding"] for item in response.output["embeddings"]]
    
    def embed_query(self, text: str) -> List[float]:
        """单个查询嵌入"""
        response = dashscope.TextEmbedding.call(
            model=self.model,
            input=text
        )
        return response.output["embeddings"][0]["embedding"]
```

#### 3.3.2 向量库管理（`vectorstore.py`）

**职责**: 管理 Chroma 向量库的初始化、持久化、检索

```python
from langchain.vectorstores import Chroma
from app.rag.embeddings import DashScopeEmbeddings
from app.core.config import settings

class VectorStoreManager:
    """向量库管理器"""
    
    def __init__(self):
        self.embeddings = DashScopeEmbeddings()
        self.vectorstore = None
    
    def initialize(self):
        """初始化或加载已有向量库"""
        self.vectorstore = Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR
        )
    
    def add_documents(self, documents):
        """批量添加文档"""
        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()
    
    def similarity_search(self, query: str, k: int = 5):
        """相似度检索"""
        return self.vectorstore.similarity_search(query, k=k)
```

#### 3.3.3 文档加载器（`document_loader.py`）

**职责**: 从不同格式（PDF、DOCX、TXT）加载兽医知识文档

```python
from langchain.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader
)
from pathlib import Path

class DocumentLoaderFactory:
    """文档加载器工厂"""
    
    @staticmethod
    def load(file_path: str):
        """根据文件类型自动选择加载器"""
        suffix = Path(file_path).suffix.lower()
        
        if suffix == ".pdf":
            return PyPDFLoader(file_path).load()
        elif suffix == ".docx":
            return Docx2txtLoader(file_path).load()
        elif suffix == ".txt":
            return TextLoader(file_path).load()
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")
```

#### 3.3.4 检索器（`retriever.py`）

**职责**: 封装检索策略，支持元数据过滤（如按宠物类型过滤）

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

class EnhancedRetriever:
    """增强检索器（支持上下文压缩）"""
    
    def __init__(self, vectorstore, llm):
        self.base_retriever = vectorstore.as_retriever(
            search_kwargs={"k": settings.RETRIEVAL_TOP_K}
        )
        # 可选：使用 LLM 压缩检索结果
        self.compressor = LLMChainExtractor.from_llm(llm)
    
    def retrieve(self, query: str, filters: dict = None):
        """检索相关文档"""
        if filters:
            # 添加元数据过滤（如 pet_type: "狗"）
            self.base_retriever.search_kwargs["filter"] = filters
        
        docs = self.base_retriever.get_relevant_documents(query)
        return docs
```

---

### 3.4 服务层（`app/services/`）

#### 3.4.1 RAG 服务（`rag_service.py`）

**职责**: 核心 RAG 流程编排（检索 → Prompt 构造 → LLM 调用）

```python
from app.rag.vectorstore import VectorStoreManager
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService

class RAGService:
    """RAG 检索增强生成服务"""
    
    def __init__(self):
        self.vector_manager = VectorStoreManager()
        self.vector_manager.initialize()
        self.llm_service = LLMService()
        self.prompt_service = PromptService()
    
    async def answer_question(
        self, 
        question: str, 
        pet_profile: dict = None
    ):
        """回答用户问题"""
        # 1. 向量检索相关知识
        docs = self.vector_manager.similarity_search(question, k=5)
        
        # 2. 构造 Prompt（注入宠物档案）
        prompt = self.prompt_service.build_rag_prompt(
            question=question,
            context_docs=docs,
            pet_profile=pet_profile
        )
        
        # 3. 调用 LLM 生成回答
        answer = await self.llm_service.generate(prompt)
        
        # 4. 返回结果（带来源）
        return {
            "answer": answer,
            "sources": [doc.metadata for doc in docs],
            "confidence": self._calculate_confidence(docs)
        }
    
    def _calculate_confidence(self, docs):
        """计算置信度（基于检索相似度）"""
        # 简化实现：取平均相似度
        return sum([doc.metadata.get("score", 0.5) for doc in docs]) / len(docs)
```

#### 3.4.2 LLM 服务（`llm_service.py`）

**职责**: 封装阿里百炼 LLM 调用（qwen-plus、qwen-max）

```python
import dashscope
from app.core.config import settings

class LLMService:
    """大语言模型调用服务"""
    
    def __init__(self, model: str = None):
        self.model = model or settings.LLM_MODEL
        dashscope.api_key = settings.DASHSCOPE_API_KEY
    
    async def generate(self, prompt: str, **kwargs):
        """生成回答"""
        response = dashscope.Generation.call(
            model=self.model,
            prompt=prompt,
            **kwargs
        )
        
        if response.status_code == 200:
            return response.output.text
        else:
            raise Exception(f"LLM 调用失败: {response.message}")
    
    async def stream_generate(self, prompt: str):
        """流式生成（用于主动问诊 Agent）"""
        responses = dashscope.Generation.call(
            model=self.model,
            prompt=prompt,
            stream=True
        )
        
        for response in responses:
            if response.status_code == 200:
                yield response.output.text
```

#### 3.4.3 多模态服务（`multimodal_service.py`）

**职责**: 图片分析（qwen-vl-plus）

```python
import dashscope
from app.core.config import settings

class MultimodalService:
    """多模态图片分析服务"""
    
    def __init__(self):
        self.model = settings.MULTIMODAL_MODEL
        dashscope.api_key = settings.DASHSCOPE_API_KEY
    
    async def analyze_image(self, image_url: str, question: str = "描述图片中的异常情况"):
        """分析宠物健康图片"""
        response = dashscope.MultiModalConversation.call(
            model=self.model,
            messages=[{
                "role": "user",
                "content": [
                    {"image": image_url},
                    {"text": question}
                ]
            }]
        )
        
        if response.status_code == 200:
            return {
                "description": response.output.choices[0].message.content,
                "confidence": 0.85  # 简化处理
            }
        else:
            raise Exception(f"多模态分析失败: {response.message}")
```

#### 3.4.4 Prompt 服务（`prompt_service.py`）

**职责**: 管理所有 Prompt 模板

```python
from pathlib import Path

class PromptService:
    """Prompt 模板管理服务"""
    
    def __init__(self):
        self.template_dir = Path("prompts")
    
    def build_rag_prompt(self, question: str, context_docs, pet_profile: dict = None):
        """构造 RAG 问答 Prompt"""
        # 读取模板
        template = self._load_template("rag_prompt.txt")
        
        # 拼接检索到的知识
        context = "\n\n".join([doc.page_content for doc in context_docs])
        
        # 注入宠物档案（个性化）
        pet_info = self._format_pet_profile(pet_profile) if pet_profile else ""
        
        # 填充模板
        prompt = template.format(
            pet_info=pet_info,
            context=context,
            question=question
        )
        return prompt
    
    def _load_template(self, filename: str):
        """加载模板文件"""
        with open(self.template_dir / filename, "r", encoding="utf-8") as f:
            return f.read()
    
    def _format_pet_profile(self, profile: dict):
        """格式化宠物档案"""
        return f"宠物信息：品种{profile.get('breed')}，年龄{profile.get('age')}岁，体重{profile.get('weight')}kg"
```

---

### 3.5 Agent 模块（`app/agents/`）

#### 主动问诊 Agent（`diagnosis_agent.py`）

**职责**: 实现多轮对话主动问诊（基于 LangChain Agent）

```python
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from app.services.llm_service import LLMService
from app.rag.vectorstore import VectorStoreManager

class DiagnosisAgent:
    """主动问诊 Agent（思维链推理）"""
    
    def __init__(self):
        self.llm = LLMService()
        self.vector_manager = VectorStoreManager()
        self.vector_manager.initialize()
        
        # 定义工具
        self.tools = [
            Tool(
                name="搜索知识库",
                func=self._search_knowledge,
                description="从兽医教材中搜索相关症状信息"
            ),
            Tool(
                name="追问用户",
                func=self._ask_follow_up,
                description="当信息不足时,主动追问关键细节"
            )
        ]
        
        # 对话记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 初始化 Agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent="conversational-react-description",
            memory=self.memory,
            verbose=True
        )
    
    def _search_knowledge(self, query: str):
        """搜索知识库工具"""
        docs = self.vector_manager.similarity_search(query, k=3)
        return "\n".join([doc.page_content for doc in docs])
    
    def _ask_follow_up(self, question: str):
        """追问工具（返回追问问题）"""
        return f"追问: {question}"
    
    async def chat(self, user_input: str):
        """与用户对话"""
        response = await self.agent.arun(user_input)
        return response
```

---

## 📋 四、核心依赖清单

### 4.1 `requirements.txt`

```txt
# Web 框架
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# LangChain 生态
langchain==0.1.4
langchain-community==0.0.16

# 阿里百炼 SDK
dashscope==1.14.1

# 向量数据库
chromadb==0.4.22

# 文档处理
pypdf==4.0.1
python-docx==1.1.0
python-multipart==0.0.6  # 文件上传

# 文本处理
jieba==0.42.1  # 中文分词（可选）

# 工具库
loguru==0.7.2  # 日志
python-dotenv==1.0.0  # 环境变量
httpx==0.26.0  # 异步 HTTP 客户端

# 测试
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0  # 测试客户端

# 可选：数据库（如需）
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9  # PostgreSQL

# 可选：任务队列
celery==5.3.6
redis==5.0.1
```

### 4.2 安装命令

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

## 🔗 五、功能与模块映射关系

| 项目介绍.md 中的功能 | 对应模块 | 核心技术 |
|---------------------|---------|---------|
| **功能1: 用户/宠物档案管理** | `app/services/prompt_service.py`<br>`app/schemas/pet.py` | 将宠物档案注入到 Prompt 中实现个性化 |
| **功能2: 基于 RAG 的智能问答** | `app/rag/`<br>`app/services/rag_service.py` | LangChain + Chroma + DashScope Embeddings + qwen-plus |
| **功能3: 多模态辅助诊断** | `app/services/multimodal_service.py`<br>`app/api/v1/endpoints/multimodal.py` | qwen-vl-plus 图片理解 |
| **功能4: 主动问诊 Agent** | `app/agents/diagnosis_agent.py` | LangChain Agent + ConversationBufferMemory + CoT |

---

## 🚀 六、快速启动指南

### 6.1 最小可运行版本（MVP）

**第一阶段目标**: 实现基础 RAG 问答功能

#### Step 1: 创建基础项目结构

```bash
mkdir -p app/{api/v1/endpoints,core,models,services,rag,schemas,utils}
mkdir -p data/{raw,processed,vectorstore}
mkdir -p prompts scripts tests
touch app/__init__.py app/main.py
```

#### Step 2: 实现核心文件

需要优先实现的文件（按顺序）：

1. ✅ `app/core/config.py` - 配置管理
2. ✅ `app/core/logging.py` - 日志配置
3. ✅ `app/rag/embeddings.py` - 嵌入模型
4. ✅ `app/rag/vectorstore.py` - 向量库管理
5. ✅ `app/services/llm_service.py` - LLM 调用
6. ✅ `app/services/rag_service.py` - RAG 服务
7. ✅ `app/api/v1/endpoints/chat.py` - 问答接口
8. ✅ `app/main.py` - 应用入口

#### Step 3: 初始化向量库

```python
# scripts/init_vectorstore.py
from app.rag.vectorstore import VectorStoreManager
from app.rag.document_loader import DocumentLoaderFactory
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 加载文档
docs = DocumentLoaderFactory.load("data/raw/兽医手册.pdf")

# 切分文档
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# 存入向量库
vector_manager = VectorStoreManager()
vector_manager.initialize()
vector_manager.add_documents(chunks)

print(f"✅ 成功添加 {len(chunks)} 个文档片段到向量库")
```

#### Step 4: 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问 API 文档
# http://localhost:8000/docs
```

### 6.2 测试 API

```bash
# 使用 curl 测试
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "狗狗呕吐可能是什么原因？",
    "pet_profile": {
      "breed": "金毛",
      "age": 3,
      "weight": 30
    }
  }'
```

---

## 📊 七、开发优先级建议

### P0 - 核心功能（第1-2周）

- [x] 项目结构搭建
- [ ] 配置管理与日志
- [ ] RAG 基础流程（embeddings + vectorstore + retriever）
- [ ] LLM 服务封装
- [ ] 单轮问答 API
- [ ] 初始化脚本（文档加载 + 向量化）

### P1 - 增强功能（第3-4周）

- [ ] 多轮对话支持（对话历史管理）
- [ ] 多模态图片分析接口
- [ ] Prompt 模板化管理
- [ ] 错误处理与日志完善
- [ ] 单元测试（核心服务）

### P2 - 高级功能（第5-6周）

- [ ] 主动问诊 Agent（LangChain Agent）
- [ ] 宠物档案个性化注入
- [ ] 流式响应（SSE）
- [ ] 性能优化（缓存、批处理）
- [ ] Docker 容器化

---

## ⚠️ 八、关键注意事项

### 8.1 安全与隐私（遵守 rule.md）

1. ❌ **禁止硬编码密钥**
   - 所有 API Key 必须从 `.env` 文件读取
   - `.env` 文件必须加入 `.gitignore`

2. ✅ **输入验证**
   - 使用 Pydantic 严格验证请求参数
   - 防止注入攻击（SQL 注入、Prompt 注入）

3. ✅ **医疗免责声明**
   - 所有回答必须包含"仅供参考，请咨询执业兽医"提示

### 8.2 RAG 质量保证

1. **文档质量**
   - 使用权威兽医教材（非网络爬虫数据）
   - 清洗噪声（页眉页脚、目录等）

2. **切分策略**
   - 推荐 `chunk_size=500, overlap=50`
   - 按语义单元切分（段落、章节）

3. **检索优化**
   - 初始 Top-K=5，根据效果调整
   - 考虑混合检索（向量 + 关键词）

### 8.3 成本控制

| 项目 | 预估成本 | 优化建议 |
|------|---------|---------|
| text-embedding-v3 | 0.0007元/千tokens | 批量嵌入（减少API调用） |
| qwen-plus | 0.004元/千tokens | 缓存高频问答 |
| qwen-vl-plus | 0.008元/千tokens | 图片压缩 + 采样检查 |

**开发阶段预算**: 约 100-300 元

---

## 📚 九、参考资源

### 9.1 官方文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangChain 官方文档](https://python.langchain.com/)
- [阿里百炼平台文档](https://help.aliyun.com/zh/dashscope/)
- [Chroma 向量数据库](https://docs.trychroma.com/)

### 9.2 最佳实践

- [FastAPI 项目结构最佳实践](https://github.com/tiangolo/full-stack-fastapi-template)
- [LangChain RAG 教程](https://python.langchain.com/docs/use_cases/question_answering/)
- [Pydantic Settings 使用指南](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

## 🎯 十、下一步行动

### 立即可执行的任务

1. ✅ **创建项目结构**
   ```bash
   python scripts/create_structure.py
   ```

2. ✅ **生成 requirements.txt**
   ```bash
   # 已在本文档第四节提供
   ```

3. ⬜ **实现核心配置模块**
   - 创建 `app/core/config.py`
   - 测试环境变量加载

4. ⬜ **实现嵌入模型封装**
   - 创建 `app/rag/embeddings.py`
   - 测试 API 连接

5. ⬜ **初始化向量库**
   - 准备1-2份测试文档
   - 运行 `scripts/init_vectorstore.py`

### 需要你提供的信息

- [ ] 兽医知识库文档来源（PDF/DOCX 文件路径）
- [ ] 是否需要与 Golang 后端集成（共享用户数据库）
- [ ] 是否需要 Docker 容器化部署

---

## 📝 附录：快速创建脚本

### A.1 自动创建项目结构脚本

```python
# scripts/create_project_structure.py
import os
from pathlib import Path

# 定义目录结构
DIRS = [
    "app/api/v1/endpoints",
    "app/core",
    "app/models",
    "app/services",
    "app/rag",
    "app/agents",
    "app/schemas",
    "app/db",
    "app/utils",
    "data/raw",
    "data/processed",
    "data/vectorstore/chroma_db",
    "prompts",
    "scripts",
    "tests/test_api",
    "tests/test_services",
    "tests/test_rag",
    "logs"
]

# 定义文件
FILES = [
    "app/__init__.py",
    "app/main.py",
    "app/api/__init__.py",
    "app/api/v1/__init__.py",
    "app/api/v1/endpoints/__init__.py",
    "app/api/v1/endpoints/chat.py",
    "app/api/v1/endpoints/multimodal.py",
    "app/api/v1/endpoints/agent.py",
    "app/api/v1/endpoints/health.py",
    "app/api/v1/router.py",
    "app/api/deps.py",
    "app/core/__init__.py",
    "app/core/config.py",
    "app/core/security.py",
    "app/core/logging.py",
    "app/models/__init__.py",
    "app/models/request.py",
    "app/models/response.py",
    "app/models/domain.py",
    "app/services/__init__.py",
    "app/services/rag_service.py",
    "app/services/llm_service.py",
    "app/services/multimodal_service.py",
    "app/services/agent_service.py",
    "app/services/prompt_service.py",
    "app/rag/__init__.py",
    "app/rag/embeddings.py",
    "app/rag/vectorstore.py",
    "app/rag/retriever.py",
    "app/rag/document_loader.py",
    "app/rag/text_splitter.py",
    "app/rag/chain.py",
    "app/agents/__init__.py",
    "app/agents/diagnosis_agent.py",
    "app/agents/tools.py",
    "app/agents/prompts.py",
    "app/schemas/__init__.py",
    "app/schemas/chat.py",
    "app/schemas/pet.py",
    "app/schemas/diagnosis.py",
    "app/db/__init__.py",
    "app/db/models.py",
    "app/utils/__init__.py",
    "app/utils/text_processor.py",
    "app/utils/image_processor.py",
    "app/utils/validators.py",
    "scripts/init_vectorstore.py",
    "scripts/test_api.py",
    "scripts/benchmark.py",
    "tests/__init__.py",
    "tests/test_api/__init__.py",
    "tests/test_services/__init__.py",
    "tests/test_rag/__init__.py",
    "prompts/rag_prompt.txt",
    "prompts/agent_prompt.txt",
    "prompts/multimodal_prompt.txt",
    ".gitignore",
    "README.md",
    "requirements.txt"
]

def create_structure():
    """创建项目结构"""
    base_dir = Path(__file__).parent.parent
    
    # 创建目录
    for dir_path in DIRS:
        (base_dir / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")
    
    # 创建文件
    for file_path in FILES:
        full_path = base_dir / file_path
        if not full_path.exists():
            full_path.touch()
            print(f"✅ 创建文件: {file_path}")
    
    print("\n🎉 项目结构创建完成！")

if __name__ == "__main__":
    create_structure()
```

### A.2 .gitignore 模板

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# 环境变量
.env
.env.local

# 数据文件
data/raw/*
data/processed/*
data/vectorstore/chroma_db/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# 日志
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# 测试
.pytest_cache/
.coverage
htmlcov/

# 打包
dist/
build/
*.egg-info/
```

---

**文档版本**: v1.0  
**最后更新**: 2026年1月16日  
**维护者**: AI 助手 (GitHub Copilot)
