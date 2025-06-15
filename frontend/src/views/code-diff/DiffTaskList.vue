<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">代码Diff任务</h1>
      <p class="page-description">管理代码差异对比任务</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>Diff任务列表</span>
          <el-button type="primary" @click="showCreateDialog">
            创建Diff任务
          </el-button>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-section mb-3">
        <el-form :model="filterForm" inline>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
              <el-option label="待执行" value="pending" />
              <el-option label="执行中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="仓库">
            <el-select v-model="filterForm.repositoryId" placeholder="全部仓库" clearable>
              <el-option label="核心交易系统" value="1" />
              <el-option label="支付系统" value="2" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="loadDiffTasks">搜索</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 任务表格 -->
      <el-table :data="diffTasks" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="repositoryName" label="仓库" />
        <el-table-column prop="compareType" label="对比类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.compareType === 'branch' ? 'primary' : 'success'">
              {{ scope.row.compareType === 'branch' ? '分支对比' : '提交对比' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sourceRef" label="源" />
        <el-table-column prop="targetRef" label="目标" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button
              v-if="scope.row.status === 'pending'"
              type="primary"
              size="small"
              @click="executeDiffTask(scope.row)"
              :loading="scope.row.executing"
            >
              执行
            </el-button>
            
            <el-button
              v-if="scope.row.status === 'completed'"
              type="success"
              size="small"
              @click="viewDiffContent(scope.row)"
            >
              查看Diff
            </el-button>
            
            <el-button
              type="text"
              size="small"
              @click="deleteDiffTask(scope.row)"
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
          @size-change="loadDiffTasks"
          @current-change="loadDiffTasks"
        />
      </div>
    </el-card>

    <!-- 创建Diff任务对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建代码Diff任务"
      width="600px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="120px"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="选择仓库" prop="repositoryId">
          <el-select v-model="createForm.repositoryId" placeholder="请选择仓库" style="width: 100%">
            <el-option label="核心交易系统" value="1" />
            <el-option label="支付系统" value="2" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="对比类型" prop="compareType">
          <el-radio-group v-model="createForm.compareType">
            <el-radio label="branch">分支对比</el-radio>
            <el-radio label="commit">提交对比</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="源分支/提交" prop="sourceRef">
          <el-input v-model="createForm.sourceRef" placeholder="如: feature/login 或 commit hash" />
        </el-form-item>
        
        <el-form-item label="目标分支/提交" prop="targetRef">
          <el-input v-model="createForm.targetRef" placeholder="如: main 或 commit hash" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createDiffTask" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- Diff内容查看对话框 -->
    <el-dialog
      v-model="diffContentDialogVisible"
      title="代码Diff内容"
      width="90%"
      class="diff-dialog"
    >
      <div class="diff-content">
        <pre v-if="currentDiffContent" class="diff-viewer">{{ currentDiffContent }}</pre>
        <div v-else class="empty-diff">暂无Diff内容</div>
      </div>
      
      <template #footer>
        <el-button @click="diffContentDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { CodeDiffTask, TaskStatus } from '@/types'

// 表单引用
const createFormRef = ref<FormInstance>()

// 加载状态
const loading = ref(false)
const creating = ref(false)

// 对话框状态
const createDialogVisible = ref(false)
const diffContentDialogVisible = ref(false)

// 当前查看的Diff内容
const currentDiffContent = ref('')

// 筛选表单
const filterForm = reactive({
  status: '',
  repositoryId: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 创建表单
const createForm = reactive({
  name: '',
  repositoryId: '',
  compareType: 'branch',
  sourceRef: '',
  targetRef: ''
})

// 表单验证规则
const createRules: FormRules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' }
  ],
  repositoryId: [
    { required: true, message: '请选择仓库', trigger: 'change' }
  ],
  sourceRef: [
    { required: true, message: '请输入源分支或提交', trigger: 'blur' }
  ],
  targetRef: [
    { required: true, message: '请输入目标分支或提交', trigger: 'blur' }
  ]
}

// Diff任务列表
const diffTasks = ref<(CodeDiffTask & { repositoryName?: string; executing?: boolean })[]>([])

// 获取状态标签类型
const getStatusTagType = (status: TaskStatus) => {
  const typeMap = {
    pending: 'info',
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
    running: '执行中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || '未知'
}

// 显示创建对话框
const showCreateDialog = () => {
  Object.assign(createForm, {
    name: '',
    repositoryId: '',
    compareType: 'branch',
    sourceRef: '',
    targetRef: ''
  })
  createDialogVisible.value = true
}

// 创建Diff任务
const createDiffTask = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    creating.value = true
    
    // TODO: 调用API创建Diff任务
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('Diff任务创建成功')
    createDialogVisible.value = false
    loadDiffTasks()
  } catch (error) {
    console.error('Create diff task failed:', error)
  } finally {
    creating.value = false
  }
}

// 执行Diff任务
const executeDiffTask = async (task: CodeDiffTask & { executing?: boolean }) => {
  try {
    task.executing = true
    
    // TODO: 调用API执行Diff任务
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success('Diff任务执行完成')
    loadDiffTasks()
  } catch (error) {
    console.error('Execute diff task failed:', error)
    ElMessage.error('Diff任务执行失败')
  } finally {
    task.executing = false
  }
}

// 查看Diff内容
const viewDiffContent = (task: CodeDiffTask) => {
  // 模拟Diff内容
  currentDiffContent.value = `diff --git a/src/login.js b/src/login.js
index 1234567..abcdefg 100644
--- a/src/login.js
+++ b/src/login.js
@@ -10,7 +10,7 @@ function login(username, password) {
   if (!username || !password) {
-    throw new Error('用户名和密码不能为空');
+    return { success: false, message: '用户名和密码不能为空' };
   }
   
   // 验证用户凭据
@@ -20,6 +20,10 @@ function login(username, password) {
   
   if (user && user.password === password) {
+    // 记录登录日志
+    console.log(\`用户 \${username} 于 \${new Date()} 登录\`);
+    
     return {
       success: true,
       token: generateToken(user.id),`
  
  diffContentDialogVisible.value = true
}

// 删除Diff任务
const deleteDiffTask = async (task: CodeDiffTask) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除Diff任务 "${task.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API删除任务
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('Diff任务删除成功')
    loadDiffTasks()
  } catch {
    // 用户取消
  }
}

