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
  createdAt: string
  updatedAt?: string
}

// 创建 AI 模型请求参数
export interface CreateAIModelRequest {
  name: string
  provider: string
  baseUrl: string
  apiKey?: string
  model: string
  maxTokens?: number
  temperature?: number
  topP?: number
  frequencyPenalty?: number
  presencePenalty?: number
  isDefault?: boolean
  isActive?: boolean
  timeout?: number
  extraConfig?: Record<string, any>
}

// 更新 AI 模型请求参数
export interface UpdateAIModelRequest {
  name?: string
  provider?: string
  modelName?: string
  apiKey?: string
  baseUrl?: string
  parameters?: {
    temperature?: number
    maxTokens?: number
    [key: string]: any
  }
  isActive?: boolean
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
    api.post(`/ai/models/${id}/set-default`)
}

export default aiModelsApi 