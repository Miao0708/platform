<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">测试用例任务</h1>
      <p class="page-description">管理和查看所有测试用例生成任务</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务列表</span>
          <el-button type="primary" @click="$router.push('/test-case/create')">
            创建用例任务
          </el-button>
        </div>
      </template>
      
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="caseCount" label="用例数量" />
        <el-table-column prop="createdAt" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button
              v-if="scope.row.status === 'completed'"
              type="success"
              size="small"
              @click="viewCases(scope.row)"
            >
              查看用例
            </el-button>
            <el-button
              type="text"
              size="small"
              @click="deleteTask(scope.row)"
              style="color: #f56c6c"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { TestCaseTask, TaskStatus } from '@/types'

const router = useRouter()

const tasks = ref<(TestCaseTask & { caseCount?: number })[]>([])

const getStatusTagType = (status: TaskStatus) => {
  const typeMap = {
    pending: 'info',
    queued: 'warning', 
    running: 'primary',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: TaskStatus) => {
  const textMap = {
    pending: '待执行',
    queued: '排队中',
    running: '执行中', 
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || '未知'
}

const viewCases = (task: TestCaseTask) => {
  router.push(`/test-case/management?taskId=${task.id}`)
}

const deleteTask = async (task: TestCaseTask) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 "${task.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    ElMessage.success('任务删除成功')
    loadTasks()
  } catch {
    // 用户取消
  }
}

const loadTasks = async () => {
  // 模拟数据
  tasks.value = [
    {
      id: '1',
      name: '用户注册流程测试用例',
      requirementTextId: '1',
      promptTemplateId: '1',
      status: 'completed',
      caseCount: 15,
      createdAt: '2024-01-15 14:30:00',
      updatedAt: '2024-01-15 14:30:00'
    }
  ]
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
