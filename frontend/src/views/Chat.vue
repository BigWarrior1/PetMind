<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, ElDialog } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { usePetsStore } from '@/stores/pets'
import SessionList from '@/components/SessionList.vue'
import ChatMessage from '@/components/ChatMessage.vue'
import ChatInput from '@/components/ChatInput.vue'
import type { Session } from '@/api/sessions'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()
const petsStore = usePetsStore()

const chatContainer = ref<HTMLElement>()
const sidebarWidth = ref(280)
const isCollapsed = ref(false)

// 宠物选择对话框
const petDialogVisible = ref(false)
const selectedPetId = ref<string | null>(null)

onMounted(async () => {
  await Promise.all([
    chatStore.fetchSessions(),
    petsStore.fetchPets()
  ])

  if (chatStore.sessions.length > 0) {
    chatStore.setCurrentSession(chatStore.sessions[0])
  }
})

watch(() => chatStore.messages, () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}, { deep: true })

// 创建普通会话
async function handleCreateSession() {
  // 检查是否已有"新对话"的空会话
  const existingNewSession = chatStore.normalSessions.find(s => s.title === '新对话')
  if (existingNewSession) {
    chatStore.setCurrentSession(existingNewSession)
    return
  }

  const session = await chatStore.createSession()
  chatStore.setCurrentSession(session)
}

// 创建宠物专属会话
async function handleCreatePetSession() {
  if (petsStore.pets.length === 0) {
    ElMessage.warning('请先添加宠物')
    router.push('/pets')
    return
  }

  // 总是让用户选择确认，即使是只有一只宠物
  const pet = await selectPet()
  if (!pet) return

  // 检查该宠物是否已有专属会话
  const existingSession = chatStore.petSessions.find((s: Session) => s.pet_id === pet.id)
  if (existingSession) {
    ElMessage.info(`已存在与 ${pet.name} 的专属会话，正在打开...`)
    chatStore.setCurrentSession(existingSession)
    return
  }

  const title = `${pet.name}的专属顾问`
  const session = await chatStore.createSessionWithTitle(pet.id, title)
  chatStore.setCurrentSession(session)
}

// 选择宠物的辅助函数
async function selectPet(): Promise<{ id: string; name: string } | null> {
  const pets = petsStore.pets
  if (pets.length === 0) return null

  // 只有一只宠物也显示选择框让用户确认
  return new Promise((resolve) => {
    if (pets.length === 1) {
      // 只有一只宠物，显示确认框
      ElMessageBox.confirm(
        `确定要为宠物 "${pets[0].name}" 创建专属对话吗？`,
        '创建宠物专属会话',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }
      ).then(() => {
        resolve(pets[0])
      }).catch(() => {
        resolve(null)
      })
    } else {
      // 多只宠物，显示对话框让用户直接点击选择
      petDialogVisible.value = true
      // 等待用户选择后 resolve
      const checkSelected = setInterval(() => {
        if (selectedPetId.value) {
          clearInterval(checkSelected)
          const pet = pets.find(p => p.id === selectedPetId.value)
          petDialogVisible.value = false
          selectedPetId.value = null
          resolve(pet || null)
        }
      }, 50)

      // 30秒超时
      setTimeout(() => {
        clearInterval(checkSelected)
        if (petDialogVisible.value) {
          petDialogVisible.value = false
          selectedPetId.value = null
          resolve(null)
        }
      }, 30000)
    }
  })
}

// 确认选择宠物
function confirmPetSelection(pet: { id: string }) {
  selectedPetId.value = pet.id
}

function handleSelectSession(session: Session) {
  chatStore.setCurrentSession(session)
}

async function handleDeleteSession(sessionId: string) {
  await chatStore.deleteSession(sessionId)
  ElMessage.success('会话已删除')
}

async function handleSend(content: string) {
  await chatStore.sendMessageStream(content)
}

