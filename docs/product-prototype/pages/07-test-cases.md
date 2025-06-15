# 测试用例管理页面原型

## 页面概述
测试用例管理页面提供AI生成测试用例、测试用例管理、执行跟踪等功能，支持基于需求文档自动生成标准化测试用例。

## 页面布局

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            测试用例管理                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 操作栏: [新建任务] [生成用例] [批量操作▼] [导入] [导出] [模板管理]              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 筛选栏: [状态▼] [优先级▼] [类型▼] [需求文档▼] [执行状态▼] [搜索框]              │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────┐ ┌───────────────────────────────────────────┐ │
│ │        任务列表区域          │ │            测试用例详情区域                │ │
│ │                             │ │                                           │ │
│ │ ┌─────────────────────────┐ │ │ ┌───────────────────────────────────────┐ │ │
│ │ │ 📋 需求分析测试用例      │ │ │ │ 用例标题: 用户登录功能测试            │ │ │
│ │ │ 状态: ✅ 已完成         │ │ │ │ 优先级: [P1] 类型: [功能测试]         │ │ │
│ │ │ 需求: 用户管理需求      │ │ │ │ ─────────────────────────────────────│ │ │
│ │ │ 用例数: 15 生成时间: 2小时前 │ │ │ │ 📝 前置条件:                         │ │ │
│ │ │ [查看] [编辑] [执行]    │ │ │ │ • 系统已部署且正常运行                │ │ │
│ │ └─────────────────────────┘ │ │ │ • 用户数据库已初始化                  │ │ │
│ │                             │ │ │                                           │ │
│ │ ┌─────────────────────────┐ │ │ │ 🔄 测试步骤:                          │ │ │
│ │ │ 📊 API接口测试用例      │ │ │ │ 1. 打开登录页面                       │ │ │
│ │ │ 状态: 🔄 生成中         │ │ │ │ 2. 输入正确的用户名密码               │ │ │
│ │ │ 需求: API设计文档       │ │ │ │ 3. 点击登录按钮                       │ │ │
│ │ │ 进度: [████████░░] 80%  │ │ │ │ 4. 验证跳转到主页                     │ │ │
│ │ │ [取消] [查看日志]       │ │ │ │                                           │ │
│ │ └─────────────────────────┘ │ │ │ ✅ 预期结果:                          │ │ │
│ │                             │ │ │ • 登录成功，跳转到主页                │ │ │
│ │ ┌─────────────────────────┐ │ │ │ • 显示用户信息                        │ │ │
│ │ │ 🔒 安全测试用例         │ │ │ │                                           │ │
│ │ │ 状态: ❌ 生成失败       │ │ │ │ 🏷️ 标签: [登录, 认证, 功能]           │ │ │
│ │ │ 需求: 安全需求文档      │ │ │ │ ⏱️ 预估时间: 5分钟                     │ │ │
│ │ │ 错误: 模板配置错误      │ │ │ │                                           │ │
│ │ │ [重试] [查看错误]       │ │ │ │ [编辑] [复制] [删除] [执行]            │ │ │
│ │ └─────────────────────────┘ │ │ └───────────────────────────────────────┘ │ │
│ │                             │ │                                           │ │
│ │ [加载更多...]              │ │ ┌───────────────────────────────────────┐ │ │
│ └─────────────────────────────┘ │ │           AI分析建议                  │ │ │
│                                 │ │ • 建议增加异常情况测试                │ │ │
│                                 │ │ • 建议补充边界值测试                  │ │ │
│                                 │ │ • 测试覆盖率: 85%                     │ │ │
│                                 │ │ [查看详细分析]                        │ │ │
│                                 │ └───────────────────────────────────────┘ │ │
│                                 └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 数据模型

