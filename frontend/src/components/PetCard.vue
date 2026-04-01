<script setup lang="ts">
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import type { Pet } from '@/api/pets'

const props = defineProps<{
  pet: Pet
}>()

const emit = defineEmits<{
  (e: 'edit', pet: Pet): void
  (e: 'delete', petId: string): void
}>()

function getSpeciesIcon(species: string): string {
  switch (species) {
    case '狗': return '🐶'
    case '猫': return '🐱'
    case '兔子': return '🐰'
    case '仓鼠': return '🐹'
    case '龙猫': return '🐭'
    case '荷兰猪': return '🐷'
    case '鸟类': return '🐦'
    case '乌龟': return '🐢'
    case '守宫': return '🦎'
    case '蛇': return '🐍'
    case '鱼': return '🐟'
    default: return '🐾'
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm(
      `确定删除宠物 "${props.pet.name}" 吗？相关会话也会被删除。`,
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
  <div class="pet-card">
    <div class="card-header">
      <div class="pet-avatar">
        {{ getSpeciesIcon(pet.species) }}
      </div>
      <div class="pet-info">
        <h3 class="pet-name">{{ pet.name }}</h3>
        <span class="pet-species">{{ pet.species }}{{ pet.breed ? ' · ' + pet.breed : '' }}</span>
      </div>
    </div>

    <div class="card-details" v-if="pet.age || pet.weight || pet.gender">
      <div class="detail-item" v-if="pet.age">
        <span class="detail-label">年龄</span>
        <span class="detail-value">{{ pet.age }}</span>
      </div>
      <div class="detail-item" v-if="pet.weight">
        <span class="detail-label">体重</span>
        <span class="detail-value">{{ pet.weight }}</span>
      </div>
      <div class="detail-item" v-if="pet.gender">
        <span class="detail-label">性别</span>
        <span class="detail-value">{{ pet.gender }}</span>
      </div>
    </div>

    <div class="card-notes" v-if="pet.notes">
      {{ pet.notes }}
    </div>

    <div class="card-actions">
      <el-button size="small" @click="emit('edit', pet)">
        <Edit style="margin-right: 4px" />
        编辑
      </el-button>
      <el-button size="small" type="danger" @click="handleDelete">
        <Delete style="margin-right: 4px" />
        删除
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.pet-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #eee;
  transition: box-shadow 0.2s;
}

.pet-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.pet-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.pet-info {
  flex: 1;
}

.pet-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.pet-species {
  font-size: 13px;
  color: #999;
}

.card-details {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-top: 1px solid #f5f5f5;
  border-bottom: 1px solid #f5f5f5;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 12px;
  color: #999;
}

.detail-value {
  font-size: 14px;
  color: #1a1a1a;
  font-weight: 500;
}

.card-notes {
  padding: 12px 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.card-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding-top: 12px;
}
</style>