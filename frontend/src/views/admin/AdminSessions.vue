<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminApi, type Session } from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const loading = ref(false)
const sessions = ref<Session[]>([])
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0
})

async function fetchSessions() {
  loading.value = true
  try {
    const res = await adminApi.getSessions(pagination.value.page, pagination.value.pageSize)
    sessions.value = res.data
    pagination.value.total = res.total
    pagination.value.totalPages = res.total_pages
  } catch (error) {
    ElMessage.error('获取会话列表失败')
  } finally {
    loading.value = false
  }
}

async function handleDelete(session: Session) {
  try {
    await ElMessageBox.confirm(`确定要删除会话「${session.title}」吗？该操作会删除该会话的所有消息！`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await adminApi.deleteSession(session.id)
    ElMessage.success('删除成功')
    fetchSessions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function handleViewMessages(session: Session) {
  router.push(`/admin/sessions/${session.id}`)
}

function handlePageChange(page: number) {
  pagination.value.page = page
  fetchSessions()
}

onMounted(() => {
  fetchSessions()
})
</script>

<template>
  <div class="sessions-page">
    <h1 class="page-title">会话管理</h1>

    <el-card>
      <el-table :data="sessions" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="300" show-overflow-tooltip />
        <el-table-column prop="title" label="标题" width="200" show-overflow-tooltip />
        <el-table-column prop="user_id" label="用户ID" width="300" show-overflow-tooltip />
        <el-table-column prop="pet_id" label="宠物ID" width="150">
          <template #default="{ row }">
            {{ row.pet_id || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="summary" label="摘要" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.summary || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="最后活跃" width="180">
          <template #default="{ row }">
            {{ new Date(row.updated_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleViewMessages(row)">
              查看消息
            </el-button>
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
.sessions-page {
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