### TestCaseTask 接口
```typescript
interface TestCaseTask {
  id: string
  name: string
  description?: string
  requirementId: string
  requirementName: string
  promptTemplateId: string
  caseTemplateId?: string
  status: 'pending' | 'generating' | 'completed' | 'failed'
  progress: number
  testCases: TestCase[]
  generationConfig: {
    caseTypes: TestCaseType[]
    priorities: TestCasePriority[]
    maxCases: number
    includeEdgeCases: boolean
    includeNegativeCases: boolean
  }
  aiAnalysis?: {
    coverage: number
    suggestions: string[]
    qualityScore: number
    missingScenarios: string[]
  }
  statistics: {
    totalCases: number
    byType: Record<TestCaseType, number>
    byPriority: Record<TestCasePriority, number>
    estimatedTime: number
  }
  errorMessage?: string
  generatedAt?: string
  lastModified: string
  createdBy: string
}

interface TestCase {
  id: string
  taskId: string
  title: string
  description: string
  type: TestCaseType
  priority: TestCasePriority
  preconditions: string[]
  steps: TestStep[]
  expectedResult: string
  testData?: TestData[]
  tags: string[]
  estimatedTime: number
  actualResult?: string
  executionStatus: 'not_executed' | 'passed' | 'failed' | 'blocked'
  defects: string[]
  notes: string
  executedBy?: string
  executedAt?: string
}

interface TestStep {
  stepNumber: number
  action: string
  expectedResult: string
  testData?: string
  screenshot?: string
}

interface TestData {
  name: string
  value: string
  type: 'input' | 'expected' | 'boundary'
}

type TestCaseType = 'functional' | 'performance' | 'security' | 'usability' | 'compatibility' | 'api' | 'integration'
type TestCasePriority = 'P0' | 'P1' | 'P2' | 'P3'

interface CaseTemplate {
  id: string
  name: string
  description: string
  structure: {
    sections: TemplateSection[]
    defaultValues: Record<string, any>
  }
  isDefault: boolean
  isActive: boolean
  usage: number
  createdAt: string
}

interface TemplateSection {
  name: string
  field: string
  type: 'text' | 'textarea' | 'select' | 'multi-select' | 'steps'
  required: boolean
  options?: string[]
  placeholder?: string
}
```

### 状态管理

```typescript
interface TestCaseState {
  // 任务数据
  tasks: TestCaseTask[]
  currentTask: TestCaseTask | null
  currentTestCase: TestCase | null
  
  // 模板数据
  templates: CaseTemplate[]
  currentTemplate: CaseTemplate | null
  
  // UI状态
  loading: boolean
  generating: boolean
  error: string | null
  
  // 筛选和搜索
  filters: {
    status: string[]
    priority: TestCasePriority[]
    type: TestCaseType[]
    requirementId: string[]
    executionStatus: string[]
    search: string
  }
  
  // 分页
  pagination: {
    page: number
    pageSize: number
    total: number
  }
  
  // 选择状态
  selectedTasks: string[]
  selectedTestCases: string[]
  
  // 对话框状态
  dialogs: {
    createTask: boolean
    editTask: boolean
    generateCases: boolean
    templateManager: boolean
    batchExecution: boolean
    exportDialog: boolean
  }
}

interface TestCaseActions {
  // 任务管理
  loadTasks(): Promise<void>
  createTask(task: CreateTestCaseTaskRequest): Promise<void>
  updateTask(id: string, updates: Partial<TestCaseTask>): Promise<void>
  deleteTask(id: string): Promise<void>
  generateTestCases(taskId: string): Promise<void>
  
  // 测试用例管理
  updateTestCase(taskId: string, caseId: string, updates: Partial<TestCase>): Promise<void>
  deleteTestCase(taskId: string, caseId: string): Promise<void>
  executeTestCase(taskId: string, caseId: string, result: TestCaseExecution): Promise<void>
  batchExecuteTestCases(executions: BatchExecution): Promise<void>
  
  // 模板管理
  loadTemplates(): Promise<void>
  createTemplate(template: CreateTemplateRequest): Promise<void>
  updateTemplate(id: string, updates: Partial<CaseTemplate>): Promise<void>
  deleteTemplate(id: string): Promise<void>
  setDefaultTemplate(id: string): Promise<void>
  
  // 批量操作
  batchDeleteTasks(taskIds: string[]): Promise<void>
  batchGenerateCases(taskIds: string[]): Promise<void>
  
  // 导入导出
  exportTestCases(taskId: string, format: 'excel' | 'csv' | 'json'): Promise<void>
  importTestCases(file: File): Promise<void>
  
  // UI操作
  setCurrentTask(task: TestCaseTask | null): void
  setCurrentTestCase(testCase: TestCase | null): void
  updateFilters(filters: Partial<TestCaseState['filters']>): void
  setSelectedTasks(taskIds: string[]): void
  setSelectedTestCases(caseIds: string[]): void
  toggleDialog(dialog: keyof TestCaseState['dialogs']): void
}
```

