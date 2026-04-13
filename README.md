# 🐾 PetMind 宠物健康智能问答系统

PetMind 是一个基于 AI 大语言模型（LLM）与检索增强生成（RAG）技术的专业宠物医疗咨询辅助平台。旨在通过结合权威兽医知识库，为宠物主人提供比通用 AI 更准确、更可信的健康建议，减少"AI 幻觉"，引导用户及时联系执业兽医。

## ✨ 核心特性

- **RAG 检索增强**：基于 14 本权威兽医教材 + 192 条专业问答数据
- **来源可信**：每条回答附带引用来源和置信度评分
- **就医警示**：自动识别危急症状，优先输出就医提示
- **多模态支持**：支持图片上传，AI 可分析宠物照片
- **会话记忆**：支持多轮对话，自动压缩历史消息
- **流式响应**：实时流式输出，体验流畅
- **后台管理**：管理员可管理用户、宠物、会话数据

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                           用户浏览器                                  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Vue 3 Frontend (5173)                       │
│   用户端: / (问答) /pets (宠物)     管理端: /admin/* (后台管理)     │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTP REST API
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Go Gin Backend (8080)                          │
│                    GORM + PostgreSQL                                │
│   用户认证: /api/v1/auth/*     管理员: /api/v1/admin/*            │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTP POST /chat
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Python FastAPI AI 服务 (8000)                     │
│                  LangChain + Chroma 向量数据库                        │
│                           │                                         │
│                           ▼                                         │
│              ┌─────────────────────────────┐                         │
│              │     阿里通义千问 LLM      │                         │
│              │   qwen-plus / qwen-vl-plus │                        │
│              └─────────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
PetMind/
├── backend-go/           # Go 后端服务
│   ├── cmd/server/      # 程序入口
│   ├── internal/       # 内部包
│   │   ├── config/     # 配置管理 (Viper + godotenv)
│   │   ├── handler/    # HTTP 处理器
│   │   ├── middleware/ # 中间件 (CORS/JWT/AdminAuth)
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
│   │   ├── layouts/     # 布局组件
│   │   ├── stores/       # Pinia 状态管理
│   │   └── views/       # 页面视图
│   │       └── admin/    # 管理后台页面
│   └── .env.example     # 环境变量模板
│
├── learn-doc/           # 项目文档
├── check_env.sh          # 服务器环境检查脚本
└── README.md
```

## 🛠️ 技术栈

| 模块 | 技术 | 框架/库 |
|------|------|---------|
| 前端 | TypeScript, Vue 3 | Vite, Vue Router, Pinia, Axios, Element Plus |
| 后端 | Go | Gin, GORM, JWT (golang-jwt), godotenv |
| 数据库 | PostgreSQL | GORM |
| AI 服务 | Python | FastAPI, LangChain, Chroma, Uvicorn |
| 向量数据库 | Chroma (本地 SQLite) | bge-large-zh-v1.5 embedding |
| LLM | 阿里通义千问 (DashScope API) | qwen-plus, qwen-vl-plus |

## 🚀 快速开始

### 环境要求

- Go >= 1.21
- Python >= 3.9
- Node.js >= 18
- PostgreSQL >= 13
- Git

### 1. 克隆项目

```bash
git clone <repository-url>
cd PetMind
```

### 2. 配置 PostgreSQL 数据库

```sql
-- 创建数据库
CREATE DATABASE petmind;
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp backend-go/.env.example backend-go/.env
cp core-python/.env_example core-python/.env

# 编辑 backend-go/.env，配置以下必填项：
#   PETMIND_DB_TYPE=postgres
#   PETMIND_DB_HOST=localhost
#   PETMIND_DB_PORT=5432
#   PETMIND_DB_USER=postgres
#   PETMIND_DB_PASSWORD=你的密码
#   PETMIND_DB_NAME=petmind
#   PETMIND_ADMIN_SECRET=你的管理员密钥
```

### 4. 一键启动

Windows 用户双击 `start.ps1` 或在 PowerShell 中运行：

```powershell
.\start.ps1
```

### 5. 手动启动

```bash
# 终端 1: 启动 AI 服务 (Python)
cd core-python
.\venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端 2: 启动后端 (Go)
cd backend-go
go run cmd/server/main.go

# 终端 3: 启动前端 (Vue)
cd frontend
npm run dev
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端 (用户端) | http://localhost:5173 |
| 管理后台 | http://localhost:5173/admin/login |
| AI 服务文档 | http://localhost:8000/docs |
| 后端健康检查 | http://localhost:8080/health |

## 📡 API 路由

### 后端接口 (8080)

#### 用户认证
```
POST   /api/v1/auth/register     # 普通用户注册
POST   /api/v1/auth/login      # 普通用户登录
POST   /api/v1/admin/register   # 管理员注册 (需密钥)
POST   /api/v1/admin/login     # 管理员登录
```

#### 宠物管理 (需认证)
```
GET    /api/v1/pets             # 获取宠物列表
POST   /api/v1/pets             # 创建宠物
GET    /api/v1/pets/:id         # 获取宠物详情
PUT    /api/v1/pets/:id         # 更新宠物
DELETE /api/v1/pets/:id         # 删除宠物
```

#### 会话管理 (需认证)
```
GET    /api/v1/sessions         # 获取会话列表
POST   /api/v1/sessions          # 创建会话
GET    /api/v1/sessions/:id      # 获取会话详情
DELETE /api/v1/sessions/:id      # 删除会话
```

#### 消息管理 (需认证)
```
GET    /api/v1/messages/session/:session_id   # 获取会话消息
POST   /api/v1/messages                        # 发送消息
POST   /api/v1/messages/stream                  # 流式发送消息
POST   /api/v1/messages/image                  # 上传图片分析
```

#### 管理员接口 (需管理员认证)
```
GET    /api/v1/admin/stats              # 统计信息
GET    /api/v1/admin/users             # 用户列表
DELETE /api/v1/admin/users/:id         # 删除用户
GET    /api/v1/admin/pets              # 宠物列表
DELETE /api/v1/admin/pets/:id         # 删除宠物
GET    /api/v1/admin/sessions          # 会话列表
GET    /api/v1/admin/sessions/:id/messages  # 会话消息详情
DELETE /api/v1/admin/sessions/:id     # 删除会话
```

#### 健康检查
```
GET    /health                         # 后端健康检查
```

### AI 服务 (8000)

```
POST   /api/v1/chat           # 聊天接口
POST   /api/v1/chat/stream    # 流式聊天
POST   /api/v1/analyze/image   # 图片分析
POST   /api/v1/summarize      # 摘要生成
POST   /api/v1/generate_title  # 标题生成
GET    /health                 # AI 服务健康检查
```

## 🔧 配置说明

### 后端配置 (backend-go/.env)

| 变量 | 说明 | 默认值 |
|------|------|--------|
| PETMIND_JWT_SECRET | JWT 密钥 | 必须修改 |
| PETMIND_DB_TYPE | 数据库类型 | postgres |
| PETMIND_DB_HOST | PostgreSQL 主机 | localhost |
| PETMIND_DB_PORT | PostgreSQL 端口 | 5432 |
| PETMIND_DB_USER | PostgreSQL 用户 | postgres |
| PETMIND_DB_PASSWORD | PostgreSQL 密码 | - |
| PETMIND_DB_NAME | 数据库名 | petmind |
| PETMIND_AI_API_URL | AI 服务地址 | http://localhost:8000/api/v1 |
| PETMIND_ADMIN_SECRET | 管理员注册密钥 | - |
| PETMIND_PORT | 服务端口 | 8080 |

### AI 服务配置 (core-python/.env)

| 变量 | 说明 |
|------|------|
| DASHSCOPE_API_KEY | 阿里百炼 API 密钥（必填） |
| POSTGRES_HOST | PostgreSQL 主机 |
| POSTGRES_PORT | PostgreSQL 端口 |
| POSTGRES_USER | PostgreSQL 用户 |
| POSTGRES_PASSWORD | PostgreSQL 密码 |
| POSTGRES_DB | 数据库名 |

## 🔐 管理员说明

### 注册管理员

1. 访问 http://localhost:5173/admin/register
2. 填写用户名、邮箱、密码
3. 输入管理员密钥（默认在 config.yaml 中配置）
4. 点击注册，自动登录管理后台

### 管理员功能

- **仪表板**: 查看用户数、宠物数、会话数、消息数统计
- **用户管理**: 查看所有用户、删除用户（含级联删除宠物/会话/消息）
- **宠物管理**: 查看所有宠物、删除宠物（含级联删除会话/消息）
- **会话管理**: 查看所有会话、查看会话消息详情、删除会话（含级联删除消息）

## 📚 知识库

### PDF 教材 (14 本)

涵盖：WSAVA犬猫免疫指导手册、兽医内科学、兽医外科学、兽医临床诊断学、兽医传染病学、兽医药理学等。

### 问答数据 (192 条)

涵盖：疾病防治、日常护理、急救处理、营养喂养、行为问题、老年护理、美容保健、品种特性等。

## 🔒 安全说明

- JWT 密钥请使用强随机字符串
- 生产环境务必修改默认配置
- 管理员密钥请妥善保管
- AI 回答仅供参考，不替代执业兽医诊断
- 危急症状会自动提醒用户及时就医

## 📄 许可证

MIT License

## 🙏 致谢

本项目的知识库基于以下权威资料构建：
- WSAVA (World Small Animal Veterinary Association) 指南
- 国内权威兽医教材
- 专业宠物养护资料
