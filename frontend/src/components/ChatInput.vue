<script setup lang="ts">
import { ref } from 'vue'
import { Picture, Promotion, Loading } from '@element-plus/icons-vue'

const emit = defineEmits<{
  (e: 'send', content: string): void
  (e: 'sendImage', file: File): void
}>()

const props = defineProps<{
  loading?: boolean
}>()

const inputText = ref('')
const fileInput = ref<HTMLInputElement>()

function handleSend() {
  if (!inputText.value.trim() || props.loading) return
  emit('send', inputText.value.trim())
  inputText.value = ''
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    emit('sendImage', file)
    target.value = '' // 重置以便选择同一文件
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="chat-input-container">
    <div class="input-wrapper">
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        style="display: none"
        @change="handleFileChange"
      />

      <el-button
        :icon="Picture"
        circle
        class="image-button"
        @click="triggerFileInput"
        :disabled="loading"
      />

      <el-input
        v-model="inputText"
        type="textarea"
        :rows="1"
        resize="none"
        placeholder="输入消息，Enter 发送..."
        class="input-area"
        :disabled="loading"
        @keydown="handleKeydown"
      />

      <el-button
        :icon="loading ? Loading : Promotion"
        type="primary"
        circle
        class="send-button"
        @click="handleSend"
        :disabled="loading || !inputText.trim()"
      />
    </div>

    <div class="input-hint">
      <span>按 Enter 发送，Shift + Enter 换行</span>
    </div>
  </div>
</template>

<style scoped>
.chat-input-container {
  padding: 16px;
  background: white;
  border-top: 1px solid #eee;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.image-button {
  flex-shrink: 0;
}

.input-area {
  flex: 1;
}

.input-area :deep(.el-textarea__inner) {
  border-radius: 20px;
  padding: 10px 16px;
  line-height: 1.5;
}

.send-button {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
}

.input-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
  text-align: center;
}
</style>