## 页面交互逻辑

### 任务管理交互
```typescript
// 创建测试用例生成任务
async function createTestCaseTask() {
  const taskData = {
    name: taskForm.name,
    description: taskForm.description,
    requirementId: taskForm.requirementId,
    promptTemplateId: taskForm.promptTemplateId,
    caseTemplateId: taskForm.caseTemplateId,
    generationConfig: {
      caseTypes: taskForm.selectedTypes,
      priorities: taskForm.selectedPriorities,
      maxCases: taskForm.maxCases,
      includeEdgeCases: taskForm.includeEdgeCases,
      includeNegativeCases: taskForm.includeNegativeCases
    }
  }
  
  await testCaseStore.createTask(taskData)
  
  // 如果启用自动生成，立即开始生成
  if (taskForm.autoGenerate) {
    await generateTestCases(task.id)
  }
  
  showSuccessMessage('测试用例任务创建成功')
  closeCreateDialog()
}

// 生成测试用例
async function generateTestCases(taskId: string) {
  try {
    setGenerating(true)
    
    // 开始生成并监听进度
    const task = await testCaseStore.generateTestCases(taskId)
    
    // 轮询生成进度
    const progressInterval = setInterval(async () => {
      const updatedTask = await testCaseStore.getTask(taskId)
      
      if (updatedTask.status === 'completed') {
        clearInterval(progressInterval)
        setGenerating(false)
        showSuccessMessage(`测试用例生成完成，共生成 ${updatedTask.testCases.length} 个用例`)
        
        // 显示AI分析结果
        if (updatedTask.aiAnalysis) {
          showAIAnalysisDialog(updatedTask.aiAnalysis)
        }
      } else if (updatedTask.status === 'failed') {
        clearInterval(progressInterval)
        setGenerating(false)
        showErrorMessage(`生成失败: ${updatedTask.errorMessage}`)
      }
    }, 2000)
    
  } catch (error) {
    setGenerating(false)
    showErrorMessage('开始生成失败: ' + error.message)
  }
}

// 测试用例编辑
function editTestCase(testCase: TestCase) {
  currentEditingCase.value = { ...testCase }
  dialogs.editCase = true
}

async function saveTestCase() {
  const validation = validateTestCase(currentEditingCase.value)
  if (!validation.isValid) {
    showValidationErrors(validation.errors)
    return
  }
  
  await testCaseStore.updateTestCase(
    currentTask.value.id,
    currentEditingCase.value.id,
    currentEditingCase.value
  )
  
  showSuccessMessage('测试用例保存成功')
  dialogs.editCase = false
}
```

