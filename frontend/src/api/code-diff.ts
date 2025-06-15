import { api } from './index'

// 代码差异相关接口定义

// 代码文件差异信息
export interface FileDiff {
  path: string
  change_type: 'added' | 'modified' | 'deleted' | 'renamed'
  additions: number
  deletions: number
  diff: string
}

// 差异汇总信息
export interface DiffSummary {
  total_files: number
  total_additions: number
  total_deletions: number
}

// 代码差异结果
export interface CodeDiffResult {
  files: FileDiff[]
  summary: DiffSummary
}

// 代码差异任务
export interface CodeDiffTask {
  id: number
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  repository_url: string
  source_branch: string
  target_branch: string
  file_patterns?: string[]
  exclude_patterns?: string[]
  result?: CodeDiffResult
  error_message?: string
  created_at: string
  completed_at?: string
}

// 创建代码差异任务请求参数
export interface CreateCodeDiffRequest {
  repository_url: string
  source_branch: string
  target_branch: string
  file_patterns?: string[]
  exclude_patterns?: string[]
}

// 代码差异 API
export const codeDiffApi = {
  // 创建代码差异任务
  createDiffTask: (data: CreateCodeDiffRequest) =>
    api.post<{ id: number; task_id: string; status: string; created_at: string }>('/tasks/code-diff', data),

  // 获取代码差异任务列表
  getDiffTasks: (params?: { skip?: number; limit?: number }) =>
    api.get<CodeDiffTask[]>('/tasks/code-diff'),

  // 获取单个代码差异任务
  getDiffTask: (diffId: number) =>
    api.get<CodeDiffTask>(`/tasks/code-diff/${diffId}`),

  // 删除代码差异任务
  deleteDiffTask: (diffId: number) =>
    api.delete(`/tasks/code-diff/${diffId}`),

  // 获取任务内容
  getDiffContent: (diffId: number) =>
    api.get(`/tasks/code-diff/${diffId}/content`)
}

export default codeDiffApi 