<script setup lang="ts">
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import type { Pet } from '@/api/pets'

// Icons are used via template, keep imports for icon components

const props = defineProps<{
  pet: Pet
}>()

const emit = defineEmits<{
  (e: 'edit', pet: Pet): void
  (e: 'delete', petId: string): void
}>()

async function handleDelete() {
  try {
    await ElMessageBox.confirm(
      `确定删除宠物 "${props.pet.name}" 吗？`,
      '删除宠物',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    emit('delete', props.pet.id)
  } catch {
    // 用户取消
  }
}
</script>

<template>
  <el-card class="pet-card" shadow="hover">
    <div class="pet-header">
      <div class="pet-avatar">
        {{ pet.species === '猫' ? '🐱' : pet.species === '狗' ? '🐕' : '🐾' }}
      </div>
      <div class="pet-info">
        <h3 class="pet-name">{{ pet.name }}</h3>
        <span class="pet-species">{{ pet.species || '未知' }} · {{ pet.breed || '未知品种' }}</span>
      </div>
    </div>

    <div class="pet-details">
      <div v-if="pet.age" class="detail-item">
        <span class="detail-label">年龄</span>
        <span class="detail-value">{{ pet.age }}</span>
      </div>
      <div v-if="pet.weight" class="detail-item">
        <span class="detail-label">体重</span>
        <span class="detail-value">{{ pet.weight }}</span>
      </div>
      <div v-if="pet.gender" class="detail-item">
        <span class="detail-label">性别</span>
        <span class="detail-value">{{ pet.gender }}</span>
      </div>
    </div>

    <div v-if="pet.notes" class="pet-notes">
      {{ pet.notes }}
    </div>

    <div class="pet-actions">
      <el-button
        :icon="Edit"
        size="small"
        @click="emit('edit', pet)"
      >
        编辑
      </el-button>
      <el-button
        :icon="Delete"
        size="small"
        type="danger"
        @click="handleDelete"
      >
        删除
      </el-button>
    </div>
  </el-card>
</template>

<style scoped>
.pet-card {
  border-radius: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.pet-card:hover {
  transform: translateY(-2px);
}

.pet-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.pet-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.pet-info {
  flex: 1;
}

.pet-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.pet-species {
  font-size: 13px;
  color: #999;
}

.pet-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.detail-item {
  text-align: center;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 8px;
}

.detail-label {
  display: block;
  font-size: 11px;
  color: #999;
  margin-bottom: 2px;
}

.detail-value {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.pet-notes {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
  line-height: 1.5;
}

.pet-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
