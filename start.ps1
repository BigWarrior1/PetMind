# PetMind 一键启动脚本
# 使用方式: 右键 -> 用 PowerShell 运行
# 或在 PowerShell 中: .\start.ps1

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot

Write-Host "========================================"
Write-Host "  PetMind 服务启动器"
Write-Host "========================================"
Write-Host ""

# 检查 Python AI 服务
Write-Host "[1/3] 启动 AI 服务 (Python)..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\core-python'; Write-Host 'AI 服务启动中...'; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

Start-Sleep -Seconds 1

# 检查 Go 后端
Write-Host "[2/3] 启动 Go 后端..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\backend-go'; Write-Host 'Go 后端启动中...'; go run cmd/server/main.go" -WindowStyle Normal

Start-Sleep -Seconds 1

# 检查 Vue 前端
Write-Host "[3/3] 启动前端..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\frontend'; Write-Host '前端启动中...'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "========================================"
Write-Host "  服务已在新窗口启动!"
Write-Host "========================================"
Write-Host ""
Write-Host "访问地址:"
Write-Host "  AI 服务:   http://localhost:8000/docs"
Write-Host "  Go 后端:   http://localhost:8080"
Write-Host "  Vue 前端:  http://localhost:5173"
Write-Host ""
Write-Host "按任意键退出此窗口..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
