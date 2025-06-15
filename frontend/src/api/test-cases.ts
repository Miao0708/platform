import { api } from './index'

// 任务状态类型
export type TaskStatus = 'pending' | 'queued' | 'running' | 'completed' | 'failed'

// 测试用例优先级
export type TestCasePriority = 'P0' | 'P1' | 'P2' | 'P3'

// 测试用例类型
export type TestCaseType = 'functional' | 'performance' | 'security' | 'usability' | 'compatibility'

// 测试用例接口
export interface TestCase {
  id: string
  title: string
  description: string
  preconditions: string
  steps: string
  expected_result: string
  priority: TestCasePriority
  type: TestCaseType
  tags: string[]
}

// 测试用例生成任务接口
export interface TestCaseTask {
  id: string
  name: string
  requirement_text_id: string
  prompt_template_id: string
  case_template_id?: string
  status: TaskStatus
  result?: TestCase[]
  error_message?: string
  created_at: string
  updated_at?: string
}

// 测试用例模板接口
export interface CaseTemplate {
  id: string
  name: string
  description?: string
  structure: Record<string, string>
  is_default: boolean
  created_at: string
}

// 创建测试用例任务请求
export interface CreateTestCaseTaskRequest {
  name: string
  requirement_text_id: string
  prompt_template_id: string
  case_template_id?: string
}

// 创建测试用例模板请求
export interface CreateCaseTemplateRequest {
  name: string
  description?: string
  structure: Record<string, string>
  is_default?: boolean
}

// 测试用例生成API
export const testCasesApi = {
  // === 测试用例任务管理 ===
  // 获取测试用例任务列表
  getTasks: (params?: { 
    page?: number
    limit?: number
    status?: TaskStatus
    requirement_text_id?: string
  }) => 
    api.get('/test-cases/tasks', { params }),

  // 创建测试用例生成任务
  createTask: (data: CreateTestCaseTaskRequest): Promise<TestCaseTask> => 
    api.post('/test-cases/tasks', data),

  // 获取测试用例任务详情
  getTask: (id: string): Promise<TestCaseTask> => 
    api.get(`/test-cases/tasks/${id}`),

  // 更新测试用例任务
  updateTask: (id: string, data: Partial<CreateTestCaseTaskRequest>) => 
    api.put(`/test-cases/tasks/${id}`, data),

  // 删除测试用例任务
  deleteTask: (id: string) => 
    api.delete(`/test-cases/tasks/${id}`),

  // 执行测试用例生成任务
  executeTask: (id: string) => 
    api.post(`/test-cases/tasks/${id}/execute`),

  // === 测试用例管理 ===
  // 获取测试用例列表
  getTestCases: (taskId: string) => 
    api.get(`/test-cases/tasks/${taskId}/cases`),

  // 更新测试用例
  updateTestCase: (taskId: string, caseId: string, data: Partial<TestCase>) => 
    api.put(`/test-cases/tasks/${taskId}/cases/${caseId}`, data),

  // 删除测试用例
  deleteTestCase: (taskId: string, caseId: string) => 
    api.delete(`/test-cases/tasks/${taskId}/cases/${caseId}`),

  // === 测试用例模板管理 ===
  // 获取测试用例模板列表
  getTemplates: () => 
    api.get('/test-cases/templates'),

  // 创建测试用例模板
  createTemplate: (data: CreateCaseTemplateRequest): Promise<CaseTemplate> => 
    api.post('/test-cases/templates', data),

  // 获取测试用例模板详情
  getTemplate: (id: string): Promise<CaseTemplate> => 
    api.get(`/test-cases/templates/${id}`),

  // 更新测试用例模板
  updateTemplate: (id: string, data: Partial<CreateCaseTemplateRequest>) => 
    api.put(`/test-cases/templates/${id}`, data),

  // 删除测试用例模板
  deleteTemplate: (id: string) => 
    api.delete(`/test-cases/templates/${id}`),

  // 设置默认模板
  setDefaultTemplate: (id: string) => 
    api.post(`/test-cases/templates/${id}/set-default`),

  // === 导出和批量操作 ===
  // 导出测试用例
  exportTestCases: (taskId: string, format: 'excel' | 'csv' | 'json' = 'excel') => 
    api.get(`/test-cases/tasks/${taskId}/export`, { 
      params: { format },
      responseType: 'blob'
    }),

  // 批量删除任务
  batchDeleteTasks: (ids: string[]) => 
    api.post('/test-cases/tasks/batch/delete', { ids }),

  // 批量执行任务
  batchExecuteTasks: (ids: string[]) => 
    api.post('/test-cases/tasks/batch/execute', { ids }),

  // === 统计 ===
  // 获取测试用例统计
  getStats: () => 
    api.get('/test-cases/stats')
}