// 重置筛选
const resetFilter = () => {
  Object.assign(filterForm, {
    status: '',
    repositoryId: ''
  })
  loadDiffTasks()
}

// 加载Diff任务列表
const loadDiffTasks = async () => {
  try {
    loading.value = true
    
    // TODO: 调用API加载Diff任务列表
    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    diffTasks.value = [
      {
        id: '1',
        name: '登录功能优化Diff',
        repositoryId: '1',
        repositoryName: '核心交易系统',
        sourceRef: 'feature/login-improvement',
        targetRef: 'main',
        compareType: 'branch',
        status: 'completed',
        diffContent: 'diff content here...',
        createdAt: '2024-01-15 14:30:00',
        updatedAt: '2024-01-15 14:30:00'
      },
      {
        id: '2',
        name: '支付接口修复Diff',
        repositoryId: '2',
        repositoryName: '支付系统',
        sourceRef: 'hotfix/payment-bug',
        targetRef: 'main',
        compareType: 'branch',
        status: 'pending',
        createdAt: '2024-01-15 13:45:00',
        updatedAt: '2024-01-15 13:45:00'
      }
    ]
    
    pagination.total = 2
  } catch (error) {
    console.error('Load diff tasks failed:', error)
    ElMessage.error('加载Diff任务列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDiffTasks()
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

.diff-dialog {
  .diff-content {
    max-height: 70vh;
    overflow-y: auto;
    
    .diff-viewer {
      background: #f8f9fa;
      padding: 16px;
      border-radius: 6px;
      font-family: 'Courier New', monospace;
      font-size: 12px;
      line-height: 1.4;
      white-space: pre-wrap;
      
      // Diff语法高亮
      :deep(.diff-added) {
        background-color: #d4edda;
        color: #155724;
      }
      
      :deep(.diff-removed) {
        background-color: #f8d7da;
        color: #721c24;
      }
    }
    
    .empty-diff {
      text-align: center;
      color: #999;
      padding: 40px 0;
    }
  }
}
</style>
