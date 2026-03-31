# PetMind Go 后端服务

基于 Go + Gin 的宠物健康智能问答系统后端服务。

## 技术栈

| 技术 | 说明 |
|------|------|
| **框架** | Gin (高性能 HTTP Web 框架) |
| **ORM** | GORM (Go ORM 库) |
| **数据库** | SQLite (开发) / PostgreSQL (生产) |
| **认证** | JWT (JSON Web Token) |
| **AI 集成** | 调用 Python FastAPI AI 服务 |

## 项目结构

```
backend-go/
├── cmd/
│   └── server/
│       └── main.go              # 程序入口
├── internal/
│   ├── config/                  # 配置管理
│   │   └── config.go
│   ├── handler/                 # HTTP 处理函数
│   │   ├── auth_handler.go     # 认证
│   │   ├── pet_handler.go      # 宠物档案
│   │   ├── session_handler.go   # 会话
│   │   └── message_handler.go  # 消息
│   ├── middleware/             # 中间件
│   │   └── middleware.go       # CORS、JWT认证
│   ├── model/                  # 数据模型
│   │   └── models.go
│   ├── repository/             # 数据库操作
│   │   └── db.go
│   └── service/                # 业务逻辑
│       ├── auth_service.go
│       ├── pet_service.go
│       ├── session_service.go
│       ├── message_service.go
│       └── ai_service.go
├── pkg/
│   └── client/                  # 客户端
├── data/                        # 数据目录
│   ├── uploads/               # 上传文件
│   └── petmind.db             # SQLite 数据库
├── go.mod
└── go.sum
```

## API 接口

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |

### 宠物档案（需认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/pets` | 列出宠物列表 |
| POST | `/api/v1/pets` | 创建宠物 |
| GET | `/api/v1/pets/:id` | 获取宠物详情 |
| PUT | `/api/v1/pets/:id` | 更新宠物 |
| DELETE | `/api/v1/pets/:id` | 删除宠物 |

### 会话（需认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/sessions` | 列出会话列表 |
| POST | `/api/v1/sessions` | 创建会话 |
| GET | `/api/v1/sessions/:id` | 获取会话详情 |
| DELETE | `/api/v1/sessions/:id` | 删除会话 |

### 消息（需认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/messages/session/:session_id` | 获取会话消息 |
| POST | `/api/v1/messages` | 发送文本消息 |
| POST | `/api/v1/messages/image` | 发送图片消息 |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PETMIND_JWT_SECRET` | `your-secret-key-change-in-production` | JWT 密钥 |
| `PETMIND_DB_TYPE` | `sqlite` | 数据库类型 |
| `PETMIND_DB_PATH` | `./data/petmind.db` | SQLite 路径 |
| `PETMIND_DB_HOST` | `localhost` | PostgreSQL 主机 |
| `PETMIND_DB_PORT` | `5432` | PostgreSQL 端口 |
| `PETMIND_DB_USER` | `postgres` | PostgreSQL 用户 |
| `PETMIND_DB_PASSWORD` | `postgres` | PostgreSQL 密码 |
| `PETMIND_DB_NAME` | `petmind` | PostgreSQL 数据库名 |
| `PETMIND_AI_API_URL` | `http://localhost:8000/api/v1` | Python AI 服务地址 |
| `PETMIND_UPLOAD_DIR` | `./data/uploads` | 上传文件目录 |
| `PETMIND_PORT` | `8080` | 服务端口 |

## 配置文件

项目使用 [Viper](https://github.com/spf13/viper) 进行配置管理，支持多种配置方式。

### 配置文件路径（按优先级）

1. 当前目录 `./config.yaml`
2. `./config/config.yaml`
3. `/etc/petmind/config.yaml`

### config.yaml 示例

```yaml
# JWT 配置
jwt_secret: "your-secret-key-change-in-production"

# 数据库配置
db:
  type: "sqlite"
  path: "./data/petmind.db"

# AI 服务配置
ai:
  api_url: "http://localhost:8000/api/v1"

# 文件上传配置
upload:
  dir: "./data/uploads"

# 服务器配置
server:
  port: "8080"
```

### 配置优先级

```
环境变量 > 命令行参数 > config.yaml > 默认值
```

## 快速开始

### 1. 安装依赖

```bash
cd backend-go
go mod tidy
```

### 2. 运行服务

```bash
# 直接运行（使用默认配置）
go run cmd/server/main.go

# 或复制并编辑配置文件
cp .env.example .env
go run cmd/server/main.go
```

### 3. 运行

```bash
go run cmd/server/main.go
```

### 4. 测试 API

```bash
# 健康检查
curl http://localhost:8080/health

# 注册
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"123456"}'

# 登录
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'
```

## 数据库模型

### 用户 (users)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| username | VARCHAR | 用户名（唯一） |
| email | VARCHAR | 邮箱（唯一） |
| password | VARCHAR | 密码（加密） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 宠物 (pets)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| user_id | UUID | 所属用户 |
| name | VARCHAR | 宠物名称 |
| species | VARCHAR | 种类（狗/猫） |
| breed | VARCHAR | 品种 |
| age | VARCHAR | 年龄 |
| weight | VARCHAR | 体重 |
| gender | VARCHAR | 性别 |
| birthday | VARCHAR | 生日 |
| notes | TEXT | 备注 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 会话 (sessions)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| user_id | UUID | 所属用户 |
| pet_id | UUID | 关联宠物（可选） |
| title | VARCHAR | 会话标题 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 消息 (messages)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| session_id | UUID | 所属会话 |
| role | ENUM | user/assistant |
| content | TEXT | 消息内容 |
| image_urls | TEXT | 图片路径（JSON数组） |
| sources | TEXT | RAG来源（JSON数组） |
| created_at | TIMESTAMP | 创建时间 |

## 认证流程

1. 用户登录/注册获取 JWT token
2. 后续请求在 Header 中携带 `Authorization: Bearer <token>`
3. 后端验证 token 并提取 user_id

## TODO

- [x] AI 服务集成（调用 Python FastAPI） ✅
- [ ] WebSocket 支持（实时对话）
- [ ] Redis 缓存
- [ ] PostgreSQL 生产部署配置
- [ ] Docker 容器化
