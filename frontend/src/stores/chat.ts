import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sessionsApi } from '@/api/sessions'
import { messagesApi, type Message } from '@/api/messages'
import type { Session } from '@/api/sessions'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<Session[]>([])
  const currentSession = ref<Session | null>(null)
  const messages = ref<Message[]>([])
  const loading = ref(false)

  async function fetchSessions() {
    sessions.value = await sessionsApi.list()
  }

  async function createSession(title: string, petId?: string) {
    const session = await sessionsApi.create({ title, pet_id: petId })
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

    loading.value = true
    try {
      await messagesApi.send({
        session_id: currentSession.value.id,
        content
      })

      // 再次获取消息（包含AI回复）
      await fetchMessages(currentSession.value.id)
    } finally {
      loading.value = false
    }
  }

  async function sendImage(file: File, question: string = '请分析这张图片中的宠物健康状况') {
    if (!currentSession.value) return

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
    } finally {
      loading.value = false
    }
  }

  return {
    sessions,
    currentSession,
    messages,
    loading,
    fetchSessions,
    createSession,
    deleteSession,
    setCurrentSession,
    fetchMessages,
    sendMessage,
    sendImage
  }
})
