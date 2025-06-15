/**
 * 任务管理API - 支持三级分离架构
 */

import { api } from './index'
import type { AxiosRequestConfig } from 'axios'

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

// 任务列表响应
export interface TaskListResponse<T> {
  tasks: T[]
  total: number
  page: number
  limit: number
  pages: number
  hasNext: boolean
  hasPrev: boolean
}

// 任务选择器（用于关联任务）
export interface CodeDiffTaskSelector {
  id: number
  name: string
  status: TaskStatus
  createdAt: string
  description?: string
  repositoryName?: string
  sourceBranch: string
  targetBranch: string
  fileCount: number
}

export interface RequirementTaskSelector {
  id: number
  name: string
  status: TaskStatus
  createdAt: string
  description?: string
  category?: string
  priority: string
  complexity?: string
}

// 任务执行相关
export interface TaskExecution {
  id: string
  taskType: string
  taskId: number
  executionId: string
  status: TaskStatus
  startedAt?: string
  completedAt?: string
  stepsTotal: number
  stepsCompleted: number
  currentStep?: string
  result?: string
  errorMessage?: string
  logs?: string
}

export interface TaskExecutionResponse {
  executionId: string
  status: TaskStatus
  progress: {
    stepsTotal: number
    stepsCompleted: number
    currentStep?: string
  }
  result?: any
  error?: string
}

// 任务统计
export interface TaskStats {
  totalTasks: number
  pendingTasks: number
  runningTasks: number
  completedTasks: number
  failedTasks: number
  tasksByType: Record<string, number>
  resourceUsage: {
    totalTokensUsed: number
    averageProcessingTime: number
  }
}