async function handleSendImage(file: File) {
  await chatStore.sendImage(file)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="chat-layout">
    <!-- 侧边栏 -->
    <aside
      class="sidebar"
      :style="{ width: isCollapsed ? '0px' : sidebarWidth + 'px' }"
    >
      <SessionList
        v-if="!isCollapsed"
        :sessions="chatStore.sessions"
        :pet-sessions="chatStore.petSessions"
        :normal-sessions="chatStore.normalSessions"
        :current-session-id="chatStore.currentSession?.id"
        @select="handleSelectSession"
        @create="handleCreateSession"
        @create-pet="handleCreatePetSession"
        @delete="handleDeleteSession"
      />
    </aside>

    <!-- 主内容区 -->
    <main class="chat-main">
      <!-- 顶栏 -->
      <header class="chat-header">
        <div class="header-left">
          <el-button
            :icon="isCollapsed ? 'Expand' : 'Fold'"
            text
            @click="isCollapsed = !isCollapsed"
          />
          <span class="header-title">
            {{ chatStore.currentSession?.title || 'PetMind' }}
          </span>
        </div>

        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" style="background: #667eea">
                {{ authStore.user?.username?.[0]?.toUpperCase() }}
              </el-avatar>
              <span class="username">{{ authStore.user?.username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/pets')">
                  宠物管理
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 聊天区域 -->
      <div class="chat-content" ref="chatContainer">
        <template v-if="chatStore.currentSession">
          <div v-if="chatStore.messages.length === 0" class="empty-chat">
            <div class="empty-icon">💬</div>
            <h3>开始新对话</h3>
            <p>描述您宠物的健康问题，我会尽力为您提供帮助</p>
            <div class="quick-questions">
              <el-tag
                v-for="q in ['我的猫最近呕吐怎么办？', '狗狗食欲不振是什么原因？', '猫咪掉毛严重正常吗？']"
                :key="q"
                class="quick-tag"
                @click="handleSend(q)"
              >
                {{ q }}
              </el-tag>
            </div>
          </div>

          <ChatMessage
            v-for="msg in chatStore.messages"
            :key="msg.id"
            :message="msg"
          />

          <div v-if="chatStore.loading" class="loading-indicator">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>AI 正在思考...</span>
          </div>
        </template>

        <div v-else class="no-session">
          <div class="empty-icon">🐾</div>
          <h3>欢迎使用 PetMind</h3>
          <p>选择一个会话或创建新会话开始聊天</p>
          <el-button type="primary" @click="handleCreateSession">
            新建会话
          </el-button>
        </div>
      </div>

      <!-- 输入区 -->
      <div v-if="chatStore.currentSession" class="chat-input">
        <ChatInput
          :loading="chatStore.loading"
          @send="handleSend"
          @send-image="handleSendImage"
        />
      </div>
    </main>

    <!-- 宠物选择对话框 -->
    <el-dialog
      v-model="petDialogVisible"
      title="选择宠物"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="pet-select-list">
        <el-card
          v-for="pet in petsStore.pets"
          :key="pet.id"
          class="pet-select-card"
          shadow="hover"
          @click="confirmPetSelection(pet)"
        >
          <div class="pet-card-content">
            <div class="pet-avatar">
              {{ pet.name.charAt(0) }}
            </div>
            <div class="pet-info">
              <div class="pet-name">{{ pet.name }}</div>
              <div class="pet-details">{{ pet.species }} · {{ pet.breed || '未知品种' }}</div>
            </div>
          </div>
        </el-card>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.chat-layout {
  height: 100vh;
  display: flex;
  overflow: hidden;
}

.sidebar {
  flex-shrink: 0;
  transition: width 0.3s;
  overflow: hidden;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  height: 60px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #eee;
  background: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #333;
}

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #fafbfc;
}

.empty-chat,
.no-session {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #666;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-chat h3,
.no-session h3 {
  margin: 0 0 8px;
  font-size: 20px;
  color: #333;
}

.empty-chat p,
.no-session p {
  margin: 0 0 24px;
  font-size: 14px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  max-width: 500px;
}

.quick-tag {
  cursor: pointer;
}

.quick-tag:hover {
  opacity: 0.8;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  color: #999;
  font-size: 14px;
}

.chat-input {
  flex-shrink: 0;
}

.pet-select-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pet-select-card {
  cursor: pointer;
  transition: all 0.3s;
}

.pet-select-card:hover {
  transform: translateY(-2px);
}

.pet-card-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.pet-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
}

.pet-info {
  flex: 1;
}

.pet-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.pet-details {
  font-size: 13px;
  color: #999;
  margin-top: 4px;
}
</style>
