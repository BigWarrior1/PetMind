import request from './index'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface User {
  id: string
  username: string
  email: string
  created_at: string
  updated_at: string
}

export interface LoginResponse {
  token: string
  user: User
}

export const authApi = {
  login(data: LoginRequest) {
    return request.post<any, { token: string; user: User }>('/auth/login', data)
  },

  register(data: RegisterRequest) {
    return request.post<any, User>('/auth/register', data)
  }
}
