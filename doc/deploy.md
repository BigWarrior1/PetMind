# PetMind 部署文档

## 目录

- [环境要求](#环境要求)
- [PostgreSQL 安装与配置](#postgresql-安装与配置)
- [服务启动顺序](#服务启动顺序)
- [环境变量说明](#环境变量说明)
- [Windows 部署](#windows-部署)
- [Linux 部署](#linux-部署)
- [故障排查](#故障排查)

---

## 环境要求

| 软件 | 最低版本 | 说明 |
|------|----------|------|
| Go | 1.21+ | Go 后端服务 |
| Python | 3.9+ | AI 服务 |
| Node.js | 18+ | 前端构建 |
| PostgreSQL | 13+ | 主数据库 |
| Git | 2.x+ | 代码管理 |

---

## PostgreSQL 安装与配置

### Windows 安装

1. 从 [PostgreSQL 官网](https://www.postgresql.org/download/windows/) 下载安装包
2. 安装时记录端口（默认 5432）和 postgres 用户密码
3. 安装完成后通过 pgAdmin 或 psql 创建数据库：

```sql
-- 连接 PostgreSQL
psql -U postgres

-- 创建数据库
CREATE DATABASE petmind;

-- 验证创建成功
\l
```

### Linux (Ubuntu/Debian) 安装

```bash
# 安装 PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 切换到 postgres 用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE petmind;
ALTER USER postgres WITH PASSWORD 'your_password';
\q
```

### Linux (CentOS/RHEL) 安装

```bash
# 安装 PostgreSQL
sudo dnf install postgresql postgresql-server postgresql-contrib

# 初始化数据库
sudo postgresql-setup --initdb

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库
sudo -u postgres psql -c "CREATE DATABASE petmind;"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'your_password';"
```

---

## 服务启动顺序

**必须按以下顺序启动，否则服务间依赖可能失败：**

```
1. PostgreSQL（数据库）
        ↓
2. Python FastAPI（AI 服务，端口 8000）
        ↓
3. Go Gin（后端服务，端口 8080）
        ↓
4. Vue（前端，端口 5173）
```

### 一键启动（Windows）

```powershell
# 项目根目录下运行
.\start.ps1
```

### 手动分步启动

```bash
# 终端 1: 启动 AI 服务
cd core-python
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Linux/Mac
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端 2: 启动 Go 后端
cd backend-go
go run cmd/server/main.go

# 终端 3: 启动前端
cd frontend
npm run dev
```

---

## 环境变量说明

### backend-go/.env

```env
# JWT 密钥（必填，请使用强随机字符串）
PETMIND_JWT_SECRET=your-strong-jwt-secret-key

# 数据库类型（postgres 或 sqlite）
PETMIND_DB_TYPE=postgres

# PostgreSQL 连接配置
PETMIND_DB_HOST=localhost
PETMIND_DB_PORT=5432
PETMIND_DB_USER=postgres
PETMIND_DB_PASSWORD=your_db_password
PETMIND_DB_NAME=petmind

# AI 服务地址
PETMIND_AI_API_URL=http://localhost:8000/api/v1

# 文件上传目录
PETMIND_UPLOAD_DIR=./data/uploads

# 服务端口
PETMIND_PORT=8080

# 管理员注册密钥（必填）
PETMIND_ADMIN_SECRET=your-admin-secret-key
```

### core-python/.env

```env
# 阿里百炼 API 密钥（必填）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# PostgreSQL 配置（可选，Chroma 向量库使用本地 SQLite）
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=petmind
```

### frontend/.env（可选）

```env
# 后端 API 地址（默认 http://localhost:8080）
VITE_API_BASE_URL=http://localhost:8080
```

---

## Windows 部署

### 完整部署流程

```powershell
# 1. 克隆项目
git clone <repository-url>
cd PetMind

# 2. 配置后端环境变量
cp backend-go/.env.example backend-go/.env
# 编辑 backend-go/.env，填写 PostgreSQL 密码和密钥

# 3. 安装 Go 依赖
cd backend-go
go mod tidy
cd ..

# 4. 配置 Python 环境
cd core-python
cp .env_example .env
# 编辑 .env，填写 DASHSCOPE_API_KEY

python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 初始化向量数据库（首次运行必须执行）
python scripts/init_vectorstore.py --rebuild
cd ..

# 5. 安装前端依赖
cd frontend
npm install
cd ..

# 6. 一键启动
.\start.ps1
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 用户前端 | http://localhost:5173 |
| 管理后台登录 | http://localhost:5173/admin/login |
| 管理后台注册 | http://localhost:5173/admin/register |
| AI 服务文档 | http://localhost:8000/docs |
| 后端健康检查 | http://localhost:8080/health |

---

## Linux 部署

### 完整部署流程

```bash
# 1. 克隆项目
git clone <repository-url>
cd PetMind

# 2. 安装 Go（如未安装）
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# 3. 配置后端环境变量
cp backend-go/.env.example backend-go/.env
vi backend-go/.env   # 填写 PostgreSQL 密码和密钥

# 4. 安装 Go 依赖
cd backend-go && go mod tidy && cd ..

# 5. 配置 Python 环境
cd core-python
cp .env_example .env
vi .env   # 填写 DASHSCOPE_API_KEY

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 初始化向量数据库
python scripts/init_vectorstore.py --rebuild
cd ..

# 6. 安装前端依赖（如需构建生产版本）
cd frontend
npm install
npm run build   # 生成 dist/ 目录
cd ..
```

### 使用 Nginx 部署前端（生产）

```nginx
# /etc/nginx/conf.d/petmind.conf
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    root /path/to/PetMind/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # 代理后端 API
    location /api/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 代理流式响应（SSE）
    location /api/v1/messages/stream {
        proxy_pass http://localhost:8080;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding on;
    }
}
```

---

## 故障排查

### 问题：后端启动失败 - 端口被占用

```
listen tcp :8080: bind: address already in use
```

**解决方案：**

```bash
# 查找占用端口的进程
# Windows:
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux:
lsof -i :8080
kill -9 <PID>
```

### 问题：PostgreSQL 连接失败

```
failed to connect to database: dial tcp localhost:5432: connect: connection refused
```

**解决方案：**

```bash
# 检查 PostgreSQL 是否运行
# Windows: 在服务管理器中检查 postgresql-x64-xx 服务
# Linux:
sudo systemctl status postgresql

# 检查配置文件中的密码是否正确
cat backend-go/.env | grep PETMIND_DB
```

### 问题：Python AI 服务启动失败 - 缺少依赖

```
ModuleNotFoundError: No module named 'langchain'
```

**解决方案：**

```bash
cd core-python
.\venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux
pip install -r requirements.txt
```

### 问题：向量数据库为空 - AI 回答质量差

**解决方案：**

```bash
cd core-python
.\venv\Scripts\activate
python scripts/init_vectorstore.py --rebuild
```

这将重新加载所有知识库文档并构建向量索引（需要几分钟）。

### 问题：管理员无法登录

**解决方案：**

1. 确认已在 `backend-go/.env` 或 `config.yaml` 中配置 `PETMIND_ADMIN_SECRET`
2. 注册时输入的管理员密钥必须与配置一致
3. 检查后端日志确认注册请求是否成功

```bash
# 测试注册管理员（将 your-secret 替换为实际密钥）
curl -X POST http://localhost:8080/api/v1/admin/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"123456","admin_secret":"your-secret"}'
```

### 问题：前端访问 /admin/login 跳转到 /

**原因：** 路由守卫逻辑导致。

**说明：** 管理员登录/注册页面无需认证，任何人都可以访问。如果跳转到 `/`，请检查前端路由配置中 `/admin/login` 是否带有 `meta: { guest: true }`（该 meta 表示"仅未登录用户可访问"，已登录用户会被重定向到 `/`）。

### 问题：AI 回答超时

**原因：** 阿里云 API 响应慢或网络不稳定。

**解决方案：** 检查 `DASHSCOPE_API_KEY` 是否有效，确认 API 余额充足。

```bash
# 测试 AI 服务连通性
curl http://localhost:8000/health
```

### 问题：图片上传失败

**解决方案：** 确认上传目录存在并有写入权限：

```bash
mkdir -p backend-go/data/uploads
# Linux:
chmod 755 backend-go/data/uploads
```

---

## 生产环境建议

1. **JWT 密钥**：使用至少 32 位强随机字符串
2. **管理员密钥**：使用复杂密钥，不要使用默认值
3. **数据库密码**：使用强密码，限制数据库访问 IP
4. **HTTPS**：生产环境务必启用 HTTPS
5. **日志**：配置日志轮转，避免磁盘爆满
6. **备份**：定期备份 PostgreSQL 数据库和 Chroma 向量库