// ===== 第一级：代码差异任务 API =====
export const codeDiffTaskApi = {
  // 获取代码差异任务列表
  getCodeDiffTasks: (params?: {
    page?: number
    limit?: number
    status?: string
    repositoryId?: number
  }) => api.get<TaskListResponse<CodeDiffTask>>('/tasks/code-diff', params ? { params } : undefined),
  
  // 创建代码差异任务
  createCodeDiffTask: (data: CreateCodeDiffTaskRequest) =>
    api.post<CodeDiffTask>('/tasks/code-diff', data),
  
  // 获取代码差异任务详情
  getCodeDiffTask: (id: string) =>
    api.get<CodeDiffTask>(`/tasks/code-diff/${id}`),
  
  // 更新代码差异任务
  updateCodeDiffTask: (id: string, data: Partial<CodeDiffTask>) =>
    api.put<CodeDiffTask>(`/tasks/code-diff/${id}`, data),
  
  // 删除代码差异任务
  deleteCodeDiffTask: (id: string) =>
    api.delete(`/tasks/code-diff/${id}`),
  
  // 重新生成代码差异
  regenerateCodeDiff: (id: string) =>
    api.post<CodeDiffTask>(`/tasks/code-diff/${id}/regenerate`),
  
  // 获取代码差异内容
  getCodeDiffContent: (id: string) =>
    api.get<{ content: string }>(`/tasks/code-diff/${id}/content`),
  
  // 获取可选择的代码差异任务（用于流水线）
  getCodeDiffSelectors: (params?: { status?: string }) =>
    api.get<CodeDiffTaskSelector[]>('/tasks/code-diff/selectors', { params }),
  
  // 上传代码差异文件
  uploadCodeDiffFile: (file: File, name: string, description?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    if (description) formData.append('description', description)
    
    return api.post<CodeDiffTask>('/tasks/code-diff/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// ===== 第二级：需求解析任务 API =====
export const requirementTaskApi = {
  // 获取需求解析任务列表
  getRequirementTasks: (params?: {
    page?: number
    limit?: number
    status?: string
    category?: string
    priority?: string
  }) => api.get<TaskListResponse<RequirementParseTask>>('/tasks/requirements', { params }),
  
  // 创建需求解析任务（文本）
  createRequirementTask: (data: CreateRequirementParseTaskRequest) =>
    api.post<RequirementParseTask>('/tasks/requirements', data),
  
  // 获取需求解析任务详情
  getRequirementTask: (id: string) =>
    api.get<RequirementParseTask>(`/tasks/requirements/${id}`),
  
  // 更新需求解析任务
  updateRequirementTask: (id: string, data: Partial<RequirementParseTask>) =>
    api.put<RequirementParseTask>(`/tasks/requirements/${id}`, data),
  
  // 删除需求解析任务
  deleteRequirementTask: (id: string) =>
    api.delete(`/tasks/requirements/${id}`),
  
  // 重新解析需求
  reparseRequirement: (id: string, config?: Record<string, any>) =>
    api.post<RequirementParseTask>(`/tasks/requirements/${id}/reparse`, { config }),
  
  // 获取可选择的需求任务（用于流水线）
  getRequirementSelectors: (params?: { 
    status?: string
    category?: string 
  }) => api.get<RequirementTaskSelector[]>('/tasks/requirements/selectors', { params }),
  
  // 上传需求文档
  uploadRequirementFile: (file: File, name: string, category?: string, priority?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)
    if (category) formData.append('category', category)
    if (priority) formData.append('priority', priority)
    
    return api.post<RequirementParseTask>('/tasks/requirements/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // 验证需求格式
  validateRequirement: (content: string) =>
    api.post<{
      isValid: boolean
      errors: string[]
      warnings: string[]
      suggestions: string[]
    }>('/tasks/requirements/validate', { content })
}

// ===== 第三级：流水线任务 API =====
export const pipelineTaskApi = {
  // 获取流水线任务列表
  getPipelineTasks: (params?: {
    page?: number
    limit?: number
    status?: string
    pipelineType?: string
  }) => api.get<TaskListResponse<PipelineTask>>('/tasks/pipelines', { params }),
  
  // 创建流水线任务
  createPipelineTask: (data: CreatePipelineTaskRequest) =>
    api.post<PipelineTask>('/tasks/pipelines', data),
  
  // 获取流水线任务详情
  getPipelineTask: (id: string) =>
    api.get<PipelineTask>(`/tasks/pipelines/${id}`),
  
  // 更新流水线任务
  updatePipelineTask: (id: string, data: Partial<PipelineTask>) =>
    api.put<PipelineTask>(`/tasks/pipelines/${id}`, data),
  
  // 删除流水线任务
  deletePipelineTask: (id: string) =>
    api.delete(`/tasks/pipelines/${id}`),
  
  // 启动流水线任务
  startPipelineTask: (id: string, config?: Record<string, any>) =>
    api.post<TaskExecutionResponse>(`/tasks/pipelines/${id}/start`, { config }),
  
  // 停止流水线任务
  stopPipelineTask: (id: string) =>
    api.post(`/tasks/pipelines/${id}/stop`),
  
  // 重新运行流水线任务
  rerunPipelineTask: (id: string, config?: Record<string, any>) =>
    api.post<TaskExecutionResponse>(`/tasks/pipelines/${id}/rerun`, { config }),
  
  // 获取流水线执行结果
  getPipelineResult: (id: string) =>
    api.get<{
      result?: string
      resultData?: Record<string, any>
      logs?: string
    }>(`/tasks/pipelines/${id}/result`),
  
  // 下载流水线结果
  downloadPipelineResult: (id: string, format: 'json' | 'pdf' | 'markdown' = 'json') =>
    api.get(`/tasks/pipelines/${id}/download`, {
      params: { format },
      responseType: 'blob'
    })
}

// ===== 任务执行跟踪 API =====
export const taskExecutionApi = {
  // 获取任务执行状态
  getExecutionStatus: (executionId: string) =>
    api.get<TaskExecution>(`/tasks/executions/${executionId}`),
  
  // 获取任务执行日志
  getExecutionLogs: (executionId: string) =>
    api.get<{ logs: string }>(`/tasks/executions/${executionId}/logs`),
  
  // 获取任务执行历史
  getExecutionHistory: (taskType: string, taskId: string) =>
    api.get<TaskExecution[]>(`/tasks/executions/history/${taskType}/${taskId}`),
  
  // 停止任务执行
  stopExecution: (executionId: string) =>
    api.post(`/tasks/executions/${executionId}/stop`)
}

// ===== 任务统计和批量操作 API =====
export const taskStatsApi = {
  // 获取任务统计
  getTaskStats: () =>
    api.get<TaskStats>('/tasks/stats'),
  
  // 获取任务状态分布
  getTaskStatusDistribution: (taskType?: string) =>
    api.get<Record<string, number>>('/tasks/stats/status-distribution', {
      params: { taskType }
    }),
  
  // 批量删除任务
  batchDeleteTasks: (taskType: string, ids: string[]) =>
    api.post('/tasks/batch/delete', { taskType, ids }),
  
  // 批量启动任务
  batchStartTasks: (taskType: string, ids: string[]) =>
    api.post('/tasks/batch/start', { taskType, ids }),
  
  // 批量停止任务
  batchStopTasks: (taskType: string, ids: string[]) =>
    api.post('/tasks/batch/stop', { taskType, ids }),
  
  // 清理已完成的任务
  cleanupCompletedTasks: (olderThanDays: number = 30) =>
    api.post('/tasks/cleanup', { olderThanDays })
}

// ===== WebSocket连接（实时状态更新） =====
export class TaskWebSocketClient {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  connect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    const wsUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'
    this.ws = new WebSocket(`${wsUrl}/ws/tasks`)

    this.ws.onopen = () => {
      console.log('Task WebSocket connected')
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('Task WebSocket error:', error)
      if (onError) onError(error)
    }

    this.ws.onclose = () => {
      console.log('Task WebSocket disconnected')
      this.reconnect(onMessage, onError)
    }
  }

  private reconnect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect(onMessage, onError)
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  subscribe(taskId: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'subscribe',
        taskId
      }))
    }
  }

  unsubscribe(taskId: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'unsubscribe',
        taskId
      }))
    }
  }
}

