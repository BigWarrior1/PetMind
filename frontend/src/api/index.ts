import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 120000  // 120 秒，适应 AI 回复较慢的情况
})

// 请求拦截器：添加 JWT token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：统一处理错误
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const status = error.response.status
      const message = error.response.data?.error || '请求失败'

      // 判断当前请求是否为登录接口
      const isLoginRequest = error.config?.url?.includes('/auth/login') ||
                             error.config?.url?.includes('/admin/login')

      switch (status) {
        case 401:
          if (isLoginRequest) {
            // 登录失败：显示后端返回的错误信息（如"用户名或密码错误"），不做重定向
            ElMessage.error(message)
          } else {
            // Token 过期：清除登录状态并跳转登录页
            ElMessage.error(message)
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            window.location.href = '/login'
          }
          break
        case 403:
          ElMessage.error(message)
          break
        case 404:
          ElMessage.error(message)
          break
        case 409:
          ElMessage.error(message)
          break
        case 500:
          ElMessage.error(message)
          break
        default:
          ElMessage.error(message)
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default request
