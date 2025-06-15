import { api } from './index'

// AI 模型相关接口定义

// AI 模型信息
export interface AIModel {
  id: number
  name: string
  provider: string
  base_url: string
  model: string
  max_tokens: number
  temperature: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
  is_default: boolean
  is_active: boolean
  timeout: number
  usage_count: number
  total_tokens_used: number
  last_used_at?: string
  extra_config?: Record<string, any>
  created_at: string
  updated_at?: string
}

// 创建 AI 模型请求参数
export interface CreateAIModelRequest {
  name: string
  provider: string
  base_url: string
  api_key?: string
  model: string
  max_tokens?: number
  temperature?: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
  is_default?: boolean
  is_active?: boolean
  timeout?: number
  extra_config?: Record<string, any>
}

// 更新 AI 模型请求参数
export interface UpdateAIModelRequest {
  name?: string
  provider?: string
  model_name?: string
  api_key?: string
  base_url?: string
  parameters?: {
    temperature?: number
    max_tokens?: number
    [key: string]: any
  }
  is_active?: boolean
}

// 测试连接响应
export interface TestConnectionResponse {
  success: boolean
  message: string
  response_time: number
}

// 获取 AI 模型列表查询参数
export interface GetAIModelsParams {
  skip?: number
  limit?: number
  provider?: string
}

// AI 模型 API
export const aiModelsApi = {
  // 获取 AI 模型列表
  getAIModels: (params?: GetAIModelsParams) =>
    api.get<AIModel[]>('/ai/models', params ? { params } : {}),

  // 获取单个 AI 模型
  getAIModel: (id: number) =>
    api.get<AIModel>(`/ai/models/${id}`),

  // 创建 AI 模型配置
  createAIModel: (data: CreateAIModelRequest) =>
    api.post<AIModel>('/ai/models', data),

  // 更新 AI 模型配置
  updateAIModel: (id: number, data: UpdateAIModelRequest) =>
    api.put<AIModel>(`/ai/models/${id}`, data),

  // 删除 AI 模型配置
  deleteAIModel: (id: number) =>
    api.delete(`/ai/models/${id}`),

  // 测试 AI 模型连接
  testConnection: (id: number) =>
    api.post<TestConnectionResponse>(`/ai/models/${id}/test`),

  // 设置默认模型
  setDefaultModel: (id: number) =>
    api.post(`/ai/models/${id}/set-default`)
}

export default aiModelsApi 