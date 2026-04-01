<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import { ChatDotRound, User } from '@element-plus/icons-vue'
import type { Message } from '@/api/messages'

const props = defineProps<{
  message: Message
}>()

const isUser = computed(() => props.message.role === 'user')

// 渲染 Markdown 内容
const renderedContent = computed(() => {
  if (!props.message.content) return ''
  return marked(props.message.content)
})

const imageUrls = computed(() => {
  if (!props.message.image_urls) return []
  try {
    return JSON.parse(props.message.image_urls)
  } catch {
    return []
  }
})

const sources = computed(() => {
  if (!props.message.sources) return []
  try {
    return JSON.parse(props.message.sources)
  } catch {
    return []
  }
})

const formatTime = (time: string) => {
  const date = new Date(time)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div :class="['message', isUser ? 'message-user' : 'message-assistant']">
    <div class="message-avatar">
      <el-icon v-if="isUser" :size="24"><User /></el-icon>
      <el-icon v-else :size="24"><ChatDotRound /></el-icon>
    </div>

    <div class="message-content">
      <!-- 图片展示 -->
      <div v-if="imageUrls.length > 0" class="message-images">
        <el-image
          v-for="(url, index) in imageUrls"
          :key="index"
          :src="url"
          :preview-src-list="imageUrls"
          fit="cover"
          class="message-image"
        />
      </div>

      <!-- 文字内容 -->
      <div class="message-text" v-html="renderedContent"></div>

      <!-- 来源信息 -->
      <div v-if="sources.length > 0 && !isUser" class="message-sources">
        <div class="sources-label">参考来源：</div>
        <div
          v-for="(source, index) in sources"
          :key="index"
          class="source-item"
        >
          {{ source.source }}
        </div>
      </div>

      <!-- 时间 -->
      <div class="message-time">{{ formatTime(message.created_at) }}</div>
    </div>
  </div>
</template>

<style scoped>
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  animation: messageIn 0.3s ease-out;
}

@keyframes messageIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-user .message-avatar {
  background: #667eea;
  color: white;
}

.message-assistant .message-avatar {
  background: #f0f2f5;
  color: #666;
}

.message-content {
  max-width: 70%;
  min-width: 100px;
}

.message-user .message-content {
  text-align: right;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-break: break-word;
}

.message-user .message-text {
  background: #667eea;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-assistant .message-text {
  background: #f0f2f5;
  color: #333;
  border-bottom-left-radius: 4px;
}

/* Markdown 样式 */
.message-text :deep(h1),
.message-text :deep(h2),
.message-text :deep(h3) {
  margin: 0.5em 0;
  font-weight: 600;
}

.message-text :deep(h1) { font-size: 1.25em; }
.message-text :deep(h2) { font-size: 1.1em; }
.message-text :deep(h3) { font-size: 1em; }

.message-text :deep(p) {
  margin: 0.5em 0;
}

.message-text :deep(p:first-child) {
  margin-top: 0;
}

.message-text :deep(p:last-child) {
  margin-bottom: 0;
}

.message-text :deep(ul),
.message-text :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.message-text :deep(li) {
  margin: 0.25em 0;
}

.message-text :deep(strong) {
  font-weight: 600;
}

.message-text :deep(em) {
  font-style: italic;
}

.message-text :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: monospace;
}

.message-user .message-text :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

.message-text :deep(pre) {
  background: rgba(0, 0, 0, 0.05);
  padding: 1em;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.5em 0;
}

.message-user .message-text :deep(pre) {
  background: rgba(255, 255, 255, 0.15);
}

.message-text :deep(pre code) {
  background: none;
  padding: 0;
}

.message-text :deep(blockquote) {
  margin: 0.5em 0;
  padding: 0.5em 1em;
  border-left: 3px solid rgba(0, 0, 0, 0.2);
  background: rgba(0, 0, 0, 0.03);
  color: inherit;
}

.message-user .message-text :deep(blockquote) {
  border-left-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
}

.message-text :deep(a) {
  color: #667eea;
  text-decoration: none;
}

.message-text :deep(a:hover) {
  text-decoration: underline;
}

.message-user .message-text :deep(a) {
  color: #fff;
}

.message-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.message-image {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  cursor: pointer;
}

.message-sources {
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  font-size: 12px;
  color: #666;
}

.sources-label {
  font-weight: 500;
  margin-bottom: 4px;
}

.source-item {
  color: #667eea;
}

.message-time {
  margin-top: 4px;
  font-size: 11px;
  color: #999;
}
</style>
