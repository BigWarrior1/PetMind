import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { guest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/Register.vue'),
      meta: { guest: true }
    },
    {
      path: '/',
      name: 'chat',
      component: () => import('@/views/Chat.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/pets',
      name: 'pets',
      component: () => import('@/views/Pets.vue'),
      meta: { requiresAuth: true }
    },
    // 管理员路由（登录注册页无需认证，任何人都可访问）
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/AdminLogin.vue')
    },
    {
      path: '/admin/register',
      name: 'admin-register',
      component: () => import('@/views/admin/AdminRegister.vue')
    },
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/AdminDashboard.vue')
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('@/views/admin/AdminUsers.vue')
        },
        {
          path: 'pets',
          name: 'admin-pets',
          component: () => import('@/views/admin/AdminPets.vue')
        },
        {
          path: 'sessions',
          name: 'admin-sessions',
          component: () => import('@/views/admin/AdminSessions.vue')
        },
        {
          path: 'sessions/:id',
          name: 'admin-session-detail',
          component: () => import('@/views/admin/AdminSessionDetail.vue')
        },
        {
          path: '',
          redirect: '/admin/dashboard'
        }
      ]
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    // 如果不是管理员，尝试跳转登录页
    if (!authStore.isLoggedIn) {
      next('/admin/login')
    } else {
      // 已登录但不是管理员，跳转到主页
      next('/')
    }
  } else if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.guest && authStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
