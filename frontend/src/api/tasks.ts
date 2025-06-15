import { api } from './index'

// 任务状态类型
export type TaskStatus = 'pending' | 'queued' | 'running' | 'completed' | 'failed'

// 任务类型
export type TaskType = 'code_diff' | 'requirement_parse' | 'pipeline'

// 流水线任务类型
export type PipelineType = 'code_review' | 'test_generation' | 'custom'

// 基础任务接口
export interface BaseTask {
  id: string
  name: string
  type: TaskType
  status: TaskStatus
  error_message?: string
  created_at: string
  updated_at?: string
}

// 代码差异任务
export interface CodeDiffTask extends BaseTask {
  type: 'code_diff'
  repository_id: string
  source_ref: string
  target_ref: string
  compare_type: 'branch' | 'commit'
  diff_content?: string
}

// 需求解析任务
export interface RequirementParseTask extends BaseTask {
  type: 'requirement_parse'
  requirement_text_id: string
  prompt_template_id: string
  result?: string
}

// 流水线任务
export interface PipelineTask extends BaseTask {
  type: 'pipeline'
  pipeline_type: PipelineType
  config: Record<string, any>
  steps: PipelineStep[]
  current_step?: number
}

// 流水线步骤
export interface PipelineStep {
  id: string
  name: string
  type: string
  config: Record<string, any>
  status: TaskStatus
  result?: any
  error_message?: string
}

// 创建代码差异任务请求
export interface CreateCodeDiffTaskRequest {
  name: string
  repository_id: string
  source_ref: string
  target_ref: string
  compare_type: 'branch' | 'commit'
}

// 创建需求解析任务请求
export interface CreateRequirementParseTaskRequest {
  name: string
  requirement_text_id: string
  prompt_template_id: string
}

// 创建流水线任务请求
export interface CreatePipelineTaskRequest {
  name: string
  pipeline_type: PipelineType
  config: Record<string, any>
  steps: Omit<PipelineStep, 'id' | 'status' | 'result' | 'error_message'>[]
}

// 任务列表查询参数
export interface TaskListParams {
  page?: number
  limit?: number
  type?: TaskType
  status?: TaskStatus
  search?: string
}

// 任务管理API
export const tasksApi = {
  // === 通用任务管理 ===
  // 获取任务列表
  getTasks: (params?: TaskListParams) => 
    api.get('/tasks', { params }),

  // 获取任务详情
  getTask: (id: string): Promise<BaseTask> => 
    api.get(`/tasks/${id}`),

  // 删除任务
  deleteTask: (id: string) => 
    api.delete(`/tasks/${id}`),

  // 取消任务
  cancelTask: (id: string) => 
    api.post(`/tasks/${id}/cancel`),

  // 重试任务
  retryTask: (id: string) => 
    api.post(`/tasks/${id}/retry`),

  // === 代码差异任务 ===
  // 获取代码差异任务列表
  getCodeDiffTasks: (params?: Omit<TaskListParams, 'type'>) => 
    api.get('/tasks/code-diff', { params }),

  // 创建代码差异任务
  createCodeDiffTask: (data: CreateCodeDiffTaskRequest): Promise<CodeDiffTask> => 
    api.post('/tasks/code-diff', data),

  // 获取代码差异任务详情
  getCodeDiffTask: (id: string): Promise<CodeDiffTask> => 
    api.get(`/tasks/code-diff/${id}`),

  // 执行代码差异任务
  executeCodeDiffTask: (id: string) => 
    api.post(`/tasks/code-diff/${id}/execute`),

  // === 需求解析任务 ===
  // 获取需求解析任务列表
  getRequirementTasks: (params?: Omit<TaskListParams, 'type'>) => 
    api.get('/tasks/requirements', { params }),

  // 创建需求解析任务
  createRequirementTask: (data: CreateRequirementParseTaskRequest): Promise<RequirementParseTask> => 
    api.post('/tasks/requirements', data),

  // 获取需求解析任务详情
  getRequirementTask: (id: string): Promise<RequirementParseTask> => 
    api.get(`/tasks/requirements/${id}`),

  // 执行需求解析任务
  executeRequirementTask: (id: string) => 
    api.post(`/tasks/requirements/${id}/execute`),

  // === 流水线任务 ===
  // 获取流水线任务列表
  getPipelineTasks: (params?: Omit<TaskListParams, 'type'>) => 
    api.get('/tasks/pipeline', { params }),

  // 创建流水线任务
  createPipelineTask: (data: CreatePipelineTaskRequest): Promise<PipelineTask> => 
    api.post('/tasks/pipeline', data),

  // 获取流水线任务详情
  getPipelineTask: (id: string): Promise<PipelineTask> => 
    api.get(`/tasks/pipeline/${id}`),

  // 执行流水线任务
  executePipelineTask: (id: string) => 
    api.post(`/tasks/pipeline/${id}/execute`),

  // 暂停流水线任务
  pausePipelineTask: (id: string) => 
    api.post(`/tasks/pipeline/${id}/pause`),

  // 恢复流水线任务
  resumePipelineTask: (id: string) => 
    api.post(`/tasks/pipeline/${id}/resume`),

  // === 批量操作 ===
  // 批量删除任务
  batchDeleteTasks: (ids: string[]) => 
    api.post('/tasks/batch/delete', { ids }),

  // 批量取消任务
  batchCancelTasks: (ids: string[]) => 
    api.post('/tasks/batch/cancel', { ids }),

  // 批量重试任务
  batchRetryTasks: (ids: string[]) => 
    api.post('/tasks/batch/retry', { ids }),

  // === 统计 ===
  // 获取任务统计
  getTaskStats: () => 
    api.get('/tasks/stats'),

  // 获取任务执行历史
  getTaskHistory: (params?: { 
    start_date?: string
    end_date?: string
    type?: TaskType
  }) => 
    api.get('/tasks/history', { params })
}