### 测试用例执行管理
```typescript
// 单个用例执行
async function executeTestCase(testCase: TestCase) {
  const executionData = {
    caseId: testCase.id,
    actualResult: executionForm.actualResult,
    executionStatus: executionForm.status,
    defects: executionForm.defects,
    notes: executionForm.notes,
    screenshots: executionForm.screenshots,
    executedBy: userStore.currentUser.id,
    executedAt: new Date().toISOString()
  }
  
  await testCaseStore.executeTestCase(
    currentTask.value.id,
    testCase.id,
    executionData
  )
  
  showSuccessMessage('测试用例执行结果已保存')
  
  // 更新任务统计
  updateTaskStatistics()
}

// 批量执行
async function batchExecuteTestCases() {
  const executions = selectedTestCases.value.map(caseId => ({
    caseId,
    status: batchExecutionForm.defaultStatus,
    notes: batchExecutionForm.notes,
    executedBy: userStore.currentUser.id
  }))
  
  await testCaseStore.batchExecuteTestCases({
    taskId: currentTask.value.id,
    executions
  })
  
  showSuccessMessage(`批量执行完成，共处理 ${executions.length} 个用例`)
  clearSelection()
}

// 生成测试报告
async function generateTestReport() {
  const reportData = {
    taskId: currentTask.value.id,
    includeDetails: reportForm.includeDetails,
    includeScreenshots: reportForm.includeScreenshots,
    includeStatistics: reportForm.includeStatistics,
    format: reportForm.format
  }
  
  const report = await testCaseStore.generateReport(reportData)
  
  if (reportForm.format === 'pdf') {
    downloadFile(report.url, `测试报告_${currentTask.value.name}.pdf`)
  } else {
    showReportPreview(report.content)
  }
}
```

### 模板管理
```typescript
// 模板创建
async function createCaseTemplate() {
  const templateData = {
    name: templateForm.name,
    description: templateForm.description,
    structure: {
      sections: templateForm.sections,
      defaultValues: templateForm.defaultValues
    },
    isDefault: templateForm.isDefault
  }
  
  await testCaseStore.createTemplate(templateData)
  showSuccessMessage('模板创建成功')
  dialogs.templateManager = false
}

// 模板预览
function previewTemplate(template: CaseTemplate) {
  const previewCase = generatePreviewCase(template)
  showTemplatePreview(previewCase)
}

function generatePreviewCase(template: CaseTemplate): TestCase {
  return {
    id: 'preview',
    taskId: 'preview',
    title: template.structure.defaultValues.title || '示例测试用例',
    description: template.structure.defaultValues.description || '这是一个模板预览',
    type: 'functional',
    priority: 'P1',
    preconditions: template.structure.defaultValues.preconditions || [],
    steps: template.structure.defaultValues.steps || [],
    expectedResult: template.structure.defaultValues.expectedResult || '',
    testData: [],
    tags: [],
    estimatedTime: 5,
    executionStatus: 'not_executed',
    defects: [],
    notes: ''
  }
}
```

## 响应式设计适配

### 桌面端布局 (≥1200px)
- 双栏布局：任务列表 + 用例详情
- 任务列表宽度：400px
- 用例详情区域：剩余空间
- 显示完整的操作按钮和筛选选项

### 平板端布局 (768px-1199px)
- 可切换的单栏布局
- 添加标签页切换：任务列表 | 用例详情
- 精简操作按钮，使用下拉菜单
- 筛选栏收缩为下拉选择器

### 移动端布局 (<768px)
- 全屏单栏布局
- 卡片式任务展示
- 底部导航栏
- 上滑显示用例详情
- 简化的创建表单

```typescript
// 响应式布局管理
const layout = computed(() => {
  if (screenWidth.value >= 1200) return 'desktop'
  if (screenWidth.value >= 768) return 'tablet'
  return 'mobile'
})

const showSidebar = computed(() => {
  return layout.value === 'desktop' || (layout.value === 'tablet' && activeTab.value === 'tasks')
})

const showDetails = computed(() => {
  return layout.value === 'desktop' || (layout.value !== 'desktop' && activeTab.value === 'details')
})
```

## 性能优化

### 虚拟滚动
```typescript
// 任务列表虚拟滚动
const virtualListProps = {
  height: 600,
  itemSize: 120,
  items: filteredTasks.value,
  renderItem: (item: TestCaseTask) => h(TaskCard, { task: item })
}
```

