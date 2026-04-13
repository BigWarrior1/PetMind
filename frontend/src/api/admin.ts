import request from './index'

export interface AdminLoginRequest {
  username: string
  password: string
}

export interface AdminRegisterRequest {
  username: string
  email: string
  password: string
  admin_secret: string
}

export interface User {
  id: string
  username: string
  email: string
  role: string
  created_at: string
  updated_at: string
}

export interface Pet {
  id: string
  user_id: string
  name: string
  species: string
  breed: string
  age: string
  weight: string
  gender: string
  birthday: string
  notes: string
  created_at: string
  updated_at: string
}

export interface Session {
  id: string
  user_id: string
  pet_id: string | null
  title: string
  summary: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  session_id: string
  role: string
  content: string
  image_urls: string
  sources: string
  created_at: string
}

export interface PageResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface StatsResponse {
  users: number
  pets: number
  sessions: number
  messages: number
}

export const adminApi = {
  // 管理员注册
  register(data: AdminRegisterRequest) {
    return request.post<any, { message: string; user: User; token: string }>('/admin/register', data)
  },

  // 管理员登录
  login(data: AdminLoginRequest) {
    return request.post<any, { token: string; user: User }>('/admin/login', data)
  },

  // 获取统计数据
  getStats() {
    return request.get<any, StatsResponse>('/admin/stats')
  },

  // 用户管理
  getUsers(page: number = 1, pageSize: number = 20) {
    return request.get<any, PageResponse<User>>('/admin/users', { params: { page, page_size: pageSize } })
  },

  deleteUser(id: string) {
    return request.delete<any, { message: string }>(`/admin/users/${id}`)
  },

  // 宠物管理
  getPets(page: number = 1, pageSize: number = 20) {
    return request.get<any, PageResponse<Pet>>('/admin/pets', { params: { page, page_size: pageSize } })
  },

  deletePet(id: string) {
    return request.delete<any, { message: string }>(`/admin/pets/${id}`)
  },

  // 会话管理
  getSessions(page: number = 1, pageSize: number = 20) {
    return request.get<any, PageResponse<Session>>('/admin/sessions', { params: { page, page_size: pageSize } })
  },

  getSessionMessages(sessionId: string) {
    return request.get<any, Message[]>(`/admin/sessions/${sessionId}/messages`)
  },

  deleteSession(id: string) {
    return request.delete<any, { message: string }>(`/admin/sessions/${id}`)
  }
}
