# PetMind Go 后端服务

基于 Go + Gin 的宠物健康智能问答系统后端服务。

## 技术栈

| 技术 | 说明 |
|------|------|
| **框架** | Gin (高性能 HTTP Web 框架) |
| **ORM** | GORM (Go ORM 库) |
| **数据库** | PostgreSQL (生产) / SQLite (开发) |
| **认证** | JWT (JSON Web Token) |
| **AI 集成** | 调用 Python FastAPI AI 服务 |

## 项目结构

```
backend-go/
├── cmd/server/
│   └── main.go              # 程序入口
├── internal/
│   ├── config/              # 配置管理
│   │   └── config.go
│   ├── handler/             # HTTP 处理函数
│   │   ├── auth_handler.go     # 认证
│   │   ├── pet_handler.go      # 宠物档案
│   │   ├── session_handler.go   # 会话
│   │   ├── message_handler.go   # 消息
│   │   └── admin_handler.go    # 管理员接口
│   ├── middleware/           # 中间件
│   │   └── middleware.go       # CORS、JWT认证、AdminAuth
│   ├── model/                # 数据模型
│   │   └── models.go
│   ├── repository/           # 数据库操作
│   │   ├── db.go
│   │   ├── user_repository.go
│   │   ├── pet_repository.go
│   │   ├── session_repository.go
│   │   ├── message_repository.go
│   │   └── admin_repository.go
│   └── service/             # 业务逻辑
│       ├── auth_service.go
│       ├── pet_service.go
│       ├── session_service.go
│       ├── message_service.go
│       └── ai_service.go
├── .env                      # 环境变量 (不提交)
├── config.yaml               # 配置文件
├── go.mod
└── go.sum
```

## API 接口

### 认证接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/auth/register` | 普通用户注册 | 否 |
| POST | `/api/v1/auth/login` | 普通用户登录 | 否 |
| POST | `/api/v1/admin/register` | 管理员注册 | 否 (需密钥) |
| POST | `/api/v1/admin/login` | 管理员登录 | 否 |

### 用户认证接口

#### 注册用户
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456"
}
```

**响应 (201):**
```json
{
  "message": "注册成功",
  "user": {
    "id": "uuid",
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "created_at": "2026-04-13T10:00:00Z"
  }
}
```

#### 用户登录
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "123456"
}
```

**响应 (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "username": "testuser",
    "email": "test@example.com",
    "role": "user"
  }
}
```

### 管理员认证接口

#### 注册管理员
```bash
POST /api/v1/admin/register
Content-Type: application/json

