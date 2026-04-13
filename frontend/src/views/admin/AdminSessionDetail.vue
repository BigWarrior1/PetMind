<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { adminApi, type Message } from '@/api/admin'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const messages = ref<Message[]>([])
const sessionId = route.params.id as string

async function fetchMessages() {
  loading.value = true
  try {
    messages.value = await adminApi.getSessionMessages(sessionId)
  } catch (error) {
    ElMessage.error('获取消息列表失败')
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/admin/sessions')
}

function formatTime(time: string) {
  return new Date(time).toLocaleString()
}

onMounted(() => {
  fetchMessages()
})
</script>

<template>
  <div class="session-detail">
    <div class="page-header">
      <el-button @click="goBack">返回列表</el-button>
      <h1 class="page-title">会话消息详情</h1>
    </div>

    <el-card v-loading="loading">
      <div class="messages-list">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message-item"
          :class="msg.role"
        >
          <div class="message-header">
            <el-tag :type="msg.role === 'user' ? 'primary' : 'success'" size="small">
              {{ msg.role === 'user' ? '用户' : '助手' }}
            </el-tag>
            <span class="message-time">{{ formatTime(msg.created_at) }}</span>
          </div>
          <div class="message-content">{{ msg.content }}</div>
          <div v-if="msg.sources && msg.sources !== '[]'" class="message-sources">
            <div class="sources-label">来源：</div>
            <div v-for="(source, idx) in JSON.parse(msg.sources)" :key="idx" class="source-item">
              {{ source.source || source }}
            </div>
          </div>
          <div v-if="msg.image_urls && msg.image_urls !== '[]'" class="message-images">
            <img
              v-for="(url, idx) in JSON.parse(msg.image_urls)"
              :key="idx"
              :src="url"
              class="message-image"
            />
          </div>
        </div>
      </div>

      <el-empty v-if="messages.length === 0 && !loading" description="暂无消息" />
    </el-card>
  </div>
</template>

<style scoped>
.session-detail {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 0 16px;
  color: #333;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  padding: 16px;
  border-radius: 8px;
  background: #f5f7fa;
}

.message-item.assistant {
  background: #e8f5e9;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.message-time {
  font-size: 12px;
  color: #999;
}

.message-content {
  line-height: 1.6;
  white-space: pre-wrap;
}

.message-sources {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #ccc;
}

.sources-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.source-item {
  font-size: 12px;
  color: #409eff;
}

.message-images {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.message-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
}
</style>
