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
            <el-button type="primary" @click="showCreateDialog('code_review')">
              创建代码评审任务
            </el-button>
            <el-button type="success" @click="showCreateDialog('test_case')">
              创建用例生成任务
            </el-button>
            <el-button type="warning" @click="showCreateDialog('requirement_testing')">
              创建需求测试任务
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-section mb-3">
        <el-form :model="filterForm" inline>
          <el-form-item label="任务类型">
            <el-select v-model="filterForm.type" placeholder="全部类型" clearable>
              <el-option label="代码评审" value="code_review" />
              <el-option label="用例生成" value="test_case" />
              <el-option label="需求测试" value="requirement_testing" />
            </el-select>
          </el-form-item>
          
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
        <el-table-column prop="type" label="类型" width="120">
          <template #default="scope">
            <el-tag :type="getTaskTypeTagType(scope.row.type)">
              {{ getTaskTypeText(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="codeDiffName" label="代码Diff">
          <template #default="scope">
            <span v-if="scope.row.type !== 'requirement_testing'">
              {{ scope.row.codeDiffName || '-' }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="requirementName" label="需求文档" />
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
              @click="executeTask(scope.row)"
              :loading="scope.row.executing"
            >
              执行
            </el-button>
            
            <el-button
              v-if="scope.row.status === 'completed' && scope.row.type === 'requirement_testing'"
              type="success"
              size="small"
              @click="viewRequirementTestResult(scope.row)"
            >
              查看详情
            </el-button>

            <el-button
              v-else-if="scope.row.status === 'completed'"
              type="success"
              size="small"
              @click="viewResult(scope.row)"
            >
              查看结果
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

    <!-- 创建流水线任务对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      :title="createDialogTitle"
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
        
        <el-form-item
          v-if="currentTaskType !== 'requirement_testing'"
          label="选择代码Diff"
          prop="codeDiffTaskId"
        >
          <el-select
            v-model="createForm.codeDiffTaskId"
            placeholder="请选择代码Diff任务"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="diff in availableDiffs"
              :key="diff.id"
              :label="diff.name"
              :value="diff.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="选择需求文档" prop="requirementDocumentId">
          <el-select 
            v-model="createForm.requirementDocumentId" 
            placeholder="请选择需求文档" 
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="req in availableRequirements"
              :key="req.id"
              :label="req.name"
              :value="req.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Prompt模板" prop="promptTemplateId">
          <el-select 
            v-model="createForm.promptTemplateId" 
            placeholder="请选择Prompt模板" 
            style="width: 100%"
          >
            <el-option
              v-for="template in availableTemplates"
              :key="template.id"
              :label="template.name"
              :value="template.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="知识库" prop="knowledgeBaseId">
          <el-select 
            v-model="createForm.knowledgeBaseId" 
            placeholder="可选择知识库" 
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="kb in availableKnowledgeBases"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createTask" :loading="creating">
          创建并执行
        </el-button>
      </template>
    </el-dialog>

    <!-- 结果查看对话框 -->
    <el-dialog
      v-model="resultDialogVisible"
      title="任务执行结果"
      width="80%"
      class="result-dialog"
    >
      <div class="result-content">
        <div v-if="currentTaskResult" v-html="renderedResult" class="result-viewer"></div>
        <div v-else class="empty-result">暂无结果</div>
      </div>
      
      <template #footer>
        <el-button @click="resultDialogVisible = false">关闭</el-button>
        <el-button v-if="currentTask?.type === 'test_case'" type="primary" @click="exportTestCases">
          导出用例
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { PipelineTask, TaskStatus, CodeDiffTask, RequirementDocument, PromptTemplate, KnowledgeBase } from '@/types'

const router = useRouter()

// 表单引用
const createFormRef = ref<FormInstance>()

// 加载状态
const loading = ref(false)
const creating = ref(false)

// 对话框状态
const createDialogVisible = ref(false)
const resultDialogVisible = ref(false)

// 当前任务类型
const currentTaskType = ref<'code_review' | 'test_case' | 'requirement_testing'>('code_review')

// 当前查看的任务和结果
const currentTask = ref<PipelineTask | null>(null)
const currentTaskResult = ref('')

// 筛选表单
const filterForm = reactive({
  type: '',
  status: '',
  name: ''
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
  codeDiffTaskId: '',
  requirementDocumentId: '',
  promptTemplateId: '',
  knowledgeBaseId: ''
})

// 可选数据
const availableDiffs = ref<CodeDiffTask[]>([])
const availableRequirements = ref<RequirementDocument[]>([])
const availableTemplates = ref<PromptTemplate[]>([])
const availableKnowledgeBases = ref<KnowledgeBase[]>([])

// 任务列表
const tasks = ref<(PipelineTask & { 
  codeDiffName?: string; 
  requirementName?: string; 
  executing?: boolean 
})[]>([])

// 创建对话框标题
const createDialogTitle = computed(() => {
  const titleMap = {
    code_review: '创建代码评审任务',
    test_case: '创建用例生成任务',
    requirement_testing: '创建需求测试任务'
  }
  return titleMap[currentTaskType.value] || '创建任务'
})

// 表单验证规则
const createRules = computed<FormRules>(() => {
  const rules: FormRules = {
    name: [
      { required: true, message: '请输入任务名称', trigger: 'blur' }
    ],
    requirementDocumentId: [
      { required: true, message: '请选择需求文档', trigger: 'change' }
    ],
    promptTemplateId: [
      { required: true, message: '请选择Prompt模板', trigger: 'change' }
    ]
  }

  // 只有非需求测试任务才需要代码Diff
  if (currentTaskType.value !== 'requirement_testing') {
    rules.codeDiffTaskId = [
      { required: true, message: '请选择代码Diff任务', trigger: 'change' }
    ]
  }

  return rules
})

// 渲染的结果内容
const renderedResult = computed(() => {
  if (!currentTaskResult.value) return ''
  
  // 简单的Markdown渲染
  return currentTaskResult.value
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
})

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

// 获取任务类型文本
const getTaskTypeText = (type: string) => {
  const typeMap = {
    code_review: '代码评审',
    test_case: '用例生成',
    requirement_testing: '需求测试'
  }
  return typeMap[type as keyof typeof typeMap] || type
}

// 获取任务类型标签类型
const getTaskTypeTagType = (type: string) => {
  const typeMap = {
    code_review: 'primary',
    test_case: 'success',
    requirement_testing: 'warning'
  }
  return typeMap[type as keyof typeof typeMap] || 'info'
}

// 显示创建对话框
const showCreateDialog = (type: 'code_review' | 'test_case' | 'requirement_testing') => {
  currentTaskType.value = type
  Object.assign(createForm, {
    name: '',
    codeDiffTaskId: '',
    requirementDocumentId: '',
    promptTemplateId: '',
    knowledgeBaseId: ''
  })
  createDialogVisible.value = true
  loadAvailableData()
}

// 加载可选数据
const loadAvailableData = async () => {
  try {
    // TODO: 并行加载所有可选数据
    // 模拟数据
    availableDiffs.value = [
      { id: '1', name: '登录功能优化Diff', repositoryId: '1', sourceRef: 'feature/login', targetRef: 'main', compareType: 'branch', status: 'completed', createdAt: '2024-01-15', updatedAt: '2024-01-15' }
    ]
    
    availableRequirements.value = [
      { id: '1', name: '用户登录功能需求', originalContent: '需求内容...', source: 'upload', status: 'completed', createdAt: '2024-01-15', updatedAt: '2024-01-15' }
    ]
    
    availableTemplates.value = [
      { id: '1', name: '代码评审-安全漏洞扫描', identifier: 'code_review_security', content: 'Prompt内容...', createdAt: '2024-01-15', updatedAt: '2024-01-15' }
    ]
    
    availableKnowledgeBases.value = [
      { id: '1', name: '项目设计文档', createdAt: '2024-01-15', updatedAt: '2024-01-15' }
    ]
  } catch (error) {
    console.error('Load available data failed:', error)
  }
}

// 创建任务
const createTask = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    creating.value = true
    
    // TODO: 调用API创建流水线任务
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success('流水线任务创建成功，正在执行中...')
    createDialogVisible.value = false
    loadTasks()
  } catch (error) {
    console.error('Create pipeline task failed:', error)
  } finally {
    creating.value = false
  }
}

// 执行任务
const executeTask = async (task: PipelineTask & { executing?: boolean }) => {
  try {
    task.executing = true
    
    // TODO: 调用API执行任务
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    ElMessage.success('任务执行完成')
    loadTasks()
  } catch (error) {
    console.error('Execute task failed:', error)
    ElMessage.error('任务执行失败')
  } finally {
    task.executing = false
  }
}

// 查看结果
const viewResult = (task: PipelineTask) => {
  currentTask.value = task
  
  // 模拟结果内容
  if (task.type === 'code_review') {
    currentTaskResult.value = `# 代码评审报告

## 总体评价
本次代码变更主要涉及用户登录模块的安全性改进，整体代码质量良好。

## 发现的问题

### 1. 安全问题
- **密码明文传输**: 在登录接口中发现密码以明文形式传输
- **SQL注入风险**: 用户名参数直接拼接到SQL语句中

### 2. 性能问题
- **数据库连接未释放**: 在某些异常情况下，数据库连接可能未正确释放

## 建议改进
1. 使用参数化查询防止SQL注入
2. 实现密码加密传输机制
3. 添加数据库连接池管理`
  } else if (task.type === 'test_case') {
    currentTaskResult.value = `# 测试用例生成结果

## 生成的测试用例

### 用例1: 正常登录流程
**前置条件**: 用户已注册，系统正常运行
**测试步骤**:
1. 打开登录页面
2. 输入正确的用户名和密码
3. 点击登录按钮
**预期结果**: 登录成功，跳转到首页

### 用例2: 错误密码登录
**前置条件**: 用户已注册，系统正常运行
**测试步骤**:
1. 打开登录页面
2. 输入正确的用户名和错误的密码
3. 点击登录按钮
**预期结果**: 显示密码错误提示`
  } else if (task.type === 'requirement_testing') {
    currentTaskResult.value = `# 需求测试分析报告

## 测试概览
- **需求名称**: 用户登录功能需求
- **生成时间**: 2024-01-15 15:30:00
- **测试点总数**: 12个
- **覆盖类型**: 功能测试、安全测试、性能测试、易用性测试

## 测试点分布
- **功能测试**: 6个 (50%)
- **安全测试**: 3个 (25%)
- **性能测试**: 2个 (17%)
- **易用性测试**: 1个 (8%)

## 优先级分布
- **高优先级**: 4个
- **中优先级**: 6个
- **低优先级**: 2个

## 生成的测试点

### 1. 用户正常登录测试
**类型**: 功能测试 | **优先级**: 高
**描述**: 验证用户使用正确的用户名和密码能够成功登录系统
**前置条件**:
- 系统正常运行
- 用户账户已创建并激活
**测试步骤**:
1. 打开登录页面
2. 输入有效的用户名
3. 输入正确的密码
4. 点击登录按钮
**预期结果**: 用户成功登录，跳转到系统首页

### 2. 密码错误登录测试
**类型**: 功能测试 | **优先级**: 高
**描述**: 验证用户输入错误密码时系统的处理
**前置条件**:
- 系统正常运行
- 用户账户已创建
**测试步骤**:
1. 打开登录页面
2. 输入有效的用户名
3. 输入错误的密码
4. 点击登录按钮
**预期结果**: 显示"用户名或密码错误"提示，不允许登录

### 3. SQL注入攻击测试
**类型**: 安全测试 | **优先级**: 高
**描述**: 验证登录接口对SQL注入攻击的防护能力
**前置条件**:
- 系统正常运行
**测试步骤**:
1. 打开登录页面
2. 在用户名字段输入SQL注入代码: admin'; DROP TABLE users; --
3. 输入任意密码
4. 点击登录按钮
**预期结果**: 系统拒绝登录，不执行恶意SQL代码

### 4. 登录性能测试
**类型**: 性能测试 | **优先级**: 中
**描述**: 验证登录接口的响应时间
**前置条件**:
- 系统正常运行
- 网络环境稳定
**测试步骤**:
1. 记录开始时间
2. 执行正常登录流程
3. 记录登录完成时间
**预期结果**: 登录响应时间不超过2秒

## 测试建议
1. **优先执行高优先级测试点**，确保核心功能正常
2. **安全测试**应在生产环境部署前完成
3. **性能测试**建议在接近生产环境的测试环境中执行
4. **建议增加边界值测试**，如超长用户名、特殊字符等

## 风险评估
- **高风险**: SQL注入漏洞可能导致数据泄露
- **中风险**: 密码策略不当可能影响账户安全
- **低风险**: 用户体验问题可能影响用户满意度`
  }
  
  resultDialogVisible.value = true
}

// 查看需求测试结果详情
const viewRequirementTestResult = (task: PipelineTask) => {
  // 跳转到需求测试结果详情页面
  router.push(`/pipelines/requirement-test/${task.id}`)
}

// 导出测试用例
const exportTestCases = () => {
  // TODO: 实现导出功能
  ElMessage.success('测试用例导出功能开发中')
}

// 删除任务
const deleteTask = async (task: PipelineTask) => {
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
    type: '',
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
        type: 'code_review',
        codeDiffTaskId: '1',
        requirementDocumentId: '1',
        promptTemplateId: '1',
        status: 'completed',
        codeDiffName: '登录功能优化Diff',
        requirementName: '用户登录功能需求',
        createdAt: '2024-01-15 14:30:00',
        updatedAt: '2024-01-15 14:30:00'
      },
      {
        id: '2',
        name: '支付流程测试用例生成',
        type: 'test_case',
        codeDiffTaskId: '2',
        requirementDocumentId: '2',
        promptTemplateId: '2',
        status: 'running',
        codeDiffName: '支付接口修复Diff',
        requirementName: '支付流程需求',
        createdAt: '2024-01-15 13:45:00',
        updatedAt: '2024-01-15 13:45:00'
      },
      {
        id: '3',
        name: '用户登录需求测试分析',
        type: 'requirement_testing',
        requirementDocumentId: '1',
        promptTemplateId: '3',
        status: 'completed',
        requirementName: '用户登录功能需求',
        createdAt: '2024-01-15 15:30:00',
        updatedAt: '2024-01-15 15:30:00'
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
  
  .header-actions {
    display: flex;
    gap: 8px;
  }
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

.result-dialog {
  .result-content {
    max-height: 70vh;
    overflow-y: auto;
    
    .result-viewer {
      line-height: 1.6;
      
      :deep(code) {
        background: #f5f5f5;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
      }
      
      :deep(strong) {
        font-weight: 600;
      }
      
      :deep(em) {
        font-style: italic;
      }
    }
    
    .empty-result {
      text-align: center;
      color: #999;
      padding: 40px 0;
    }
  }
}
</style>