// 导出WebSocket客户端实例
export const taskWebSocket = new TaskWebSocketClient()

// ===== 任务工具函数 =====
export const taskUtils = {
  // 获取任务状态显示文本
  getStatusText: (status: string): string => {
    const statusMap: Record<string, string> = {
      pending: '等待中',
      queued: '队列中',
      running: '执行中',
      completed: '已完成',
      failed: '失败',
      cancelled: '已取消'
    }
    return statusMap[status] || status
  },

  // 获取任务状态类型（用于UI样式）
  getStatusType: (status: string): string => {
    const typeMap: Record<string, string> = {
      pending: 'info',
      queued: 'warning',
      running: 'primary',
      completed: 'success',
      failed: 'danger',
      cancelled: 'info'
    }
    return typeMap[status] || 'info'
  },

  // 格式化执行时间
  formatExecutionTime: (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds.toFixed(1)}秒`
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}分${remainingSeconds.toFixed(0)}秒`
    } else {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      return `${hours}小时${minutes}分钟`
    }
  },

  // 计算任务进度百分比
  calculateProgress: (stepsCompleted: number, stepsTotal: number): number => {
    if (stepsTotal === 0) return 0
    return Math.round((stepsCompleted / stepsTotal) * 100)
  },

  // 验证任务配置
  validateTaskConfig: (config: Record<string, any>): { isValid: boolean; errors: string[] } => {
    const errors: string[] = []

    if (config.temperature && (config.temperature < 0 || config.temperature > 2)) {
      errors.push('温度值必须在0-2之间')
    }

    if (config.maxTokens && config.maxTokens < 1) {
      errors.push('最大Token数必须大于0')
    }

    if (config.ragThreshold && (config.ragThreshold < 0 || config.ragThreshold > 1)) {
      errors.push('RAG阈值必须在0-1之间')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }
}

// 导出主要的API对象已在上面使用export关键字导出
