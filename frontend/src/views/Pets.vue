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

const speciesOptions = [
  { value: '狗', label: '🐶 狗' },
  { value: '猫', label: '🐱 猫' },
  { value: '兔子', label: '🐰 兔子' },
  { value: '仓鼠', label: '🐹 仓鼠' },
  { value: '龙猫', label: '🐭 龙猫' },
  { value: '荷兰猪', label: '🐷 荷兰猪' },
  { value: '鸟类', label: '🐦 鸟类' },
  { value: '乌龟', label: '🐢 乌龟' },
  { value: '守宫', label: '🦎 守宫' },
  { value: '蛇', label: '🐍 蛇' },
  { value: '鱼', label: '🐟 鱼' },
  { value: '其他', label: '🐾 其他' }
]

const genderOptions = [
  { value: '公', label: '公' },
  { value: '母', label: '母' },
  { value: '未知', label: '未知' }
]

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
          ElMessage.success('添加成功')
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
  <div class="pets-page">
    <!-- 顶栏 -->
    <header class="page-header">
      <div class="header-left">
        <el-button text @click="router.push('/')">
          <ArrowLeft style="margin-right: 4px" />
          返回
        </el-button>
        <h1 class="page-title">宠物档案</h1>
      </div>
      <el-button type="primary" @click="openAddDialog">
        <Plus style="margin-right: 4px" />
        添加宠物
      </el-button>
    </header>

    <!-- 内容区 -->
    <main class="page-content">
      <!-- 空状态 -->
      <div v-if="petsStore.pets.length === 0" class="empty-state">
        <div class="empty-icon">🐾</div>
        <h3>还没有宠物</h3>
        <p>添加宠物后，可以获得专属的健康顾问服务</p>
        <el-button type="primary" @click="openAddDialog">添加宠物</el-button>
      </div>

      <!-- 宠物列表 -->
      <div v-else class="pets-list">
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
      width="420px"
      :close-on-click-modal="false"
      class="pet-dialog"
    >
      <ElForm
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
      >
        <ElFormItem label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入宠物名称" />
        </ElFormItem>

        <ElFormItem label="种类" prop="species">
          <el-select v-model="form.species" placeholder="请选择" style="width: 100%">
            <el-option v-for="item in speciesOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </ElFormItem>

        <ElFormItem label="品种">
          <el-input v-model="form.breed" placeholder="如：金毛、橘猫" />
        </ElFormItem>

        <div class="form-row">
          <ElFormItem label="年龄" class="form-half">
            <el-input v-model="form.age" placeholder="2岁" />
          </ElFormItem>
          <ElFormItem label="体重" class="form-half">
            <el-input v-model="form.weight" placeholder="5kg" />
          </ElFormItem>
        </div>

        <ElFormItem label="性别">
          <el-select v-model="form.gender" placeholder="请选择" style="width: 100%">
            <el-option v-for="item in genderOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </ElFormItem>

        <ElFormItem label="生日">
          <el-input v-model="form.birthday" placeholder="如：2022-01-01" />
        </ElFormItem>

        <ElFormItem label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="记录一些备注信息" />
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
.pets-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.page-header {
  position: sticky;
  top: 0;
  z-index: 10;
  padding: 16px 24px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #eee;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.page-content {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #fff;
  border-radius: 12px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.empty-state p {
  margin: 0 0 20px;
  color: #999;
  font-size: 14px;
}

.pets-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

/* Dialog Styles */
:deep(.pet-dialog) {
  border-radius: 12px;
}

:deep(.pet-dialog .el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
  margin: 0;
}

:deep(.pet-dialog .el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

:deep(.pet-dialog .el-dialog__body) {
  padding: 24px;
}

:deep(.pet-dialog .el-dialog__footer) {
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-half {
  flex: 1;
}
</style>