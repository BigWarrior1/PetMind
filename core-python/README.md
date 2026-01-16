# PetMind Core - 智能推理引擎

这是 **PetMind** 项目的核心 AI 微服务模块，负责处理所有的自然语言理解与生成任务。它作为一个独立的服务运行，通过 API 为上层业务（Go Backend）提供智能支持。

## 📋 模块简介

该模块专注于基于大语言模型（LLM）和检索增强生成（RAG）技术的逻辑实现，不包含用户鉴权等通用业务逻辑。主要特点：

- 🤖 **智能问答**：基于阿里百炼 qwen-plus 大模型
- 📚 **知识增强**：RAG 技术确保答案基于权威兽医资料
- 🎯 **可追溯性**：每个答案都标注知识来源
- ⚠️ **安全提示**：自动识别紧急症状并建议就医
- 🐕 **个性化**：支持宠物档案信息，提供定制化建议

## 🏗️ 技术架构

- **Web 框架**：FastAPI
- **LLM**：阿里百炼 qwen-plus
- **嵌入模型**：阿里 text-embedding-v3
- **向量数据库**：Chroma
- **LLM 编排**：LangChain
- **日志**：Loguru
- **配置管理**：Pydantic Settings

## 📁 项目结构

```
python_api/
├── app/                    # 核心应用代码
│   ├── api/               # API 路由
│   │   └── v1/
│   │       ├── endpoints/ # 端点实现
│   │       └── router.py  # 路由聚合
│   ├── core/              # 核心配置
│   │   ├── config.py      # 配置管理
│   │   └── logging.py     # 日志配置
│   ├── models/            # 数据模型
│   │   ├── request.py     # 请求模型
│   │   └── response.py    # 响应模型
│   ├── rag/               # RAG 组件
│   │   ├── embeddings.py  # 嵌入模型
│   │   ├── vectorstore.py # 向量库管理
│   │   ├── document_loader.py # 文档加载
│   │   ├── text_splitter.py   # 文本切分
│   │   └── retriever.py   # 检索器
│   ├── services/          # 业务逻辑
│   │   ├── llm_service.py # LLM 服务
│   │   └── rag_service.py # RAG 服务
│   └── main.py            # 应用入口
├── data/                  # 数据目录
│   ├── raw/              # 原始文档
│   └── vectorstore/      # 向量库
├── prompts/              # Prompt 模板
├── scripts/              # 工具脚本
│   ├── init_vectorstore.py # 初始化向量库
│   └── test_rag.py       # 测试脚本
├── .env                  # 环境变量
├── requirements.txt      # 依赖列表
└── README.md            # 项目文档
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- 阿里百炼 API 密钥

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

项目根目录的 `.env` 文件已包含配置模板，请确保 `DASHSCOPE_API_KEY` 已设置：

```env
DASHSCOPE_API_KEY=sk-你的API密钥
```

### 4. 初始化向量数据库

```bash
# 加载知识库文档并建立向量索引
python scripts/init_vectorstore.py

# 如果需要清空现有数据重新初始化
python scripts/init_vectorstore.py --clean
```

**说明**：
- 默认加载 `data/raw/` 目录下的所有 `.txt` 文件
- 已包含 3 个测试文档：犬瘟热防治指南、猫传腹防治手册、宠物疫苗接种指南
- 初始化过程需要调用阿里 API 生成嵌入向量，可能需要几分钟

### 5. 启动服务

```bash
# 方式 1：使用 uvicorn 直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式 2：运行 main.py
python app/main.py
```

### 6. 访问 API 文档

服务启动后，访问以下地址：

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc
- **健康检查**：http://localhost:8000/api/v1/health

## 📖 API 使用示例

### 基础问答

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "狗狗出现高烧和咳嗽怎么办？"
  }'
```

### 带宠物档案的个性化问答

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "我家狗狗需要打哪些疫苗？",
    "pet_profile": {
      "species": "犬",
      "breed": "金毛",
      "age": 0.5,
      "weight": 5
    }
  }'
