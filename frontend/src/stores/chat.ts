import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { sessionsApi } from '@/api/sessions'
import { messagesApi, type Message } from '@/api/messages'
import type { Session } from '@/api/sessions'

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

  async function sendImage(file: File, question: string = '请分析这张图片中的宠物健康状况') {
    if (!currentSession.value) return

    // 1. 立即添加用户消息（乐观更新，带图片）
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      session_id: currentSession.value.id,
      role: 'user',
      content: question,
      image_urls: JSON.stringify([URL.createObjectURL(file)]),
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

      // 再次获取消息（包含AI回复）
      if (currentSession.value) {
        await fetchMessages(currentSession.value.id)
      }
    } catch (error) {
      // 失败时移除临时消息
      messages.value = messages.value.filter(m => !m.id.startsWith('temp-'))
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
    sendMessage,
    sendImage
  }
})