{
  "username": "adminuser",
  "email": "admin@example.com",
  "password": "123456",
  "admin_secret": "你的管理员密钥"
}
```

**响应 (201):**
```json
{
  "message": "管理员注册成功",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "username": "adminuser",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

#### 管理员登录
```bash
POST /api/v1/admin/login
Content-Type: application/json

{
  "username": "adminuser",
  "password": "123456"
}
```

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
| POST | `/api/v1/messages` | 发送消息 |
| POST | `/api/v1/messages/stream` | 流式发送消息 |
| POST | `/api/v1/messages/image` | 发送图片 |

### 管理员接口（需管理员认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/stats` | 统计数据 |
| GET | `/api/v1/admin/users` | 用户列表(分页) |
| DELETE | `/api/v1/admin/users/:id` | 删除用户(含级联) |
| GET | `/api/v1/admin/pets` | 宠物列表(分页) |
| DELETE | `/api/v1/admin/pets/:id` | 删除宠物(含级联) |
| GET | `/api/v1/admin/sessions` | 会话列表(分页) |
| GET | `/api/v1/admin/sessions/:id/messages` | 会话消息详情 |
| DELETE | `/api/v1/admin/sessions/:id` | 删除会话(含级联) |

#### 管理员统计接口
```bash
GET /api/v1/admin/stats
Authorization: Bearer <admin_token>
```

**响应 (200):**
```json
{
  "users": 10,
  "pets": 25,
  "sessions": 50,
  "messages": 200
}
```

#### 用户列表(分页)
```bash
GET /api/v1/admin/users?page=1&page_size=20
Authorization: Bearer <admin_token>
```

**响应 (200):**
```json
{
  "data": [
    {
      "id": "uuid",
      "username": "testuser",
      "email": "test@example.com",
      "role": "user",
      "created_at": "2026-04-13T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

### 健康检查

```bash
GET /health
```

**响应 (200):**
```json
{
  "status": "ok"
}
```

## 错误码

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 (token无效或过期) |
| 403 | 禁止访问 (需要管理员权限) |
| 404 | 资源不存在 |
| 409 | 冲突 (如用户名/邮箱已存在) |
| 500 | 服务器内部错误 |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PETMIND_JWT_SECRET` | - | JWT 密钥 (必填) |
| `PETMIND_DB_TYPE` | `postgres` | 数据库类型 |
| `PETMIND_DB_HOST` | `localhost` | PostgreSQL 主机 |
| `PETMIND_DB_PORT` | `5432` | PostgreSQL 端口 |
| `PETMIND_DB_USER` | `postgres` | PostgreSQL 用户 |
| `PETMIND_DB_PASSWORD` | - | PostgreSQL 密码 |
| `PETMIND_DB_NAME` | `petmind` | 数据库名 |
| `PETMIND_AI_API_URL` | `http://localhost:8000/api/v1` | Python AI 服务地址 |
| `PETMIND_UPLOAD_DIR` | `./data/uploads` | 上传文件目录 |
| `PETMIND_PORT` | `8080` | 服务端口 |
| `PETMIND_ADMIN_SECRET` | - | 管理员注册密钥 (必填) |

## 配置文件

项目使用 [Viper](https://github.com/spf13/viper) 进行配置管理。

### config.yaml 示例

```yaml
# JWT 配置
jwt_secret: "your-secret-key-change-in-production"

# 数据库配置
db_type: "postgres"
db_host: "localhost"
db_port: "5432"
db_user: "postgres"
db_password: "your-password"
db_name: "petmind"

# AI 服务配置
ai_api_url: "http://localhost:8000/api/v1"

# 文件上传配置
upload_dir: "./data/uploads"

# 服务器配置
port: "8080"

# 管理员配置
admin_secret: "your-admin-secret-key"
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

### 2. 配置 PostgreSQL

```sql
CREATE DATABASE petmind;
```

### 3. 复制环境变量

```bash
cp .env.example .env
# 编辑 .env 填入配置
```

### 4. 运行服务

```bash
go run cmd/server/main.go
```

### 5. 测试 API

```bash
# 健康检查
curl http://localhost:8080/health

# 注册管理员
curl -X POST http://localhost:8080/api/v1/admin/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"123456","admin_secret":"你的密钥"}'

# 管理员登录
curl -X POST http://localhost:8080/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 获取统计数据 (需admin token)
curl http://localhost:8080/api/v1/admin/stats \
  -H "Authorization: Bearer <admin_token>"
```

## 认证流程

1. 用户/管理员登录获取 JWT token
2. 后续请求在 Header 中携带 `Authorization: Bearer <token>`
3. 后端验证 token 并提取 user_id 和 role

## 数据库模型

### 用户 (users)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| username | VARCHAR | 用户名（唯一） |
| email | VARCHAR | 邮箱（唯一） |
| password | VARCHAR | 密码（BCrypt加密） |
| role | VARCHAR | 角色: user / admin |
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
| summary | TEXT | 会话摘要 |
| summary_updated_at | TIMESTAMP | 摘要更新时间 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 消息 (messages)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| session_id | UUID | 所属会话 |
| role | VARCHAR | user / assistant |
| content | TEXT | 消息内容 |
| image_urls | TEXT | 图片路径（JSON数组） |
| sources | TEXT | RAG来源（JSON数组） |
| created_at | TIMESTAMP | 创建时间 |

## TODO

- [x] AI 服务集成（调用 Python FastAPI） ✅
- [x] 管理员后台接口 ✅
- [x] PostgreSQL 支持 ✅
- [ ] WebSocket 支持（实时对话）
- [ ] Docker 容器化
