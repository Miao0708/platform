<template>
  <div class="test-point-list">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>测试点管理</h2>
        <p class="page-description">管理和生成需求的测试点，支持AI自动生成和手动创建</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          新建测试点
        </el-button>
        <el-button type="success" @click="showGenerateDialog">
          <el-icon><MagicStick /></el-icon>
          AI生成测试点
        </el-button>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-select v-model="filters.requirementId" placeholder="选择需求" clearable>
            <el-option
              v-for="req in requirements"
              :key="req.id"
              :label="req.name"
              :value="req.id"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.type" placeholder="测试类型" clearable>
            <el-option label="功能测试" value="functional" />
            <el-option label="性能测试" value="performance" />
            <el-option label="安全测试" value="security" />
            <el-option label="易用性测试" value="usability" />
            <el-option label="兼容性测试" value="compatibility" />
            <el-option label="集成测试" value="integration" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.priority" placeholder="优先级" clearable>
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.status" placeholder="状态" clearable>
            <el-option label="待执行" value="pending" />
            <el-option label="执行中" value="in_progress" />
            <el-option label="通过" value="passed" />
            <el-option label="失败" value="failed" />
            <el-option label="阻塞" value="blocked" />
            <el-option label="跳过" value="skipped" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索测试点名称或描述"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
      </el-row>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ stats.total }}</div>
              <div class="stat-label">总测试点</div>
            </div>
            <el-icon class="stat-icon"><Document /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card passed">
            <div class="stat-content">
              <div class="stat-number">{{ stats.passed }}</div>
              <div class="stat-label">通过</div>
            </div>
            <el-icon class="stat-icon"><SuccessFilled /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card failed">
            <div class="stat-content">
              <div class="stat-number">{{ stats.failed }}</div>
              <div class="stat-label">失败</div>
            </div>
            <el-icon class="stat-icon"><CircleCloseFilled /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card pending">
            <div class="stat-content">
              <div class="stat-number">{{ stats.pending }}</div>
              <div class="stat-label">待执行</div>
            </div>
            <el-icon class="stat-icon"><Clock /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 测试点列表 -->
    <el-card class="table-card">
      <el-table
        :data="filteredTestPoints"
        v-loading="loading"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="测试点名称" min-width="200">
          <template #default="{ row }">
            <div class="test-point-name">
              <span>{{ row.name }}</span>
              <el-tag
                :type="getTypeTagType(row.type)"
                size="small"
                class="type-tag"
              >
                {{ getTypeLabel(row.type) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignee" label="执行人" width="120" />
        <el-table-column prop="estimatedTime" label="预估时间" width="100">
          <template #default="{ row }">
            <span v-if="row.estimatedTime">{{ row.estimatedTime }}分钟</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewTestPoint(row)">
              查看
            </el-button>
            <el-button type="success" size="small" @click="executeTest(row)">
              执行
            </el-button>
            <el-dropdown @command="(command) => handleCommand(command, row)">
              <el-button size="small">
                更多<el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">编辑</el-dropdown-item>
                  <el-dropdown-item command="copy">复制</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 批量操作 -->
    <div v-if="selectedTestPoints.length > 0" class="batch-actions">
      <el-card>
        <div class="batch-content">
          <span>已选择 {{ selectedTestPoints.length }} 个测试点</span>
          <div class="batch-buttons">
            <el-button @click="batchAssign">批量分配</el-button>
            <el-button @click="batchUpdateStatus">批量更新状态</el-button>
            <el-button type="danger" @click="batchDelete">批量删除</el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 创建/编辑测试点对话框 -->
    <TestPointDialog
      v-model="dialogVisible"
      :test-point="currentTestPoint"
      :requirements="requirements"
      @saved="handleTestPointSaved"
    />

    <!-- AI生成测试点对话框 -->
    <AIGenerateDialog
      v-model="generateDialogVisible"
      :requirements="requirements"
      @generated="handleTestPointsGenerated"
    />

    <!-- 测试点详情对话框 -->
    <TestPointDetailDialog
      v-model="detailDialogVisible"
      :test-point="currentTestPoint"
      @updated="handleTestPointUpdated"
    />

    <!-- 测试执行对话框 -->
    <TestExecutionDialog
      v-model="executionDialogVisible"
      :test-point="currentTestPoint"
      @executed="handleTestExecuted"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  MagicStick,
  Search,
  Document,
  SuccessFilled,
  CircleCloseFilled,
  Clock,
  ArrowDown
} from '@element-plus/icons-vue'
import type { TestPoint, TestPointType, TestPriority, TestStatus, RequirementDocument } from '@/types/models'

// 导入子组件（这些组件需要后续创建）
// import TestPointDialog from './components/TestPointDialog.vue'
// import AIGenerateDialog from './components/AIGenerateDialog.vue'
// import TestPointDetailDialog from './components/TestPointDetailDialog.vue'
// import TestExecutionDialog from './components/TestExecutionDialog.vue'

// 响应式数据
const loading = ref(false)
const testPoints = ref<TestPoint[]>([])
const requirements = ref<RequirementDocument[]>([])
const selectedTestPoints = ref<TestPoint[]>([])

// 对话框状态
const dialogVisible = ref(false)
const generateDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const executionDialogVisible = ref(false)
const currentTestPoint = ref<TestPoint | null>(null)

// 筛选条件
const filters = ref({
  requirementId: '',
  type: '',
  priority: '',
  status: '',
  keyword: ''
})

// 分页
const pagination = ref({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 统计数据
const stats = computed(() => {
  const total = testPoints.value.length
  const passed = testPoints.value.filter(tp => tp.status === 'passed').length
  const failed = testPoints.value.filter(tp => tp.status === 'failed').length
  const pending = testPoints.value.filter(tp => tp.status === 'pending').length
  
  return { total, passed, failed, pending }
})

// 过滤后的测试点
const filteredTestPoints = computed(() => {
  let result = testPoints.value
  
  if (filters.value.requirementId) {
    result = result.filter(tp => tp.requirementId === filters.value.requirementId)
  }
  
  if (filters.value.type) {
    result = result.filter(tp => tp.type === filters.value.type)
  }
  
  if (filters.value.priority) {
    result = result.filter(tp => tp.priority === filters.value.priority)
  }
  
  if (filters.value.status) {
    result = result.filter(tp => tp.status === filters.value.status)
  }
  
  if (filters.value.keyword) {
    const keyword = filters.value.keyword.toLowerCase()
    result = result.filter(tp => 
      tp.name.toLowerCase().includes(keyword) ||
      tp.description.toLowerCase().includes(keyword)
    )
  }
  
  pagination.value.total = result.length
  
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  const end = start + pagination.value.pageSize
  
  return result.slice(start, end)
})

// 工具函数
const getTypeLabel = (type: TestPointType): string => {
  const labels = {
    functional: '功能',
    performance: '性能',
    security: '安全',
    usability: '易用性',
    compatibility: '兼容性',
    integration: '集成'
  }
  return labels[type] || type
}

const getTypeTagType = (type: TestPointType): string => {
  const types = {
    functional: 'primary',
    performance: 'warning',
    security: 'danger',
    usability: 'info',
    compatibility: 'success',
    integration: ''
  }
  return types[type] || ''
}

const getPriorityLabel = (priority: TestPriority): string => {
  const labels = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return labels[priority] || priority
}

const getPriorityTagType = (priority: TestPriority): string => {
  const types = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return types[priority] || ''
}

const getStatusLabel = (status: TestStatus): string => {
  const labels = {
    pending: '待执行',
    in_progress: '执行中',
    passed: '通过',
    failed: '失败',
    blocked: '阻塞',
    skipped: '跳过'
  }
  return labels[status] || status
}

const getStatusTagType = (status: TestStatus): string => {
  const types = {
    pending: 'info',
    in_progress: 'warning',
    passed: 'success',
    failed: 'danger',
    blocked: 'warning',
    skipped: ''
  }
  return types[status] || ''
}

// 事件处理
const showCreateDialog = () => {
  currentTestPoint.value = null
  dialogVisible.value = true
}

const showGenerateDialog = () => {
  generateDialogVisible.value = true
}

const viewTestPoint = (testPoint: TestPoint) => {
  currentTestPoint.value = testPoint
  detailDialogVisible.value = true
}

const executeTest = (testPoint: TestPoint) => {
  currentTestPoint.value = testPoint
  executionDialogVisible.value = true
}

const handleCommand = (command: string, testPoint: TestPoint) => {
  switch (command) {
    case 'edit':
      currentTestPoint.value = testPoint
      dialogVisible.value = true
      break
    case 'copy':
      copyTestPoint(testPoint)
      break
    case 'delete':
      deleteTestPoint(testPoint)
      break
  }
}

const copyTestPoint = async (testPoint: TestPoint) => {
  try {
    // TODO: 实现复制逻辑
    ElMessage.success('测试点复制成功')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const deleteTestPoint = async (testPoint: TestPoint) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试点吗？', '确认删除', {
      type: 'warning'
    })
    
    // TODO: 调用删除API
    testPoints.value = testPoints.value.filter(tp => tp.id !== testPoint.id)
    ElMessage.success('删除成功')
  } catch (error) {
    // 用户取消删除
  }
}

const handleSelectionChange = (selection: TestPoint[]) => {
  selectedTestPoints.value = selection
}

const batchAssign = () => {
  // TODO: 实现批量分配逻辑
  ElMessage.info('批量分配功能开发中...')
}

const batchUpdateStatus = () => {
  // TODO: 实现批量更新状态逻辑
  ElMessage.info('批量更新状态功能开发中...')
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedTestPoints.value.length} 个测试点吗？`, '确认删除', {
      type: 'warning'
    })
    
    // TODO: 调用批量删除API
    const selectedIds = selectedTestPoints.value.map(tp => tp.id)
    testPoints.value = testPoints.value.filter(tp => !selectedIds.includes(tp.id))
    selectedTestPoints.value = []
    ElMessage.success('批量删除成功')
  } catch (error) {
    // 用户取消删除
  }
}

const handleTestPointSaved = (testPoint: TestPoint) => {
  if (currentTestPoint.value) {
    // 更新现有测试点
    const index = testPoints.value.findIndex(tp => tp.id === testPoint.id)
    if (index > -1) {
      testPoints.value[index] = testPoint
    }
  } else {
    // 添加新测试点
    testPoints.value.unshift(testPoint)
  }
  dialogVisible.value = false
  ElMessage.success('保存成功')
}

const handleTestPointsGenerated = (generatedTestPoints: TestPoint[]) => {
  testPoints.value.unshift(...generatedTestPoints)
  generateDialogVisible.value = false
  ElMessage.success(`成功生成 ${generatedTestPoints.length} 个测试点`)
}

const handleTestPointUpdated = (testPoint: TestPoint) => {
  const index = testPoints.value.findIndex(tp => tp.id === testPoint.id)
  if (index > -1) {
    testPoints.value[index] = testPoint
  }
  detailDialogVisible.value = false
}

const handleTestExecuted = (testPoint: TestPoint) => {
  const index = testPoints.value.findIndex(tp => tp.id === testPoint.id)
  if (index > -1) {
    testPoints.value[index] = testPoint
  }
  executionDialogVisible.value = false
  ElMessage.success('测试执行完成')
}

const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  pagination.value.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.value.currentPage = page
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    
    // TODO: 调用API加载数据
    await Promise.all([
      loadTestPoints(),
      loadRequirements()
    ])
  } catch (error) {
    console.error('Load data failed:', error)
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

const loadTestPoints = async () => {
  // 模拟数据
  testPoints.value = [
    {
      id: '1',
      name: '用户登录功能测试',
      description: '验证用户能够正常登录系统，包括正确和错误的用户名密码组合',
      type: 'functional',
      priority: 'high',
      category: 'smoke',
      preconditions: ['系统正常运行', '用户账户已创建'],
      steps: [
        {
          id: '1',
          stepNumber: 1,
          action: '打开登录页面',
          expectedResult: '显示登录表单'
        },
        {
          id: '2',
          stepNumber: 2,
          action: '输入正确的用户名和密码',
          expectedResult: '输入框显示输入内容'
        },
        {
          id: '3',
          stepNumber: 3,
          action: '点击登录按钮',
          expectedResult: '成功登录并跳转到首页'
        }
      ],
      expectedResult: '用户成功登录系统',
      status: 'passed',
      requirementId: '1',
      assignee: '张三',
      estimatedTime: 15,
      tags: ['登录', '认证', '核心功能'],
      createdAt: '2024-01-15 10:30:00',
      updatedAt: '2024-01-15 10:30:00'
    },
    {
      id: '2',
      name: '密码错误登录测试',
      description: '验证输入错误密码时系统的处理',
      type: 'functional',
      priority: 'medium',
      category: 'regression',
      preconditions: ['系统正常运行', '用户账户已创建'],
      steps: [
        {
          id: '1',
          stepNumber: 1,
          action: '打开登录页面',
          expectedResult: '显示登录表单'
        },
        {
          id: '2',
          stepNumber: 2,
          action: '输入正确的用户名和错误的密码',
          expectedResult: '输入框显示输入内容'
        },
        {
          id: '3',
          stepNumber: 3,
          action: '点击登录按钮',
          expectedResult: '显示密码错误提示'
        }
      ],
      expectedResult: '显示错误提示，不允许登录',
      status: 'pending',
      requirementId: '1',
      assignee: '李四',
      estimatedTime: 10,
      tags: ['登录', '错误处理'],
      createdAt: '2024-01-15 11:00:00',
      updatedAt: '2024-01-15 11:00:00'
    }
  ]
}

const loadRequirements = async () => {
  // 模拟数据
  requirements.value = [
    {
      id: '1',
      name: '用户登录功能需求',
      originalContent: '用户需要能够登录系统...',
      optimizedContent: '## 用户登录功能需求...',
      source: 'manual',
      status: 'completed',
      createdAt: '2024-01-10 09:00:00',
      updatedAt: '2024-01-10 09:00:00'
    }
  ]
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.test-point-list {
  padding: 24px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    
    .header-left {
      h2 {
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }
      
      .page-description {
        margin: 0;
        color: #606266;
        font-size: 14px;
      }
    }
    
    .header-right {
      display: flex;
      gap: 12px;
    }
  }
  
  .filter-section {
    margin-bottom: 24px;
    padding: 20px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .stats-section {
    margin-bottom: 24px;
    
    .stat-card {
      position: relative;
      overflow: hidden;
      
      :deep(.el-card__body) {
        padding: 20px;
      }
      
      .stat-content {
        .stat-number {
          font-size: 32px;
          font-weight: 600;
          color: #303133;
          line-height: 1;
          margin-bottom: 8px;
        }
        
        .stat-label {
          font-size: 14px;
          color: #606266;
        }
      }
      
      .stat-icon {
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 32px;
        color: #ddd;
      }
      
      &.passed {
        border-left: 4px solid #67c23a;
        
        .stat-number {
          color: #67c23a;
        }
        
        .stat-icon {
          color: #67c23a;
          opacity: 0.3;
        }
      }
      
      &.failed {
        border-left: 4px solid #f56c6c;
        
        .stat-number {
          color: #f56c6c;
        }
        
        .stat-icon {
          color: #f56c6c;
          opacity: 0.3;
        }
      }
      
      &.pending {
        border-left: 4px solid #e6a23c;
        
        .stat-number {
          color: #e6a23c;
        }
        
        .stat-icon {
          color: #e6a23c;
          opacity: 0.3;
        }
      }
    }
  }
  
  .table-card {
    margin-bottom: 24px;
    
    .test-point-name {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .type-tag {
        flex-shrink: 0;
      }
    }
    
    .pagination-wrapper {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
  
  .batch-actions {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1000;
    
    .el-card {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .batch-content {
      display: flex;
      align-items: center;
      gap: 16px;
      
      .batch-buttons {
        display: flex;
        gap: 8px;
      }
    }
  }
}
</style>
