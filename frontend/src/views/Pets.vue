<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { usePetsStore } from '@/stores/pets'
import PetCard from '@/components/PetCard.vue'
import type { Pet, CreatePetRequest, UpdatePetRequest } from '@/api/pets'
import {
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElOption,
  ElButton,
  type FormInstance,
  type FormRules
} from 'element-plus'

const router = useRouter()
const petsStore = usePetsStore()

const dialogVisible = ref(false)
const dialogTitle = ref('添加宠物')
const formRef = ref<FormInstance>()
const loading = ref(false)
const editingPet = ref<Pet | null>(null)

const form = ref<CreatePetRequest>({
  name: '',
  species: '',
  breed: '',
  age: '',
  weight: '',
  gender: '',
  birthday: '',
  notes: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入宠物名称', trigger: 'blur' }
  ],
  species: [
    { required: true, message: '请选择宠物种类', trigger: 'change' }
  ]
}

onMounted(() => {
  petsStore.fetchPets()
})

function openAddDialog() {
  editingPet.value = null
  dialogTitle.value = '添加宠物'
  form.value = {
    name: '',
    species: '',
    breed: '',
    age: '',
    weight: '',
    gender: '',
    birthday: '',
    notes: ''
  }
  dialogVisible.value = true
}

function openEditDialog(pet: Pet) {
  editingPet.value = pet
  dialogTitle.value = '编辑宠物'
  form.value = {
    name: pet.name,
    species: pet.species,
    breed: pet.breed,
    age: pet.age,
    weight: pet.weight,
    gender: pet.gender,
    birthday: pet.birthday,
    notes: pet.notes
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (editingPet.value) {
          await petsStore.updatePet(editingPet.value.id, form.value as UpdatePetRequest)
          ElMessage.success('宠物信息已更新')
        } else {
          await petsStore.createPet(form.value)
          ElMessage.success('宠物添加成功')
        }
        dialogVisible.value = false
      } catch {
        // 错误已在拦截器处理
      } finally {
        loading.value = false
      }
    }
  })
}

async function handleDelete(petId: string) {
  await petsStore.deletePet(petId)
  ElMessage.success('宠物已删除')
}
</script>

<template>
  <div class="pets-layout">
    <!-- 顶栏 -->
    <header class="pets-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" @click="router.push('/')">
          返回聊天
        </el-button>
        <h1 class="page-title">宠物管理</h1>
      </div>
      <el-button type="primary" :icon="Plus" @click="openAddDialog">
        添加宠物
      </el-button>
    </header>

    <!-- 宠物列表 -->
    <main class="pets-content">
      <div v-if="petsStore.pets.length === 0" class="empty-state">
        <div class="empty-icon">🐾</div>
        <h3>暂无宠物</h3>
        <p>添加您的宠物，开始智能健康问答</p>
        <el-button type="primary" @click="openAddDialog">
          添加第一个宠物
        </el-button>
      </div>

      <div v-else class="pets-grid">
        <PetCard
          v-for="pet in petsStore.pets"
          :key="pet.id"
          :pet="pet"
          @edit="openEditDialog"
          @delete="handleDelete"
        />
      </div>
    </main>

    <!-- 添加/编辑弹窗 -->
    <ElDialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <ElForm
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <ElFormItem label="名称" prop="name">
          <ElInput v-model="form.name" placeholder="请输入宠物名称" />
        </ElFormItem>

        <ElFormItem label="种类" prop="species">
          <ElSelect v-model="form.species" placeholder="请选择宠物种类" style="width: 100%">
            <ElOption label="狗" value="狗" />
            <ElOption label="猫" value="猫" />
            <ElOption label="其他" value="其他" />
          </ElSelect>
        </ElFormItem>

        <ElFormItem label="品种" prop="breed">
          <ElInput v-model="form.breed" placeholder="请输入品种" />
        </ElFormItem>

        <ElFormItem label="年龄" prop="age">
          <ElInput v-model="form.age" placeholder="如：2岁" />
        </ElFormItem>

        <ElFormItem label="体重" prop="weight">
          <ElInput v-model="form.weight" placeholder="如：5kg" />
        </ElFormItem>

        <ElFormItem label="性别" prop="gender">
          <ElSelect v-model="form.gender" placeholder="请选择性别" style="width: 100%">
            <ElOption label="公" value="公" />
            <ElOption label="母" value="母" />
            <ElOption label="未知" value="未知" />
          </ElSelect>
        </ElFormItem>

        <ElFormItem label="生日" prop="birthday">
          <ElInput v-model="form.birthday" placeholder="如：2022-01-01" />
        </ElFormItem>

        <ElFormItem label="备注" prop="notes">
          <ElInput
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </ElFormItem>
      </ElForm>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.pets-layout {
  min-height: 100vh;
  background: #f5f7fa;
}

.pets-header {
  padding: 16px 24px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.pets-content {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 12px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #333;
}

.empty-state p {
  margin: 0 0 24px;
  color: #999;
}

.pets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}
</style>
