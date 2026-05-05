import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sessionsApi } from '@/api/sessions'
import { messagesApi, type Message } from '@/api/messages'
import type { Session } from '@/api/sessions'
import { ElMessage } from 'element-plus'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<Session[]>([])
  const currentSession = ref<Session | null>(null)
  const messages = ref<Message[]>([])
  const loading = ref(false)

  // 计算属性：宠物专属会话
  const petSessions = computed(() =>
    sessions.value.filter(s => s.pet_id != null)
  )

  // 计算属性：普通会话
  const normalSessions = computed(() =>
    sessions.value.filter(s => s.pet_id == null)
  )

  async function fetchSessions() {
    sessions.value = await sessionsApi.list()
  }

  async function createSession(petId?: string) {
    // 普通对话不传 petId，宠物专属对话传 petId
    const session = await sessionsApi.create({ pet_id: petId })
    sessions.value.unshift(session)
    return session
  }

  async function createSessionWithTitle(petId: string, title: string) {
    const session = await sessionsApi.create({ pet_id: petId, title })
    sessions.value.unshift(session)
    return session
  }

  async function deleteSession(id: string) {
    await sessionsApi.delete(id)
    sessions.value = sessions.value.filter((s: Session) => s.id !== id)
    if (currentSession.value?.id === id) {
      currentSession.value = null
      messages.value = []
    }
  }

  async function setCurrentSession(session: Session | null) {
    currentSession.value = session
    if (session) {
      await fetchMessages(session.id)
    } else {
      messages.value = []
    }
  }

  async function fetchMessages(sessionId: string) {
    messages.value = await messagesApi.listBySession(sessionId)
  }

  async function sendMessageStream(content: string) {
    if (!currentSession.value) return

    // 1. 立即添加用户消息（乐观更新）
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      session_id: currentSession.value.id,
      role: 'user',
      content,
      image_urls: '[]',
      sources: '[]',
      created_at: new Date().toISOString()
    }
    messages.value.push(tempUserMessage)

    // 2. 添加一个临时的 AI 消息占位
    const tempAssistantMessage: Message = {
      id: `temp-assistant-${Date.now()}`,
      session_id: currentSession.value.id,
      role: 'assistant',
      content: '',
      image_urls: '[]',
      sources: '[]',
      created_at: new Date().toISOString()
    }
    messages.value.push(tempAssistantMessage)

    loading.value = true
    try {
      const response = await messagesApi.sendStream({
        session_id: currentSession.value.id,
        content
      }) as Response

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('无法读取响应')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // 处理 SSE 行
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            continue
          }
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6)
            try {
              const data = JSON.parse(dataStr)

              if (data.type === 'content') {
                // 追加文本内容
                tempAssistantMessage.content += data.content
                // 触发响应式更新
                const idx = messages.value.findIndex(m => m.id === tempAssistantMessage.id)
                if (idx !== -1) {
                  messages.value.splice(idx, 1, { ...tempAssistantMessage })
                }
              } else if (data.type === 'done') {
                // 流结束，更新完整消息
                if (data.assistant_msg) {
                  const idx = messages.value.findIndex(m => m.id === tempAssistantMessage.id)
                  if (idx !== -1) {
                    // assistant_msg 可能是 JSON 字符串，需要解析
                    let finalMsg = data.assistant_msg
                    if (typeof finalMsg === 'string') {
                      try {
                        finalMsg = JSON.parse(finalMsg)
                      } catch (e) {
                        // 解析失败，使用原数据
                      }
                    }
                    messages.value.splice(idx, 1, finalMsg as Message)
                  }
                }
              }
            } catch (e) {
              // 忽略解析错误
            }
          }
        }
      }
      // 刷新会话列表以获取后端生成的标题
      fetchSessions().then(() => {
        if (currentSession.value) {
          const updated = sessions.value.find(s => s.id === currentSession.value!.id)
          if (updated) {
            currentSession.value = updated
          }
        }
      })
    } catch (error: any) {
      // 失败时移除临时消息
      messages.value = messages.value.filter(m => !m.id.startsWith('temp-'))
      ElMessage.error(error.message || '发送消息失败')
    } finally {
      loading.value = false
    }
  }

  async function sendMessage(content: string) {
    if (!currentSession.value) return

    // 1. 立即添加用户消息（乐观更新）
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      session_id: currentSession.value.id,
      role: 'user',
      content,
      image_urls: '[]',
      sources: '[]',
      created_at: new Date().toISOString()
    }
    messages.value.push(tempUserMessage)

    loading.value = true
    try {
      // 2. 调用 API
      await messagesApi.send({
        session_id: currentSession.value.id,
        content
      })

      // 3. 获取完整消息列表
      await fetchMessages(currentSession.value.id)
    } catch (error) {
      // 4. 失败时移除临时消息（axios interceptor 已经显示了错误提示）
      messages.value = messages.value.filter(m => !m.id.startsWith('temp-'))
    } finally {
      loading.value = false
    }
  }

  async function sendImage(file: File, question: string = '请分析这张图片中的宠物健康状况', dataUrl?: string) {
    if (!currentSession.value) return

    // 使用传入的 dataUrl 或创建 blob URL
    const imageUrl = dataUrl || URL.createObjectURL(file)

    // 1. 立即添加用户消息（乐观更新，带图片）
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      session_id: currentSession.value.id,
      role: 'user',
      content: question,
      image_urls: JSON.stringify([imageUrl]),
      sources: '[]',
      created_at: new Date().toISOString()
    }
    messages.value.push(tempUserMessage)

    loading.value = true
    try {
      const formData = new FormData()
      formData.append('session_id', currentSession.value.id)
      formData.append('question', question)
      formData.append('image', file)

      await messagesApi.sendImage(formData)

      // 获取消息列表（包含AI回复）
      if (currentSession.value) {
        await fetchMessages(currentSession.value.id)
      }
    } catch (error: any) {
      // 失败时移除临时消息
      messages.value = messages.value.filter(m => !m.id.startsWith('temp-'))
      ElMessage.error(error.message || '发送图片失败')
    } finally {
      loading.value = false
    }
  }

  return {
    sessions,
    currentSession,
    messages,
    loading,
    petSessions,
    normalSessions,
    fetchSessions,
    createSession,
    createSessionWithTitle,
    deleteSession,
    setCurrentSession,
    fetchMessages,
    sendMessageStream,
    sendMessage,
    sendImage
  }
})
