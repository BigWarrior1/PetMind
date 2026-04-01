<script setup lang="ts">
import { Plus, ChatDotRound, Delete, Present } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import type { Session } from '@/api/sessions'

const props = defineProps<{
  sessions: Session[]
  currentSessionId?: string
  petSessions: Session[]  // 宠物专属会话
  normalSessions: Session[]  // 普通会话
}>()

const emit = defineEmits<{
  (e: 'select', session: Session): void
  (e: 'create'): void
  (e: 'createPet'): void  // 创建宠物专属会话
  (e: 'delete', sessionId: string): void
}>()

async function handleDelete(session: Session, event: Event) {
  event.stopPropagation()
  try {
    await ElMessageBox.confirm(
      `确定删除会话 "${session.title}" 吗？`,
      '删除会话',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    emit('delete', session.id)
  } catch {
    // 用户取消
  }
}
</script>

<template>
  <div class="session-list">
    <div class="session-header">
      <span class="header-title">会话列表</span>
    </div>

    <div class="session-content">
      <!-- 宠物专属对话区域：上边 1/3 -->
      <div class="session-section pet-section">
        <div class="section-header">
          <span class="section-title">
            <el-icon><Present /></el-icon>
            宠物专属对话
          </span>
          <el-button
            :icon="Plus"
            circle
            size="small"
            @click="emit('createPet')"
          />
        </div>
        <div class="section-items">
          <div
            v-for="session in petSessions"
            :key="session.id"
            :class="['session-item', { active: session.id === currentSessionId }]"
            @click="emit('select', session)"
          >
            <el-icon :size="18" class="session-icon">
              <Present />
            </el-icon>
            <span class="session-title">{{ session.title }}</span>
            <el-button
              :icon="Delete"
              circle
              size="small"
              class="delete-button"
              @click="handleDelete(session, $event)"
            />
          </div>
          <div v-if="petSessions.length === 0" class="empty-section">
            <span>暂无宠物专属对话</span>
          </div>
        </div>
      </div>

      <!-- 普通对话区域：下边 2/3 -->
      <div class="session-section normal-section">
        <div class="section-header">
          <span class="section-title">
            <el-icon><ChatDotRound /></el-icon>
            普通对话
          </span>
          <el-button
            :icon="Plus"
            circle
            size="small"
            @click="emit('create')"
          />
        </div>
        <div class="section-items">
          <div
            v-for="session in normalSessions"
            :key="session.id"
            :class="['session-item', { active: session.id === currentSessionId }]"
            @click="emit('select', session)"
          >
            <el-icon :size="18" class="session-icon">
              <ChatDotRound />
            </el-icon>
            <span class="session-title">{{ session.title }}</span>
            <el-button
              :icon="Delete"
              circle
              size="small"
              class="delete-button"
              @click="handleDelete(session, $event)"
            />
          </div>
          <div v-if="normalSessions.length === 0" class="empty-section">
            <span>暂无普通对话</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.session-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
}

.session-header {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  font-weight: 600;
  color: #333;
}

.session-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.session-section {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.pet-section {
  flex: 0 0 33.33%;
  border-bottom: 1px solid #e4e7ed;
}

.normal-section {
  flex: 1;
}

.section-header {
  padding: 8px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ebeef5;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.section-items {
  flex: 1;
  overflow-y: auto;
  padding: 4px 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 2px;
}

.session-item:hover {
  background: #e4e7ed;
}

.session-item.active {
  background: #667eea;
  color: white;
}

.session-item.active .delete-button {
  opacity: 1;
}

.session-item.active .empty-section {
  color: rgba(255, 255, 255, 0.7);
}

.session-icon {
  flex-shrink: 0;
}

.session-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.delete-button {
  opacity: 0;
  flex-shrink: 0;
  --el-button-bg-color: transparent;
  --el-button-border-color: transparent;
  --el-button-hover-bg-color: rgba(255, 255, 255, 0.2);
  --el-button-hover-border-color: transparent;
}

.session-item.active .delete-button,
.session-item:hover .delete-button {
  opacity: 1;
}

.empty-section {
  padding: 16px 8px;
  text-align: center;
  color: #999;
  font-size: 12px;
}
</style>