```

### Python 客户端示例

```python
import httpx

async def ask_question(question: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/chat",
            json={"question": question}
        )
        result = response.json()
        
        print(f"问题: {question}")
        print(f"\n回答:\n{result['answer']}")
        print(f"\n置信度: {result['confidence']:.2f}")
        print(f"\n知识来源:")
        for source in result['sources']:
            print(f"  - {source['source']}")
        print(f"\n{result['warning']}")

# 使用
import asyncio
asyncio.run(ask_question("幼猫什么时候开始打疫苗？"))
```

## 🧪 测试

### 测试 RAG 功能

```bash
python scripts/test_rag.py
```

该脚本会测试多个问题，输出答案、置信度和知识来源。

### 健康检查

```bash
curl http://localhost:8000/api/v1/health
```

返回示例：
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "vectorstore_count": 156
}
```

## 📝 添加自定义知识库

1. 将权威的宠物健康文档（TXT 格式）放入 `data/raw/` 目录
2. 运行初始化脚本重新构建向量库：

```bash
python scripts/init_vectorstore.py --clean
```

**文档要求**：
- 格式：TXT、PDF、Markdown
- 内容：权威、准确的兽医知识
- 建议：每个文档聚焦一个主题，便于检索

## ⚙️ 配置说明

主要配置项在 `.env` 文件中：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里百炼 API 密钥 | 必填 |
| `LLM_MODEL` | LLM 模型名称 | qwen-plus |
| `EMBEDDING_MODEL` | 嵌入模型名称 | text-embedding-v3 |
| `CHROMA_PERSIST_DIR` | 向量库持久化目录 | ./data/vectorstore/chroma_db |
| `API_PORT` | 服务端口 | 8000 |
| `LOG_LEVEL` | 日志级别 | INFO |
| `CHUNK_SIZE` | 文档切分大小 | 500 |
| `RETRIEVER_K` | 检索文档数量 | 5 |

## 🔧 开发指南

### 添加新的 API 端点

1. 在 `app/api/v1/endpoints/` 创建新文件
2. 定义路由和处理函数
3. 在 `app/api/v1/router.py` 中注册路由

### 自定义 Prompt 模板

编辑 `prompts/rag_prompt.txt` 文件，使用以下占位符：

- `{context}`：检索到的知识库内容
- `{question}`：用户问题
- `{pet_profile}`：宠物档案信息

### 日志查看

日志存储在 `logs/` 目录：
- 控制台：彩色实时输出
- 文件：`logs/app_YYYY-MM-DD.log`

## 🐛 常见问题

### 1. 导入错误"无法解析导入"

**原因**：依赖包未安装  
**解决**：`pip install -r requirements.txt`

### 2. 向量库初始化失败

**原因**：API 密钥未配置或网络问题  
**解决**：
- 检查 `.env` 文件中的 `DASHSCOPE_API_KEY`
- 确保网络可以访问阿里云服务

### 3. 回答质量不佳

**原因**：知识库内容不足或检索参数不合适  
**解决**：
- 增加更多高质量的知识库文档
- 调整 `CHUNK_SIZE` 和 `RETRIEVER_K` 参数
- 优化 Prompt 模板

### 4. API 调用超时

**原因**：LLM 生成速度慢或网络延迟  
**解决**：
- 使用更快的模型（如 qwen-turbo）
- 调整 `LLM_MAX_TOKENS` 减少生成长度

## 📄 许可证

本项目仅供学习和研究使用。

## ⚠️ 免责声明

本系统提供的信息仅供参考，不能替代执业兽医的专业诊断和治疗。遇到宠物健康问题，请及时咨询专业兽医。

## 🙏 致谢

- 阿里云百炼平台提供 LLM 和嵌入模型服务
- LangChain 提供 RAG 框架支持
- FastAPI 提供高性能 Web 框架

---

**联系方式**  
如有问题或建议，欢迎提交 Issue。

**开发状态**  
当前版本：v0.1.0（MVP 阶段）  
下一步计划：多模态图片分析、主动问诊 Agent
