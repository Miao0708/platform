import { api } from './index'

// 流水线相关接口定义

// 流水线配置
export interface PipelineConfig {
  code_diff_id?: number
  requirement_id?: number
  ai_model_id: number
  prompt_template_id?: number
  knowledge_base_ids?: number[]
  [key: string]: any
}

// 流水线任务
export interface Pipeline {
  id: number
  name: string
  type: 'code_review' | 'test_case_generation' | 'requirement_analysis' | 'custom'
  config: PipelineConfig
  status: 'draft' | 'active' | 'inactive'
  created_at: string
  updated_at?: string
}

// 流水线执行任务
export interface PipelineExecution {
  id: number
  pipeline_id: number
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  result?: any
  error_message?: string
  started_at: string
  completed_at?: string
}

// 创建流水线请求参数
export interface CreatePipelineRequest {
  name: string
  type: 'code_review' | 'test_case_generation' | 'requirement_analysis' | 'custom'
  config: PipelineConfig
}

// 更新流水线请求参数
export interface UpdatePipelineRequest {
  name?: string
  config?: PipelineConfig
  status?: 'draft' | 'active' | 'inactive'
}

// 执行流水线请求参数
export interface ExecutePipelineRequest {
  input_data?: any
  override_config?: Partial<PipelineConfig>
}

// 流水线 API
export const pipelinesApi = {
  // 获取流水线任务列表
  getPipelines: () =>
    api.get<Pipeline[]>('/tasks/pipelines'),

  // 获取单个流水线任务
  getPipeline: (id: number) =>
    api.get<Pipeline>(`/tasks/pipelines/${id}`),

  // 创建流水线任务
  createPipeline: (data: CreatePipelineRequest) =>
    api.post<Pipeline>('/tasks/pipelines', data),

  // 更新流水线任务
  updatePipeline: (id: number, data: UpdatePipelineRequest) =>
    api.put<Pipeline>(`/tasks/pipelines/${id}`, data),

  // 执行流水线任务
  executePipeline: (id: number, data?: ExecutePipelineRequest) =>
    api.post<{ task_id: string; status: string; started_at: string }>(`/tasks/pipelines/${id}/execute`, data)
}

export default pipelinesApi 