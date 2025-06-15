import { api } from './index'
import type { AIModelConfig, AIMessage, AIConversation, PromptTemplate } from '@/types'

// AI模型配置相关API
export const aiModelApi = {
  // 获取模型配置列表
  getModelConfigs: () => api.get<AIModelConfig[]>('/ai/models'),
  
  // 创建模型配置
  createModelConfig: (data: Omit<AIModelConfig, 'id'>) =>
    api.post<AIModelConfig>('/ai/models', data),
  
  // 更新模型配置
  updateModelConfig: (id: string, data: Partial<AIModelConfig>) =>
    api.put<AIModelConfig>(`/ai/models/${id}`, data),
  
  // 删除模型配置
  deleteModelConfig: (id: string) => api.delete(`/ai/models/${id}`),
  
  // 测试模型连接
  testModelConnection: (id: string) =>
    api.post<{ success: boolean; message: string }>(`/ai/models/${id}/test`),
  
  // 设置默认模型
  setDefaultModel: (id: string) => api.post(`/ai/models/${id}/set-default`)
}

// AI对话相关API
export const aiChatApi = {
  // 获取对话列表
  getConversations: () => api.get<AIConversation[]>('/ai/conversations'),
  
  // 创建新对话
  createConversation: (data: { title: string; modelConfigId: string }) =>
    api.post<AIConversation>('/ai/conversations', data),
  
  // 获取对话详情
  getConversation: (id: string) => api.get<AIConversation>(`/ai/conversations/${id}`),
  
  // 更新对话
  updateConversation: (id: string, data: Partial<AIConversation>) =>
    api.put<AIConversation>(`/ai/conversations/${id}`, data),
  
  // 删除对话
  deleteConversation: (id: string) => api.delete(`/ai/conversations/${id}`),
  
  // 发送消息
  sendMessage: (conversationId: string, data: {
    content: string
    modelConfigId: string
    promptTemplateId?: string
    context?: Record<string, any>
  }) => api.post<AIMessage>(`/ai/conversations/${conversationId}/messages`, data),
  
  // 流式发送消息（SSE）
  sendMessageStream: (conversationId: string, data: {
    content: string
    modelConfigId: string
    promptTemplateId?: string
    context?: Record<string, any>
  }) => {
    // 返回EventSource用于接收流式响应
    const url = `/api/ai/conversations/${conversationId}/messages/stream`
    const eventSource = new EventSource(url, {
      // 这里需要根据实际后端实现调整
    })
    return eventSource
  }
}

// Prompt模板相关API
export const promptApi = {
  // 获取Prompt模板列表
  getPromptTemplates: (params?: {
    category?: string
    tags?: string[]
    isPublic?: boolean
  }) => api.get<PromptTemplate[]>('/ai/prompts', { params }),
  
  // 创建Prompt模板
  createPromptTemplate: (data: Omit<PromptTemplate, 'id' | 'usageCount'>) =>
    api.post<PromptTemplate>('/ai/prompts', data),
  
  // 更新Prompt模板
  updatePromptTemplate: (id: string, data: Partial<PromptTemplate>) =>
    api.put<PromptTemplate>(`/ai/prompts/${id}`, data),
  
  // 删除Prompt模板
  deletePromptTemplate: (id: string) => api.delete(`/ai/prompts/${id}`),
  
  // 获取Prompt模板详情
  getPromptTemplate: (id: string) => api.get<PromptTemplate>(`/ai/prompts/${id}`),
  
  // 渲染Prompt模板（替换变量）
  renderPromptTemplate: (id: string, variables: Record<string, any>) =>
    api.post<{ content: string }>(`/ai/prompts/${id}/render`, { variables })
}

// AI任务相关API
export const aiTaskApi = {
  // 需求解析
  parseRequirement: (data: {
    content: string
    modelConfigId: string
    promptTemplateId?: string
  }) => api.post<{ optimizedContent: string; analysis: string }>('/ai/tasks/parse-requirement', data),
  
  // 代码评审
  reviewCode: (data: {
    codeDiff: string
    requirement?: string
    modelConfigId: string
    promptTemplateId?: string
    knowledgeBaseId?: string
  }) => api.post<{ review: string; issues: any[]; suggestions: string[] }>('/ai/tasks/review-code', data),
  
  // 生成测试用例
  generateTestCases: (data: {
    requirement: string
    modelConfigId: string
    promptTemplateId?: string
    caseTemplateId?: string
  }) => api.post<{ testCases: any[]; coverage: string }>('/ai/tasks/generate-test-cases', data),
  
  // 获取任务状态
  getTaskStatus: (taskId: string) => api.get<{
    status: 'pending' | 'running' | 'completed' | 'failed'
    progress: number
    result?: any
    error?: string
  }>(`/ai/tasks/${taskId}/status`)
}

// AI工具函数
export const aiUtils = {
  // 估算Token数量
  estimateTokens: (text: string): number => {
    // 简单的Token估算，实际应该使用更精确的方法
    return Math.ceil(text.length / 4)
  },
  
  // 格式化AI响应
  formatAIResponse: (response: string): string => {
    // 处理AI响应格式，如添加换行、处理特殊字符等
    return response
      .replace(/\n\n/g, '\n\n')
      .replace(/\*\*(.*?)\*\*/g, '**$1**')
      .trim()
  },
  
  // 验证模型配置
  validateModelConfig: (config: Partial<AIModelConfig>): string[] => {
    const errors: string[] = []
    
    if (!config.name) errors.push('配置名称不能为空')
    if (!config.provider) errors.push('服务商不能为空')
    if (!config.baseUrl) errors.push('API地址不能为空')
    if (!config.apiKey) errors.push('API密钥不能为空')
    if (!config.model) errors.push('模型名称不能为空')
    
    if (config.baseUrl && !isValidUrl(config.baseUrl)) {
      errors.push('API地址格式不正确')
    }
    
    if (config.maxTokens && (config.maxTokens < 1 || config.maxTokens > 32000)) {
      errors.push('最大Token数应在1-32000之间')
    }
    
    if (config.temperature && (config.temperature < 0 || config.temperature > 2)) {
      errors.push('温度参数应在0-2之间')
    }
    
    return errors
  },
  
  // 处理流式响应
  handleStreamResponse: (
    eventSource: EventSource,
    onMessage: (chunk: string) => void,
    onComplete: (fullResponse: string) => void,
    onError: (error: string) => void
  ) => {
    let fullResponse = ''
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.type === 'chunk') {
          fullResponse += data.content
          onMessage(data.content)
        } else if (data.type === 'done') {
          onComplete(fullResponse)
          eventSource.close()
        } else if (data.type === 'error') {
          onError(data.error)
          eventSource.close()
        }
      } catch (error) {
        onError('解析响应数据失败')
        eventSource.close()
      }
    }
    
    eventSource.onerror = () => {
      onError('连接中断')
      eventSource.close()
    }
    
    return () => eventSource.close()
  }
}

// 辅助函数
function isValidUrl(string: string): boolean {
  try {
    new URL(string)
    return true
  } catch {
    return false
  }
}

// 导出所有API
export default {
  model: aiModelApi,
  chat: aiChatApi,
  prompt: promptApi,
  task: aiTaskApi,
  utils: aiUtils
}
