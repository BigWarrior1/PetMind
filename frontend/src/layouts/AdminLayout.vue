<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const menuItems = [
  { path: '/admin/dashboard', label: '仪表板', icon: 'DataAnalysis' },
  { path: '/admin/users', label: '用户管理', icon: 'User' },
  { path: '/admin/pets', label: '宠物管理', icon: 'Grid' },
  { path: '/admin/sessions', label: '会话管理', icon: 'ChatDotRound' }
]

function handleLogout() {
  authStore.logout()
  router.push('/admin/login')
}
</script>

<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo">
        <h2>PetMind Admin</h2>
      </div>
      <el-menu
        :default-active="route.path"
        class="sidebar-menu"
        router
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.path"
          :index="item.path"
        >
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <div class="user-info">
          <span>{{ authStore.user?.username }}</span>
          <el-tag size="small" type="danger">管理员</el-tag>
        </div>
        <el-button type="danger" size="small" @click="handleLogout">
          退出登录
        </el-button>
      </div>
    </aside>

    <!-- 主内容 -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 220px;
  background: #304156;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 20px;
  color: white;
  text-align: center;
}

.logo h2 {
  font-size: 18px;
  margin: 0;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background: #304156;
}

.sidebar-menu .el-menu-item {
  color: #bfcbd9;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-menu-item.is-active {
  background: #263445;
  color: #409eff;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #263445;
}

.user-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #bfcbd9;
  font-size: 14px;
  margin-bottom: 12px;
}

.main-content {
  flex: 1;
  background: #f0f2f5;
  padding: 24px;
  overflow-y: auto;
}
</style>
