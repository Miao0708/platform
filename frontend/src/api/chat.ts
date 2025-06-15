import { api } from './index'

// AI对话相关接口定义

// 对话会话
export interface ChatSession {
  id: number
  title: string
  ai_model_id: number
  created_at: string
  updated_at?: string
}

// 对话消息
export interface ChatMessage {
  id: number
  session_id: number
  role: 'user' | 'assistant'
  content: string
  context?: Record<string, any>
  created_at: string
}

// 创建会话请求参数
export interface CreateSessionRequest {
  title: string
  ai_model_id: number
}

// 发送消息请求参数
export interface SendMessageRequest {
  content: string
  context?: {
    code_diff_id?: number
    requirement_id?: number
    [key: string]: any
  }
}

// 流式消息响应格式
export interface StreamMessageChunk {
  type: 'message' | 'error' | 'done'
  content?: string
  timestamp: string
}

// AI对话 API
export const chatApi = {
  // 获取对话列表
  getConversations: () =>
    api.get<ChatSession[]>('/ai/conversations'),

  // 获取单个对话详情
  getConversation: (conversationId: number) =>
    api.get<ChatSession>(`/ai/conversations/${conversationId}`),

  // 创建对话
  createConversation: (data: CreateSessionRequest) =>
    api.post<ChatSession>('/ai/conversations', data),

  // 更新对话标题
  updateConversation: (conversationId: number, data: { title: string }) =>
    api.put<ChatSession>(`/ai/conversations/${conversationId}`, data),

  // 删除对话
  deleteConversation: (conversationId: number) =>
    api.delete(`/ai/conversations/${conversationId}`),

  // 发送消息
  sendMessage: (conversationId: number, data: SendMessageRequest) =>
    api.post<ChatMessage>(`/ai/conversations/${conversationId}/messages`, data),

  // 发送流式消息
  sendMessageStream: (conversationId: number, data: SendMessageRequest) =>
    api.post(`/ai/conversations/${conversationId}/messages/stream`, data)
}

// 流式对话工具函数
export const chatUtils = {
  // 处理WebSocket消息
  handleWebSocketMessage: (
    event: MessageEvent,
    onMessage: (chunk: string) => void,
    onComplete: (fullMessage: string) => void,
    onError: (error: string) => void
  ) => {
    try {
      const data: StreamMessageChunk = JSON.parse(event.data)
      
      switch (data.type) {
        case 'message':
          if (data.content) {
            onMessage(data.content)
          }
          break
        case 'done':
          onComplete('')
          break
        case 'error':
          onError(data.content || '未知错误')
          break
      }
    } catch (error) {
      onError('解析消息失败')
    }
  },

  // 格式化Markdown内容
  formatMarkdown: (content: string): string => {
    // 基础Markdown格式化
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br/>')
  },

  // 估算消息token数量
  estimateTokens: (content: string): number => {
    // 简单估算：中文按字符数，英文按单词数
    const chineseChars = (content.match(/[\u4e00-\u9fa5]/g) || []).length
    const englishWords = content.replace(/[\u4e00-\u9fa5]/g, '').split(/\s+/).filter(w => w.length > 0).length
    
    return chineseChars + Math.ceil(englishWords * 1.3)
  },

  // 生成会话标题
  generateSessionTitle: (firstMessage: string): string => {
    // 取前20个字符作为标题
    const title = firstMessage.substring(0, 20)
    return title.length < firstMessage.length ? `${title}...` : title
  }
}

export default chatApi 