### 数据缓存
```typescript
// 任务数据缓存
const taskCache = new Map<string, TestCaseTask>()

async function getTask(id: string): Promise<TestCaseTask> {
  if (taskCache.has(id)) {
    return taskCache.get(id)!
  }
  
  const task = await api.getTask(id)
  taskCache.set(id, task)
  return task
}

// 缓存失效策略
function invalidateTaskCache(taskId: string) {
  taskCache.delete(taskId)
  // 触发重新加载
  loadTasks()
}
```

### 防抖搜索
```typescript
const debouncedSearch = useDebounceFn((searchText: string) => {
  filters.search = searchText
  loadTasks()
}, 300)
```

## 安全考虑

### 权限控制
```typescript
// 操作权限检查
const canCreateTask = computed(() => {
  return userStore.hasPermission('testcase:create')
})

const canEditTask = computed(() => {
  return userStore.hasPermission('testcase:edit') || 
         userStore.isOwner(currentTask.value?.createdBy)
})

const canDeleteTask = computed(() => {
  return userStore.hasPermission('testcase:delete') || 
         userStore.isOwner(currentTask.value?.createdBy)
})
```

### 数据验证
```typescript
function validateTestCase(testCase: Partial<TestCase>): ValidationResult {
  const errors: string[] = []
  
  if (!testCase.title?.trim()) {
    errors.push('测试用例标题不能为空')
  }
  
  if (!testCase.steps?.length) {
    errors.push('测试步骤不能为空')
  }
  
  if (!testCase.expectedResult?.trim()) {
    errors.push('预期结果不能为空')
  }
  
  if (testCase.steps) {
    testCase.steps.forEach((step, index) => {
      if (!step.action?.trim()) {
        errors.push(`第${index + 1}步操作描述不能为空`)
      }
    })
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}
```

## 用户体验优化

### 快捷键支持
- Ctrl+N: 创建新任务
- Ctrl+E: 编辑当前用例
- Ctrl+R: 执行当前用例
- Ctrl+S: 保存编辑
- Ctrl+D: 复制用例
- Delete: 删除选中项
- Ctrl+A: 全选
- Ctrl+F: 搜索

### 智能提示
```typescript
// 用例生成建议
function getGenerationSuggestions(requirement: string): string[] {
  const suggestions = []
  
  if (requirement.includes('登录')) {
    suggestions.push('建议生成正常登录、异常登录、边界值测试用例')
  }
  
  if (requirement.includes('API')) {
    suggestions.push('建议包含API参数验证、响应格式、错误处理测试')
  }
  
  if (requirement.includes('性能')) {
    suggestions.push('建议添加并发测试、压力测试、响应时间测试')
  }
  
  return suggestions
}

// 用例质量检查
function checkTestCaseQuality(testCase: TestCase): QualityReport {
  const issues = []
  const suggestions = []
  
  if (testCase.steps.length < 3) {
    issues.push('测试步骤过少，建议细化测试流程')
  }
  
  if (!testCase.preconditions.length) {
    issues.push('缺少前置条件，可能影响测试执行')
  }
  
  if (!testCase.tags.length) {
    suggestions.push('建议添加标签便于用例管理')
  }
  
  return {
    score: calculateQualityScore(testCase),
    issues,
    suggestions
  }
}
```

### 自动保存
```typescript
// 编辑自动保存
const autoSave = useDebounceFn(async () => {
  if (currentEditingCase.value && hasUnsavedChanges.value) {
    await testCaseStore.updateTestCase(
      currentTask.value.id,
      currentEditingCase.value.id,
      currentEditingCase.value
    )
    
    hasUnsavedChanges.value = false
    showToast('自动保存成功', 'success')
  }
}, 5000)

watch(currentEditingCase, autoSave, { deep: true })
``` 