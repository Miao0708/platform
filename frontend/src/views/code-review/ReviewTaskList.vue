<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">流水线任务</h1>
      <p class="page-description">管理代码评审和测试用例生成流水线任务</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>流水线任务列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="showCreateDialog">
              创建代码评审任务
            </el-button>
            <el-button type="success" @click="showCreateTestCaseDialog">
              创建用例生成任务
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-section mb-3">
        <el-form :model="filterForm" inline>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
              <el-option label="待执行" value="pending" />
              <el-option label="排队中" value="queued" />
              <el-option label="执行中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="任务名称">
            <el-input
              v-model="filterForm.name"
              placeholder="请输入任务名称"
              clearable
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="loadTasks">搜索</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 任务表格 -->
      <el-table :data="tasks" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="repositoryAlias" label="仓库" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button
              v-if="scope.row.status === 'pending'"
              type="primary"
              size="small"
              @click="executeTask(scope.row)"
              :loading="scope.row.executing"
            >
              执行
            </el-button>
            
            <el-button
              v-if="scope.row.status === 'completed'"
              type="success"
              size="small"
              @click="viewReport(scope.row)"
            >
              查看报告
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
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadTasks"
          @current-change="loadTasks"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ReviewTask, TaskStatus } from '@/types'

const router = useRouter()

// 加载状态
const loading = ref(false)

// 筛选表单
const filterForm = reactive({
  status: '',
  name: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 任务列表
const tasks = ref<(ReviewTask & { repositoryAlias?: string; executing?: boolean })[]>([])

// 获取状态标签类型
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

// 获取状态文本
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

// 执行任务
const executeTask = async (task: ReviewTask & { executing?: boolean }) => {
  try {
    task.executing = true
    
    // TODO: 调用API执行任务
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success('任务已开始执行')
    loadTasks()
  } catch (error) {
    console.error('Execute task failed:', error)
    ElMessage.error('任务执行失败')
  } finally {
    task.executing = false
  }
}

// 查看报告
const viewReport = (task: ReviewTask) => {
  router.push(`/code-review/report/${task.id}`)
}

// 删除任务
const deleteTask = async (task: ReviewTask) => {
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
    
    // TODO: 调用API删除任务
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('任务删除成功')
    loadTasks()
  } catch {
    // 用户取消
  }
}

// 重置筛选
const resetFilter = () => {
  Object.assign(filterForm, {
    status: '',
    name: ''
  })
  loadTasks()
}

// 加载任务列表
const loadTasks = async () => {
  try {
    loading.value = true
    
    // TODO: 调用API加载任务列表
    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    tasks.value = [
      {
        id: '1',
        name: '用户登录模块代码评审',
        codeDiffId: '1',
        requirementTextId: '1',
        promptTemplateId: '1',
        status: 'completed',
        repositoryAlias: '核心交易系统',
        createdAt: '2024-01-15 14:30:00',
        updatedAt: '2024-01-15 14:30:00'
      },
      {
        id: '2',
        name: '支付流程安全评审',
        codeDiffId: '2',
        requirementTextId: '2',
        promptTemplateId: '1',
        status: 'running',
        repositoryAlias: '支付系统',
        createdAt: '2024-01-15 13:45:00',
        updatedAt: '2024-01-15 13:45:00'
      },
      {
        id: '3',
        name: '数据库连接模块评审',
        codeDiffId: '3',
        requirementTextId: '3',
        promptTemplateId: '1',
        status: 'pending',
        repositoryAlias: '核心交易系统',
        createdAt: '2024-01-15 12:20:00',
        updatedAt: '2024-01-15 12:20:00'
      }
    ]
    
    pagination.total = 3
  } catch (error) {
    console.error('Load tasks failed:', error)
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
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

.filter-section {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>
