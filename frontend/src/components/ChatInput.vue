<script setup lang="ts">
import { ref } from 'vue'
import { Picture, Promotion, Loading, Close } from '@element-plus/icons-vue'

const emit = defineEmits<{
  (e: 'send', content: string): void
  (e: 'sendImage', file: File, question: string, dataUrl: string): void
}>()

const props = defineProps<{
  loading?: boolean
}>()

const inputText = ref('')
const fileInput = ref<HTMLInputElement>()
const previewImage = ref<{ file: File; dataUrl: string } | null>(null)

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    // 使用 FileReader 转换为 data URL
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImage.value = {
        file,
        dataUrl: e.target?.result as string
      }
    }
    reader.readAsDataURL(file)
    target.value = '' // 重置以便选择同一文件
  }
}

function removeImage() {
  previewImage.value = null
}

function handleSend() {
  if (props.loading) return

  // 如果有图片，先发送图片消息
  if (previewImage.value) {
    const question = inputText.value.trim() || '请分析这张图片中的宠物健康状况'
    emit('sendImage', previewImage.value.file, question, previewImage.value.dataUrl)
    previewImage.value = null
    inputText.value = ''
    return
  }

  // 只有文本
  if (!inputText.value.trim()) return
  emit('send', inputText.value.trim())
  inputText.value = ''
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
    <!-- 图片预览区域 -->
    <div v-if="previewImage" class="image-preview">
      <div class="preview-item">
        <img :src="previewImage.dataUrl" alt="预览图片" />
        <el-button
          :icon="Close"
          circle
          size="small"
          class="remove-btn"
          @click="removeImage"
        />
      </div>
    </div>

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
        :placeholder="previewImage ? '请输入您的问题...' : '输入消息，Enter 发送...'"
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
        :disabled="loading || (!inputText.trim() && !previewImage)"
      />
    </div>

    <div class="input-hint">
      <span v-if="previewImage">按 Enter 发送，Shift + Enter 换行</span>
      <span v-else>按 Enter 发送，Shift + Enter 换行</span>
    </div>
  </div>
</template>

<style scoped>
.chat-input-container {
  padding: 16px;
  background: white;
  border-top: 1px solid #eee;
}

.image-preview {
  margin-bottom: 12px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 8px;
}

.preview-item {
  position: relative;
  display: inline-block;
}

.preview-item img {
  max-width: 200px;
  max-height: 150px;
  border-radius: 8px;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 24px;
  height: 24px;
  padding: 0;
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