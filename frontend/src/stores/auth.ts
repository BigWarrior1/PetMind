import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type User, type LoginRequest, type RegisterRequest } from '@/api/auth'
import { adminApi, type AdminLoginRequest, type AdminRegisterRequest } from '@/api/admin'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(data: LoginRequest) {
    const response = await authApi.login(data)
    token.value = response.token
    user.value = response.user
    localStorage.setItem('token', response.token)
    localStorage.setItem('user', JSON.stringify(response.user))
  }

  async function register(data: RegisterRequest) {
    await authApi.register(data)
  }

  // 管理员登录
  async function adminLogin(data: AdminLoginRequest) {
    const response = await adminApi.login(data)
    token.value = response.token
    user.value = response.user
    localStorage.setItem('token', response.token)
    localStorage.setItem('user', JSON.stringify(response.user))
  }

  // 管理员注册
  async function adminRegister(data: AdminRegisterRequest) {
    await adminApi.register(data)
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    login,
    register,
    adminLogin,
    adminRegister,
    logout
  }
})