// 测试用例工具函数
export const testCaseUtils = {
  // 格式化任务状态
  formatStatus: (status: TaskStatus): string => {
    const statusMap = {
      pending: '待执行',
      queued: '排队中',
      running: '执行中',
      completed: '已完成',
      failed: '失败'
    }
    return statusMap[status] || status
  },

  // 获取状态颜色
  getStatusColor: (status: TaskStatus): string => {
    const colorMap = {
      pending: '#909399',
      queued: '#409EFF',
      running: '#E6A23C',
      completed: '#67C23A',
      failed: '#F56C6C'
    }
    return colorMap[status] || '#909399'
  },

  // 格式化优先级
  formatPriority: (priority: TestCasePriority): string => {
    const priorityMap = {
      P0: '最高',
      P1: '高',
      P2: '中',
      P3: '低'
    }
    return priorityMap[priority] || priority
  },

  // 获取优先级颜色
  getPriorityColor: (priority: TestCasePriority): string => {
    const colorMap = {
      P0: '#F56C6C',
      P1: '#E6A23C',
      P2: '#409EFF',
      P3: '#909399'
    }
    return colorMap[priority] || '#909399'
  },

  // 格式化测试用例类型
  formatType: (type: TestCaseType): string => {
    const typeMap = {
      functional: '功能测试',
      performance: '性能测试',
      security: '安全测试',
      usability: '易用性测试',
      compatibility: '兼容性测试'
    }
    return typeMap[type] || type
  },

  // 验证测试用例任务数据
  validateTask: (data: CreateTestCaseTaskRequest): string[] => {
    const errors: string[] = []
    
    if (!data.name || data.name.trim().length === 0) {
      errors.push('任务名称不能为空')
    }
    
    if (data.name && data.name.length > 100) {
      errors.push('任务名称长度不能超过100个字符')
    }
    
    if (!data.requirement_text_id) {
      errors.push('请选择需求文档')
    }
    
    if (!data.prompt_template_id) {
      errors.push('请选择Prompt模板')
    }
    
    return errors
  },

  // 验证测试用例模板数据
  validateTemplate: (data: CreateCaseTemplateRequest): string[] => {
    const errors: string[] = []
    
    if (!data.name || data.name.trim().length === 0) {
      errors.push('模板名称不能为空')
    }
    
    if (data.name && data.name.length > 100) {
      errors.push('模板名称长度不能超过100个字符')
    }
    
    if (!data.structure || Object.keys(data.structure).length === 0) {
      errors.push('模板结构不能为空')
    }
    
    return errors
  },

  // 验证测试用例数据
  validateTestCase: (data: Partial<TestCase>): string[] => {
    const errors: string[] = []
    
    if (data.title && data.title.length > 200) {
      errors.push('用例标题长度不能超过200个字符')
    }
    
    if (data.description && data.description.length > 1000) {
      errors.push('用例描述长度不能超过1000个字符')
    }
    
    if (data.steps && data.steps.length > 2000) {
      errors.push('测试步骤长度不能超过2000个字符')
    }
    
    if (data.expected_result && data.expected_result.length > 1000) {
      errors.push('预期结果长度不能超过1000个字符')
    }
    
    return errors
  },

  // 计算测试覆盖率
  calculateCoverage: (testCases: TestCase[], requirements: string[]): number => {
    if (requirements.length === 0) return 0
    
    const coveredRequirements = new Set<string>()
    
    testCases.forEach(testCase => {
      requirements.forEach(req => {
        if (testCase.description.includes(req) || testCase.steps.includes(req)) {
          coveredRequirements.add(req)
        }
      })
    })
    
    return Math.round((coveredRequirements.size / requirements.length) * 100)
  },

  // 生成默认测试用例模板
  getDefaultTemplate: (): Record<string, string> => {
    return {
      title: '测试用例标题',
      description: '测试用例描述',
      preconditions: '前置条件',
      steps: '测试步骤',
      expected_result: '预期结果',
      priority: '优先级',
      type: '测试类型'
    }
  },

  // 解析测试步骤
  parseTestSteps: (steps: string): string[] => {
    return steps.split('\n')
      .map(step => step.trim())
      .filter(step => step.length > 0)
      .map((step, index) => `${index + 1}. ${step}`)
  },

  // 格式化测试用例为文本
  formatTestCaseText: (testCase: TestCase): string => {
    return `
标题: ${testCase.title}
描述: ${testCase.description}
优先级: ${testCaseUtils.formatPriority(testCase.priority)}
类型: ${testCaseUtils.formatType(testCase.type)}

前置条件:
${testCase.preconditions}

测试步骤:
${testCase.steps}

预期结果:
${testCase.expected_result}

标签: ${testCase.tags.join(', ')}
    `.trim()
  }
}

export default testCasesApi