// 任务工具函数
export const taskUtils = {
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

  // 格式化任务类型
  formatType: (type: TaskType): string => {
    const typeMap = {
      code_diff: '代码差异',
      requirement_parse: '需求解析',
      pipeline: '流水线'
    }
    return typeMap[type] || type
  },

  // 格式化流水线类型
  formatPipelineType: (type: PipelineType): string => {
    const typeMap = {
      code_review: '代码评审',
      test_generation: '测试生成',
      custom: '自定义'
    }
    return typeMap[type] || type
  },

  // 计算任务执行时间
  calculateExecutionTime: (createdAt: string, updatedAt?: string): string => {
    if (!updatedAt) return '-'
    
    const start = new Date(createdAt)
    const end = new Date(updatedAt)
    const diffMs = end.getTime() - start.getTime()
    
    if (diffMs < 1000) {
      return '< 1秒'
    } else if (diffMs < 60000) {
      return `${Math.round(diffMs / 1000)}秒`
    } else if (diffMs < 3600000) {
      return `${Math.round(diffMs / 60000)}分钟`
    } else {
      return `${Math.round(diffMs / 3600000)}小时`
    }
  },

  // 计算流水线进度
  calculatePipelineProgress: (steps: PipelineStep[]): number => {
    if (steps.length === 0) return 0
    
    const completedSteps = steps.filter(step => step.status === 'completed').length
    return Math.round((completedSteps / steps.length) * 100)
  },

  // 获取流水线当前步骤
  getCurrentPipelineStep: (task: PipelineTask): PipelineStep | null => {
    if (task.current_step === undefined || task.current_step >= task.steps.length) {
      return null
    }
    return task.steps[task.current_step]
  },

  // 验证代码差异任务数据
  validateCodeDiffTask: (data: CreateCodeDiffTaskRequest): string[] => {
    const errors: string[] = []
    
    if (!data.name || data.name.trim().length === 0) {
      errors.push('任务名称不能为空')
    }
    
    if (data.name && data.name.length > 100) {
      errors.push('任务名称长度不能超过100个字符')
    }
    
    if (!data.repository_id) {
      errors.push('请选择代码仓库')
    }
    
    if (!data.source_ref || data.source_ref.trim().length === 0) {
      errors.push('源分支/提交不能为空')
    }
    
    if (!data.target_ref || data.target_ref.trim().length === 0) {
      errors.push('目标分支/提交不能为空')
    }
    
    if (data.source_ref === data.target_ref) {
      errors.push('源分支/提交不能与目标分支/提交相同')
    }
    
    return errors
  },

  // 验证需求解析任务数据
  validateRequirementTask: (data: CreateRequirementParseTaskRequest): string[] => {
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

  // 验证流水线任务数据
  validatePipelineTask: (data: CreatePipelineTaskRequest): string[] => {
    const errors: string[] = []
    
    if (!data.name || data.name.trim().length === 0) {
      errors.push('任务名称不能为空')
    }
    
    if (data.name && data.name.length > 100) {
      errors.push('任务名称长度不能超过100个字符')
    }
    
    if (!data.steps || data.steps.length === 0) {
      errors.push('流水线步骤不能为空')
    }
    
    return errors
  }
}

export default tasksApi
