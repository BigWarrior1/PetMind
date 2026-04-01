import request from './index'

export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant'
  content: string
  image_urls: string
  sources: string
  created_at: string
}

export interface SendMessageRequest {
  session_id: string
  content: string
}

export interface SourceInfo {
  source: string
  source_type?: string
  confidence?: number
  semantic_score?: number
}

export const messagesApi = {
  listBySession(sessionId: string) {
    return request.get<any, Message[]>(`/messages/session/${sessionId}`)
  },

  send(data: SendMessageRequest) {
    return request.post<any, Message>('/messages', data)
  },

  sendImage(formData: FormData) {
    return request.post<any, Message>('/messages/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}
