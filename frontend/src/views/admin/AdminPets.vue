<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi, type Pet } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const pets = ref<Pet[]>([])
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0
})

async function fetchPets() {
  loading.value = true
  try {
    const res = await adminApi.getPets(pagination.value.page, pagination.value.pageSize)
    pets.value = res.data
    pagination.value.total = res.total
    pagination.value.totalPages = res.total_pages
  } catch (error) {
    ElMessage.error('获取宠物列表失败')
  } finally {
    loading.value = false
  }
}

async function handleDelete(pet: Pet) {
  try {
    await ElMessageBox.confirm(`确定要删除宠物「${pet.name}」吗？该操作会级联删除该宠物的所有会话和消息！`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await adminApi.deletePet(pet.id)
    ElMessage.success('删除成功')
    fetchPets()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handlePageChange(page: number) {
  pagination.value.page = page
  fetchPets()
}

onMounted(() => {
  fetchPets()
})
</script>

<template>
  <div class="pets-page">
    <h1 class="page-title">宠物管理</h1>

    <el-card>
      <el-table :data="pets" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="300" show-overflow-tooltip />
        <el-table-column prop="name" label="名字" width="120" />
        <el-table-column prop="species" label="种类" width="100">
          <template #default="{ row }">
            {{ row.species || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="breed" label="品种" width="150">
          <template #default="{ row }">
            {{ row.breed || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="100">
          <template #default="{ row }">
            {{ row.age || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="user_id" label="所属用户" width="300" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        class="pagination"
        background
        layout="prev, pager, next"
        :total="pagination.total"
        :page-size="pagination.pageSize"
        :current-page="pagination.page"
        @current-change="handlePageChange"
      />
    </el-card>
  </div>
</template>

<style scoped>
.pets-page {
  padding: 0;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 24px;
  color: #333;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>
