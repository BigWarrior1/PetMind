import request from './index'

export interface Session {
  id: string
  user_id: string
  pet_id: string | null
  title: string
  created_at: string
  updated_at: string
}

export interface CreateSessionRequest {
  pet_id?: string
  title: string
}

export const sessionsApi = {
  list() {
    return request.get<any, Session[]>('/sessions')
  },

  get(id: string) {
    return request.get<any, Session>(`/sessions/${id}`)
  },

  create(data: CreateSessionRequest) {
    return request.post<any, Session>('/sessions', data)
  },

  delete(id: string) {
    return request.delete<any, { message: string }>(`/sessions/${id}`)
  }
}
