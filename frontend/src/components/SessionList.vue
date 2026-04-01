<script setup lang="ts">
import { Plus, ChatDotRound, Delete } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import type { Session } from '@/api/sessions'

const props = defineProps<{
  sessions: Session[]
  currentSessionId?: string
}>()

const emit = defineEmits<{
  (e: 'select', session: Session): void
  (e: 'create'): void
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
      <el-button
        :icon="Plus"
        circle
        size="small"
        @click="emit('create')"
      />
    </div>

    <div class="session-items">
      <div
        v-for="session in sessions"
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

      <div v-if="sessions.length === 0" class="empty-state">
        <p>暂无会话</p>
        <el-button type="primary" @click="emit('create')">
          创建第一个会话
        </el-button>
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

.session-items {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
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

.session-icon {
  flex-shrink: 0;
}

.session-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.empty-state {
  padding: 32px 16px;
  text-align: center;
  color: #999;
}

.empty-state p {
  margin-bottom: 16px;
}
</style>
