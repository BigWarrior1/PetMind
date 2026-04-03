# 🐾 PetMind 宠物健康智能问答系统

PetMind 是一个基于 AI 大语言模型（LLM）与检索增强生成（RAG）技术的专业宠物医疗咨询辅助平台。旨在通过结合权威兽医知识库，为宠物主人提供比通用 AI 更准确、更可信的健康建议，减少"AI 幻觉"，引导用户及时联系执业兽医。

## ✨ 核心特性

- **RAG 检索增强**：基于 14 本权威兽医教材 + 192 条专业问答数据
- **来源可信**：每条回答附带引用来源和置信度评分
- **就医警示**：自动识别危急症状，优先输出就医提示
- **多模态支持**：支持图片上传，AI 可分析宠物照片
- **会话记忆**：支持多轮对话，自动压缩历史消息
- **流式响应**：实时流式输出，体验流畅

## 🏗️ 系统架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   用户浏览器  │────▶│  Vue 3 SPA  │────▶│   Go Gin   │
└─────────────┘     └─────────────┘     │   Gateway   │
                                        └──────┬──────┘
                                               │
                          ┌────────────────────┼────────────────────┐
                          │                    │                    │
                          ▼                    ▼                    ▼
                   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
                   │   SQLite    │     │  Python AI  │────▶│   阿里通义   │
                   │  用户数据   │     │  FastAPI   │     │   千问 LLM  │
                   └─────────────┘     └──────┬──────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  Chroma DB  │
                                        │  向量数据库  │
                                        └─────────────┘
```

## 📁 项目结构

```
PetMind/
├── backend-go/           # Go 后端服务
│   ├── cmd/server/      # 程序入口
│   ├── internal/       # 内部包
│   │   ├── config/     # 配置管理 (Viper + godotenv)
│   │   ├── handler/    # HTTP 处理器
│   │   ├── middleware/ # 中间件 (CORS/JWT)
│   │   ├── model/      # 数据模型
│   │   ├── repository/ # 数据访问层 (GORM)
│   │   ├── router/     # 路由配置
│   │   └── service/    # 业务逻辑
│   ├── .env            # 环境变量 (不提交)
│   └── config.yaml     # 配置文件
│
├── core-python/         # Python AI 服务
│   ├── app/
│   │   ├── api/        # FastAPI 路由
│   │   ├── rag/         # RAG 核心模块
│   │   └── services/    # AI 服务编排
│   ├── data/
│   │   ├── raw/         # 原始 PDF 文档
│   │   └── chroma_db/   # 向量数据库
│   └── .env             # 环境变量 (不提交)
│
├── frontend/             # Vue 3 前端
│   ├── src/
│   │   ├── api/         # Axios HTTP 客户端
│   │   ├── components/   # Vue 组件
│   │   ├── stores/       # Pinia 状态管理
│   │   └── views/       # 页面视图
│   └── .env.example     # 环境变量模板
│
├── check_env.sh          # 服务器环境检查脚本
└── README.md
```

## 🛠️ 技术栈

| 模块 | 技术 | 框架/库 |
|------|------|---------|
| 前端 | TypeScript, Vue 3 | Vite, Vue Router, Pinia, Axios, Element Plus |
| 后端 | Go | Gin, GORM, JWT (golang-jwt), godotenv |
| AI 服务 | Python | FastAPI, LangChain, Chroma, Uvicorn |
| 数据库 | SQLite (开发) / PostgreSQL (生产) | GORM |
| 向量数据库 | Chroma | bge-large-zh-v1.5 embedding |
| LLM | 阿里通义千问 (DashScope API) | qwen-plus, qwen-vl-plus |

## 📚 知识库

### PDF 教材 (14 本)

| 书名 | 说明 |
|------|------|
| WSAVA犬猫免疫指导手册 | 国际小动物兽医协会免疫指南 |
| 兽医内科学第4版 | 犬猫内科疾病权威教材 |
| 兽医外科学 | 外科手术基础 |
| 兽医临床诊断学 | 诊断方法与流程 |
| 兽医传染病学 | 传染病防控 |
| 兽医药理学 | 药物作用与使用 |
| ... | ... |

### 问答数据 (192 条)

涵盖：疾病防治、日常护理、急救处理、营养喂养、行为问题、老年护理、美容保健、品种特性等。

## 🚀 快速开始

### 环境要求

- Go >= 1.21
- Python >= 3.9
- Node.js >= 18
- Git

或者直接运行 `check_env.sh` 自动检查和安装：

```bash
sudo bash check_env.sh
```

### 1. 克隆项目

```bash
git clone <repository-url>
cd PetMind
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp backend-go/.env.example backend-go/.env
cp core-python/.env.example core-python/.env

# 编辑 backend-go/.env，修改 JWT_SECRET
# 编辑 core-python/.env，配置 DASHSCOPE_API_KEY
```

### 3. 启动后端 (Go)

```bash
cd backend-go
go run ./cmd/server
# 服务运行在 http://localhost:8080
```

### 4. 启动 AI 服务 (Python)

```bash
cd core-python

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化向量数据库（首次运行）
python scripts/init_vectorstore.py --rebuild

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 启动前端 (Vue)

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev
# 访问 http://localhost:5173

# 或生产构建
npm run build
```

## 🔧 配置说明

### 后端配置 (backend-go/.env)

| 变量 | 说明 | 默认值 |
|------|------|--------|
| PETMIND_JWT_SECRET | JWT 密钥 | 必须修改 |
| PETMIND_DB_TYPE | 数据库类型 | sqlite |
| PETMIND_DB_PATH | SQLite 路径 | ./data/petmind.db |
| PETMIND_AI_API_URL | AI 服务地址 | http://localhost:8000/api/v1 |
| PETMIND_PORT | 服务端口 | 8080 |

### AI 服务配置 (core-python/.env)

| 变量 | 说明 |
|------|------|
| DASHSCOPE_API_KEY | 阿里百炼 API 密钥（必填） |

## 📡 API 路由

### 后端 (8080)

```
POST   /api/v1/auth/register    # 用户注册
POST   /api/v1/auth/login       # 用户登录
GET    /api/v1/pets             # 获取宠物列表
POST   /api/v1/pets             # 创建宠物
GET    /api/v1/pets/:id         # 获取宠物详情
PUT    /api/v1/pets/:id         # 更新宠物
DELETE /api/v1/pets/:id         # 删除宠物
GET    /api/v1/sessions         # 获取会话列表
POST   /api/v1/sessions         # 创建会话
GET    /api/v1/sessions/:id     # 获取会话详情
DELETE /api/v1/sessions/:id     # 删除会话
GET    /api/v1/messages/session/:session_id  # 获取会话消息
POST   /api/v1/messages         # 发送消息
POST   /api/v1/messages/stream  # 流式发送消息
POST   /api/v1/messages/image   # 上传图片
GET    /health                  # 健康检查
```

### AI 服务 (8000)

```
POST   /api/v1/chat       # 聊天接口
POST   /api/v1/multimodal # 多模态接口
GET    /health            # 健康检查
```

## 🔒 安全说明

- JWT 密钥请使用强随机字符串
- 生产环境务必修改默认配置
- AI 回答仅供参考，不替代执业兽医诊断
- 危急症状会自动提醒用户及时就医

## 📄 许可证

MIT License

## 🙏 致谢

本项目的知识库基于以下权威资料构建：
- WSAVA (World Small Animal Veterinary Association) 指南
- 国内权威兽医教材
- 专业宠物养护资料
