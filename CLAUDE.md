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

**Phase 1**: Python 核心 AI 引擎原型验证 (RAG 问答流程) ✅ **已完成**

核心文件结构：
```
core-python/
├── app/
│   ├── api/v1/endpoints/    # API 路由
│   ├── core/                # 核心配置
│   ├── models/              # 数据模型
│   ├── rag/                 # RAG 组件
│   │   ├── document_loader.py  # 文档加载器（PDF/TXT/DOCX/CSV）
│   │   ├── embeddings.py       # Embedding 服务
│   │   ├── retriever.py        # 检索器（含置信度评分）
│   │   ├── text_splitter.py    # 文本分割
│   │   └── vectorstore.py       # Chroma 向量库管理
│   ├── services/             # 业务服务
│   │   ├── llm_service.py       # LLM 调用服务
│   │   └── rag_service.py       # RAG 问答服务（含 Fallback）
│   └── utils/                # 工具函数
├── data/
│   ├── raw/                  # 原始兽医知识库文档
│   │   ├── *.pdf              # 14本权威兽医教材
│   │   └── *.csv              # 192条专业问答数据
│   └── chroma_db/             # Chroma 向量数据库
├── prompts/                  # Prompt 模板
├── scripts/                  # 初始化脚本
│   ├── init_vectorstore.py   # 向量库初始化（支持 --rebuild）
│   └── test_rag.py           # RAG 测试脚本
├── venv/                     # Python 虚拟环境
└── requirements.txt
```

## 关键配置

**必需的环境变量**:
- `DASHSCOPE_API_KEY`: 阿里百炼平台密钥

**向量数据库**: Chroma (本地持久化, SQLite 后端)

**Embedding 模型**: DashScope text-embedding-v3 (API 调用)

**LLM 模型**: **qwen3.5-plus** (统一多模态模型，支持文本问答 + 图片分析)

## 开发命令

### core-python 模块

```bash
cd core-python

# 激活虚拟环境（重要！）
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化向量数据库（重建模式）
python scripts/init_vectorstore.py --rebuild

# 运行 RAG 测试
python scripts/test_rag.py

# 启动 FastAPI 服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API 文档
# http://localhost:8000/docs
```

## 已完成功能

### Phase 1: RAG 问答流程 ✅

1. **多格式文档加载**
   - PDF 文档加载（PyPDF）
   - TXT 文档加载
   - DOCX 文档加载
   - CSV 问答数据加载（支持多种列名格式）

2. **数据清洗**
   - 去除非打印字符
   - 规范化空白字符
   - 去除页眉页脚
   - PDF 特殊清洗（孤立字符、不完整行）

3. **来源置信度系统**
   - 根据文件名关键词推断来源类型
   - 置信度等级：权威手册(0.95) > 学术论文(0.85) > 官方网站(0.80) > 问答数据(0.65) > AI生成(0.40)
   - 综合评分公式：语义相似度 × 0.7 + 置信度 × 0.3

4. **内容去重**
   - 基于内容 Hash 去重
   - 避免重复文档影响检索质量

5. **Fallback 降级机制**
   - 知识库无相关内容时，使用通用知识回答
   - 明确告知用户知识库限制

6. **就医警示系统**
   - 自动识别危急症状关键词
   - 优先输出就医提示

### 知识库数据

**CSV 问答数据** (192 条):

| 文件 | 内容 | 条目 |
|------|------|------|
| 宠物常见疾病防治指南.csv | 犬猫疾病预防、症状、治疗 | 20条 |
| 宠物日常护理指南.csv | 喂养、护理、训练 | 17条 |
| 宠物疾病问答_政府资料.csv | 政府官方资料整理 | 10条 |
| 宠物急救与紧急情况处理.csv | 各类紧急情况处理 | 15条 |
| 犬猫常见疾病详解.csv | 疾病原因、治疗、预防 | 25条 |
| 宠物喂养与营养指南.csv | 科学喂养、营养均衡 | 20条 |
| 宠物行为与心理问题.csv | 行为问题纠正 | 20条 |
| 老年宠物与特殊护理.csv | 老年护理、临终关怀 | 20条 |
| 宠物美容与日常保健.csv | 美容、保健、体检 | 20条 |
| 常见宠物品种特性与护理.csv | 各种品种特性与护理 | 25条 |

**PDF 教材** (14 本):
- WSAVA犬猫免疫指导手册2015.pdf
- 兽医临床诊断学
- 兽医产科学
- 兽医传染病学（陈溥言、第六版）
- 兽医内科学第4版
- 兽医外科学
- 兽医外科手术学
- 兽医学
- 兽医寄生虫学
- 兽医生物制品学
- 兽医药理学
- 动物生理学
- 家畜病理学

**向量库规模**: 572 个文档 → 1121 个文本块

## 重要设计决策

### RAG 检索策略
- Top-K 相似度检索
- 支持按宠物类型、疾病类别等元数据过滤
- 检索结果与 Prompt 组合时包含安全警示
- 综合评分排序（语义相似度 + 来源置信度）

### 安全风控
- 识别宠物危急重症，优先输出就医警示
- 系统定位是**健康信息辅助与风险提示**，不替代执业兽医诊断

### 开发阶段技术选型
- 向量库: Chroma (生产可选 Qdrant/Milvus)
- 用户数据库: SQLite → PostgreSQL
- Embedding: DashScope text-embedding-v3 (API 调用)

## 项目阶段

- [x] ~~Phase 0~~: 需求分析与技术选型 ✅
- [x] **Phase 1**: Python 核心 AI 引擎 (RAG 问答流程) ✅
- [ ] **Phase 1.5**: 多模态扩展 (图片分析 qwen-vl-plus)
- [ ] **Phase 2**: Go 后端基础框架搭建
- [ ] **Phase 3**: 前端 MVP 版本开发
- [ ] **Phase 4**: 前后端联调与完整链路测试

## 注意事项

1. **必须使用虚拟环境**: 项目使用 `venv/Scripts/python.exe` 而非系统 Python
2. **依赖安装**: 首次运行需要安装 `langchain`, `langchain-community`, `langchain-chroma`, `dashscope`, `pypdf`
3. **API 密钥**: 需要配置 `DASHSCOPE_API_KEY` 环境变量
