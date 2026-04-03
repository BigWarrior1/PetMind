#!/bin/bash

# PetMind 环境检查与自动安装脚本
# 用法: bash check_env.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "  PetMind 环境检查与安装脚本"
echo "========================================"
echo ""

# 检查是否 root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}⚠${NC} 此脚本需要 root 权限来安装软件"
    echo "请使用: sudo bash check_env.sh"
    echo ""
    echo "或者手动运行以下命令安装依赖:"
    echo "  sudo apt update && sudo apt install -y golang-go python3 python3-pip nodejs npm git sqlite3"
    exit 1
fi

# 检测包管理器
detect_package_manager() {
    if command -v apt-get &> /dev/null; then
        echo "apt"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    else
        echo "unknown"
    fi
}

# 安装函数
install_package() {
    local package=$1
    local manager=$(detect_package_manager)

    if command -v $package &> /dev/null; then
        return 0
    fi

    echo -e "${BLUE}→${NC} 安装 $package..."
    case $manager in
        apt)
            apt-get install -y $package ;;
        yum)
            yum install -y $package ;;
        dnf)
            dnf install -y $package ;;
        pacman)
            pacman -S --noconfirm $package ;;
        *)
            echo -e "${RED}✗${NC} 无法自动安装 $package，不支持的包管理器: $manager"
            return 1 ;;
    esac
}

# 检查单个命令并安装
check_and_install() {
    local cmd=$1
    local package=$2
    local name=${3:-$cmd}

    if command -v $cmd &> /dev/null; then
        return 0
    fi

    if [ -n "$package" ]; then
        install_package "$package"
    else
        echo -e "${RED}✗${NC} $name: 未安装且无法自动安装"
        return 1
    fi
}

echo "【开始检查并安装必要环境】"
echo "----------------------------------------"
echo ""

# 必要环境
check_and_install "go" "golang-go" "Go"
check_and_install "python3" "python3" "Python"
check_and_install "node" "nodejs" "Node.js"
check_and_install "npm" "npm" "npm"
check_and_install "git" "git" "Git"
check_and_install "sqlite3" "sqlite3" "SQLite"

echo ""
echo "【版本检查】"
echo "----------------------------------------"

# Go 版本
go_version=$(go version 2>/dev/null | grep -oP 'go\d+\.\d+(\.\d+)?' || echo "")
if [ -n "$go_version" ]; then
    go_num=${go_version#go}
    major=${go_num%%.*}
    minor=${go_num#*.}
    minor=${minor%%.*}
    if [ "$major" -ge 1 ] && [ "$minor" -ge 21 ]; then
        echo -e "${GREEN}✓${NC} Go: $go_version (满足 >= 1.21)"
    else
        echo -e "${YELLOW}⚠${NC} Go: $go_version (建议 >= 1.21)"
    fi
fi

# Python 版本
py_version=$(python3 --version 2>/dev/null | grep -oP '\d+\.\d+(\.\d+)?' || echo "")
if [ -n "$py_version" ]; then
    major=${py_version%%.*}
    minor=${py_version#*.}
    minor=${minor%%.*}
    if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
        echo -e "${GREEN}✓${NC} Python: $py_version (满足 >= 3.9)"
    else
        echo -e "${YELLOW}⚠${NC} Python: $py_version (建议 >= 3.9)"
    fi
fi

# Node 版本
node_version=$(node --version 2>/dev/null | grep -oP 'v\d+\.\d+(\.\d+)?' || echo "")
if [ -n "$node_version" ]; then
    node_num=${node_version#v}
    major=${node_num%%.*}
    if [ "$major" -ge 18 ]; then
        echo -e "${GREEN}✓${NC} Node.js: $node_version (满足 >= 18)"
    else
        echo -e "${YELLOW}⚠${NC} Node.js: $node_version (建议 >= 18)"
    fi
fi

# pip 检查
if command -v pip3 &> /dev/null; then
    pip_version=$(pip3 --version 2>/dev/null | grep -oP '\d+\.\d+(\.\d+)?' || echo "")
    echo -e "${GREEN}✓${NC} pip: $pip_version"
elif command -v pip &> /dev/null; then
    pip_version=$(pip --version 2>/dev/null | grep -oP '\d+\.\d+(\.\d+)?' || echo "")
    echo -e "${GREEN}✓${NC} pip: $pip_version"
else
    echo -e "${YELLOW}⚠${NC} pip: 未安装"
fi

echo ""
echo "【环境就绪！】"
echo "----------------------------------------"
echo -e "${GREEN}✓ 所有必要环境已安装完成！${NC}"
echo ""
echo "下一步："
echo "  1. cp .env.example .env  # 复制环境变量"
echo "  2. 编辑各模块的 .env 文件，配置必要的 API Key"
echo "  3. 参考 README.md 启动各服务"
