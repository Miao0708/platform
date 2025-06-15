import { api } from './index'

// AI 模型相关接口定义

// AI 模型信息
export interface AIModel {
  id: string
  name: string
  provider: string
  baseUrl: string
  model: string
  maxTokens: number
  temperature: number
  topP?: number
  frequencyPenalty?: number
  presencePenalty?: number
  isDefault: boolean
  isActive: boolean
  timeout: number
  usageCount: number
  totalTokensUsed: number
  lastUsedAt?: string
  extraConfig?: Record<string, any>

}

// 创建 AI 模型请求参数
export interface CreateAIModelRequest {
  name: string
  provider: string
  base_url: string  // 后端使用snake_case
  api_key?: string  // 后端使用snake_case
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
  model?: string
  api_key?: string
  base_url?: string
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

// 测试连接响应
export interface TestConnectionResponse {
  success: boolean
  message: string
  responseTime: number
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
  getAIModel: (id: string) =>
    api.get<AIModel>(`/ai/models/${id}`),

  // 创建 AI 模型配置
  createAIModel: (data: CreateAIModelRequest) =>
    api.post<AIModel>('/ai/models', data),

  // 更新 AI 模型配置
  updateAIModel: (id: string, data: UpdateAIModelRequest) =>
    api.put<AIModel>(`/ai/models/${id}`, data),

  // 删除 AI 模型配置
  deleteAIModel: (id: string) =>
    api.delete(`/ai/models/${id}`),

  // 测试 AI 模型连接
  testConnection: (id: string) =>
    api.post<TestConnectionResponse>(`/ai/models/${id}/test`),

  // 设置默认模型
  setDefaultModel: (id: string) =>
    api.post(`/ai/models/${id}/set-default`),

  // 拉取可用模型列表
  fetchAvailableModels: (config: { provider: string; baseUrl: string; apiKey: string }) =>
    api.post<{ value: string; label: string; description?: string }[]>('/ai/models/fetch', {
      provider: config.provider,
      base_url: config.baseUrl,
      api_key: config.apiKey
    })
}

export default aiModelsApi 