# PetMind 项目管理 Makefile

# 帮助信息
.PHONY: help
help:
	@echo "PetMind 项目管理命令"
	@echo ""
	@echo "用法: make <目标>"
	@echo ""
	@echo "前端:"
	@echo "  frontend-install    安装前端依赖"
	@echo "  frontend-dev       启动前端开发服务器 (localhost:5173)"
	@echo "  frontend-build     构建前端生产版本"
	@echo ""
	@echo "后端 Go:"
	@echo "  backend-deps       安装 Go 依赖"
	@echo "  backend-dev        启动 Go 后端服务 (localhost:8080)"
	@echo "  backend-build      构建 Go 后端"
	@echo ""
	@echo "AI 服务 (Python):"
	@echo "  ai-install         安装 Python AI 依赖"
	@echo "  ai-init-db         初始化向量数据库"
	@echo "  ai-dev             启动 Python AI 服务 (localhost:8000)"
	@echo ""
	@echo "快捷命令:"
	@echo "  install            安装所有依赖"
	@echo "  init               初始化项目 (安装依赖 + 初始化数据库)"
	@echo ""
	@echo "清理:"
	@echo "  frontend-clean     清理前端构建产物"
	@echo "  backend-clean      清理 Go 构建产物"
	@echo "  clean              清理所有构建产物"

# ==========================================
# 前端
# ==========================================

.PHONY: frontend-install frontend-dev frontend-build frontend-clean
frontend-install:
	@echo "安装前端依赖..."
	cd frontend && npm install

frontend-dev:
	@echo "启动前端开发服务器 (http://localhost:5173)..."
	cd frontend && npm run dev

frontend-build:
	@echo "构建前端..."
	cd frontend && npm run build

frontend-clean:
	@echo "清理前端构建产物..."
	rm -rf frontend/dist
	rm -rf frontend/node_modules

# ==========================================
# 后端 Go
# ==========================================

.PHONY: backend-deps backend-dev backend-build backend-clean
backend-deps:
	@echo "安装 Go 依赖..."
	cd backend-go && go mod tidy

backend-dev:
	@echo "启动 Go 后端服务 (http://localhost:8080)..."
	cd backend-go && go run cmd/server/main.go

backend-build:
	@echo "构建 Go 后端..."
	cd backend-go && go build -o bin/server cmd/server/main.go

backend-clean:
	@echo "清理 Go 构建产物..."
	rm -rf backend-go/bin
	rm -rf backend-go/data/petmind.db

# ==========================================
# AI 服务 (Python)
# ==========================================

.PHONY: ai-install ai-init-db ai-dev
ai-install:
	@echo "安装 Python AI 依赖..."
	cd core-python && pip install -r requirements.txt

ai-init-db:
	@echo "初始化向量数据库..."
	cd core-python && python scripts/init_vectorstore.py --rebuild

ai-dev:
	@echo "启动 Python AI 服务 (http://localhost:8000)..."
	@echo "API 文档: http://localhost:8000/docs"
	cd core-python && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ==========================================
# 快捷命令
# ==========================================

.PHONY: install init
install: frontend-install backend-deps ai-install
	@echo ""
	@echo "所有依赖安装完成！"
	@echo "运行 'make init' 初始化数据库"
	@echo "然后分别打开 3 个终端运行: make ai-dev | make backend-dev | make frontend-dev"

init: ai-init-db
	@echo ""
	@echo "初始化完成！"
	@echo "请分别打开 3 个终端运行以下命令:"

# ==========================================
# 清理
# ==========================================

.PHONY: clean
clean: frontend-clean backend-clean
	@echo "清理完成！"

# ==========================================
# 详细启动说明
# ==========================================

.PHONY: info
info:
	@echo "PetMind 服务启动方式 - 请分别打开 3 个终端窗口:"
	@echo ""
	@echo "终端 1 - AI 服务 (Python):"
	@echo "  make ai-dev"
	@echo "  或: cd core-python && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
	@echo ""
	@echo "终端 2 - Go 后端:"
	@echo "  make backend-dev"
	@echo "  或: cd backend-go && go run cmd/server/main.go"
	@echo ""
	@echo "终端 3 - Vue 前端:"
	@echo "  make frontend-dev"
	@echo "  或: cd frontend && npm run dev"
	@echo ""
	@echo "访问地址:"
	@echo "  前端:   http://localhost:5173"
	@echo "  AI API: http://localhost:8000/docs"
	@echo "  Go API: http://localhost:8080"
