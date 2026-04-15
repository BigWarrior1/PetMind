# PetMind 项目管理 Makefile

# ==========================================
# 配置
# ==========================================

PYTHON_VENV := core-python/venv
PYTHON := $(PYTHON_VENV)/Scripts/python.exe
AI_PORT := 8000
BACKEND_PORT := 8080
FRONTEND_PORT := 5173

# Windows 下使用 pkill，Linux 下使用 kill
ifeq ($(OS),Windows_NT)
    KILL := taskkill /F /IM
    PYACT := $(PYTHON_VENV)/Scripts/activate.bat
else
    KILL := pkill -f
    PYACT := source $(PYTHON_VENV)/bin/activate
endif

# ==========================================
# 帮助信息
# ==========================================

.PHONY: help
help:
	@echo "PetMind 项目管理命令"
	@echo ""
	@echo "用法: make <目标>"
	@echo ""
	@echo "  install              安装所有依赖 (前端 + Go + Python AI)"
	@echo "  init                 初始化项目 (安装依赖 + 初始化向量数据库)"
	@echo ""
	@echo "前端 (Vue 3):"
	@echo "  frontend-install    安装前端依赖"
	@echo "  frontend-dev        启动前端开发服务器 (localhost:$(FRONTEND_PORT))"
	@echo "  frontend-build      构建前端生产版本"
	@echo "  frontend-clean      清理前端构建产物"
	@echo ""
	@echo "后端 Go:"
	@echo "  backend-deps        安装 Go 依赖"
	@echo "  backend-dev        启动 Go 后端服务 (localhost:$(BACKEND_PORT))"
	@echo "  backend-build      构建 Go 后端"
	@echo "  backend-clean      清理 Go 构建产物"
	@echo ""
	@echo "AI 服务 (Python):"
	@echo "  ai-install          安装 Python AI 依赖"
	@echo "  ai-init-db          初始化向量数据库 (首次运行必须执行)"
	@echo "  ai-dev              启动 Python AI 服务 (localhost:$(AI_PORT))"
	@echo ""
	@echo "快捷启动 (需分别打开终端窗口):"
	@echo "  dev                 启动所有开发服务"
	@echo ""
	@echo "清理:"
	@echo "  clean               清理所有构建产物"
	@echo ""
	@echo "信息:"
	@echo "  info                显示各服务访问地址"

# ==========================================
# 前端
# ==========================================

.PHONY: frontend-install frontend-dev frontend-build frontend-clean
frontend-install:
	@echo "安装前端依赖..."
	cd frontend && npm install

frontend-dev:
	@echo "启动前端开发服务器 (http://localhost:$(FRONTEND_PORT))..."
	cd frontend && npm run dev

frontend-build:
	@echo "构建前端..."
	cd frontend && npm run build

frontend-clean:
	@echo "清理前端构建产物..."
	-if exist frontend\dist rmdir /s /q frontend\dist
	-if exist frontend\node_modules rmdir /s /q frontend\node_modules

# ==========================================
# 后端 Go
# ==========================================

.PHONY: backend-deps backend-dev backend-build backend-clean backend-run
backend-deps:
	@echo "安装 Go 依赖..."
	cd backend-go && go mod tidy

backend-dev:
	@echo "启动 Go 后端服务 (http://localhost:$(BACKEND_PORT))..."
	cd backend-go && go run cmd/server/main.go

backend-build:
	@echo "构建 Go 后端..."
	cd backend-go && go build -o bin/server.exe cmd/server/main.go

backend-clean:
	@echo "清理 Go 构建产物..."
	-if exist backend-go\bin rmdir /s /q backend-go\bin

backend-run: backend-build
	@echo "运行 Go 后端 (http://localhost:$(BACKEND_PORT))..."
	cd backend-go && ./bin/server.exe

# ==========================================
# AI 服务 (Python)
# ==========================================

.PHONY: ai-install ai-init-db ai-dev
ai-install:
	@echo "安装 Python AI 依赖..."
	@if not exist $(PYTHON_VENV) ( \
		echo "创建 Python 虚拟环境... && \
		cd core-python && python -m venv venv \
	)
	@echo "安装依赖包..."
	$(PYTHON) -m pip install -r core-python/requirements.txt

ai-init-db:
	@echo "初始化向量数据库 (这可能需要几分钟)..."
	$(PYTHON) core-python/scripts/init_vectorstore.py --rebuild

ai-dev:
	@echo "启动 Python AI 服务 (http://localhost:$(AI_PORT))..."
	@echo "API 文档: http://localhost:$(AI_PORT)/docs"
	$(PYTHON) -m uvicorn core-python/app.main:app --reload --host 0.0.0.0 --port $(AI_PORT)

# ==========================================
# 一键命令
# ==========================================

.PHONY: install init
install: frontend-install backend-deps ai-install
	@echo ""
	@echo "=========================================="
	@echo "所有依赖安装完成！"
	@echo ""
	@echo "下一步:"
	@echo "  1. 确保 PostgreSQL 已启动并创建了 petmind 数据库"
	@echo "  2. 配置 backend-go/.env 中的数据库连接信息"
	@echo "  3. 配置 core-python/.env 中的 DASHSCOPE_API_KEY"
	@echo "  4. 运行 'make init' 初始化向量数据库"
	@echo "  5. 运行 'make dev' 启动所有服务"
	@echo "=========================================="

init: ai-init-db
	@echo ""
	@echo "向量数据库初始化完成！"

# ==========================================
# 启动所有开发服务 (分别打开终端窗口)
# ==========================================

.PHONY: dev
dev:
	@echo "请分别打开 3 个终端窗口，运行以下命令:"
	@echo ""
	@echo "终端 1 - AI 服务:"
	@echo "  make ai-dev"
	@echo ""
	@echo "终端 2 - Go 后端:"
	@echo "  make backend-dev"
	@echo ""
	@echo "终端 3 - Vue 前端:"
	@echo "  make frontend-dev"

# ==========================================
# 停止所有服务
# ==========================================

.PHONY: stop
stop:
	@echo "停止所有 PetMind 服务..."
	$(KILL) node.exe 2>nul || true
	$(KILL) server.exe 2>nul || true
	$(KILL) uvicorn.exe 2>nul || true
	@echo "服务已停止"

# ==========================================
# 清理
# ==========================================

.PHONY: clean
clean: frontend-clean backend-clean
	@echo "清理完成！"

# ==========================================
# 信息
# ==========================================

.PHONY: info
info:
	@echo "PetMind 服务访问地址"
	@echo ""
	@echo "  前端 (Vue):     http://localhost:$(FRONTEND_PORT)"
	@echo "  后端 (Go):      http://localhost:$(BACKEND_PORT)"
	@echo "  后端健康检查:   http://localhost:$(BACKEND_PORT)/health"
	@echo "  AI 服务 (FastAPI):  http://localhost:$(AI_PORT)"
	@echo "  AI API 文档:    http://localhost:$(AI_PORT)/docs"
	@echo ""
	@echo "  管理后台登录:   http://localhost:$(FRONTEND_PORT)/admin/login"
	@echo ""
	@echo "数据库 (PostgreSQL):"
	@echo "  host: localhost"
	@echo "  port: 5432"
	@echo "  database: petmind"
	@echo ""
	@echo "向量数据库 (Chroma):"
	@echo "  存储路径: core-python/data/chroma_db"
