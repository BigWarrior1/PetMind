# PetMind 前端

基于 Vue 3 + Vite + Element Plus 的宠物健康智能问答系统前端。

## 技术栈

| 技术 | 说明 |
|------|------|
| Vue 3 | 渐进式 JavaScript 框架 |
| Vite | 下一代前端构建工具 |
| TypeScript | JavaScript 超集 |
| Element Plus | Vue 3 组件库 |
| Pinia | Vue 状态管理 |
| Vue Router | Vue 路由管理 |
| Axios | HTTP 请求库 |

## 项目结构

```
frontend/
├── src/
│   ├── api/                 # API 请求封装
│   │   ├── index.ts        # axios 实例 + 拦截器
│   │   ├── auth.ts         # 认证相关
│   │   ├── pets.ts         # 宠物档案
│   │   ├── sessions.ts      # 会话管理
│   │   └── messages.ts     # 消息管理
│   ├── components/         # 公共组件
│   │   ├── ChatInput.vue   # 聊天输入框
│   │   ├── ChatMessage.vue # 消息气泡
│   │   ├── SessionList.vue  # 会话列表
│   │   └── PetCard.vue     # 宠物卡片
│   ├── views/              # 页面
│   │   ├── Login.vue       # 登录页
│   │   ├── Register.vue    # 注册页
│   │   ├── Chat.vue        # 聊天主页
│   │   └── Pets.vue        # 宠物管理
│   ├── stores/             # Pinia 状态管理
│   │   ├── auth.ts         # 认证状态
│   │   ├── chat.ts         # 聊天状态
│   │   └── pets.ts         # 宠物状态
│   ├── router/             # Vue Router
│   │   └── index.ts
│   ├── styles/             # 全局样式
│   │   └── common.css
│   ├── App.vue
│   └── main.ts
├── index.html
├── vite.config.ts
└── package.json
```

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

## 功能特性

- [x] 用户注册和登录
- [x] JWT 认证
- [x] 宠物档案管理（增删改查）
- [x] 会话管理
- [x] AI 智能问答
- [x] 图片上传与分析
- [x] 就医警示提示
- [x] 参考来源展示

## 页面预览

### 聊天页面
- 左侧会话列表
- 中间聊天区域
- 底部输入框支持文字和图片

### 宠物管理
- 卡片式宠物展示
- 添加/编辑宠物弹窗

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| VITE_API_BASE_URL | /api/v1 | API 基础路径 |

## API 代理

开发环境下，Vite 会将 `/api` 请求代理到 `http://localhost:8080`（Go 后端）。

生产环境请配置 nginx 反向代理。
