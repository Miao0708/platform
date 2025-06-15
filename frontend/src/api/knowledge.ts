import { api } from './index'

// 知识库接口
export interface KnowledgeBase {
  id: string
  name: string
  description?: string
  document_count: number
  total_size: number
  is_active: boolean
  created_at: string
  updated_at?: string
}

// 知识库文档接口
export interface KnowledgeDocument {
  id: string
  knowledge_base_id: string
  filename: string
  file_size: number
  file_type: string
  content?: string
  vector_count: number
  status: 'processing' | 'completed' | 'failed'
  error_message?: string
  created_at: string
}

// 创建知识库请求
export interface CreateKnowledgeBaseRequest {
  name: string
  description?: string
}

// 更新知识库请求
export interface UpdateKnowledgeBaseRequest {
  name?: string
  description?: string
}

// 知识检索请求
export interface SearchKnowledgeRequest {
  query: string
  knowledge_base_id: string
  top_k?: number
  score_threshold?: number
}

// 知识检索结果
export interface SearchKnowledgeResult {
  document_id: string
  filename: string
  content: string
  score: number
  metadata?: Record<string, any>
}

// 知识库列表查询参数
export interface KnowledgeListParams {
  page?: number
  limit?: number
  search?: string
  is_active?: boolean
}

// 知识库API
export const knowledgeApi = {
  // === 知识库管理 ===
  // 获取知识库列表
  getKnowledgeBases: (params?: KnowledgeListParams) => 
    api.get('/knowledge-bases', { params }),

  // 创建知识库
  createKnowledgeBase: (data: CreateKnowledgeBaseRequest): Promise<KnowledgeBase> => 
    api.post('/knowledge-bases', data),

  // 获取知识库详情
  getKnowledgeBase: (id: string): Promise<KnowledgeBase> => 
    api.get(`/knowledge-bases/${id}`),

  // 更新知识库
  updateKnowledgeBase: (id: string, data: UpdateKnowledgeBaseRequest): Promise<KnowledgeBase> => 
    api.put(`/knowledge-bases/${id}`, data),

  // 删除知识库
  deleteKnowledgeBase: (id: string) => 
    api.delete(`/knowledge-bases/${id}`),

  // 激活/停用知识库
  toggleKnowledgeBase: (id: string, is_active: boolean) => 
    api.post(`/knowledge-bases/${id}/toggle`, { is_active }),

  // === 文档管理 ===
  // 获取知识库文档列表
  getDocuments: (knowledgeBaseId: string, params?: { 
    page?: number
    limit?: number
    status?: 'processing' | 'completed' | 'failed'
  }) => 
    api.get(`/knowledge-bases/${knowledgeBaseId}/documents`, { params }),

  // 上传文档到知识库
  uploadDocument: (knowledgeBaseId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/knowledge-bases/${knowledgeBaseId}/documents/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 批量上传文档
  uploadDocuments: (knowledgeBaseId: string, files: File[]) => {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })
    return api.post(`/knowledge-bases/${knowledgeBaseId}/documents/batch-upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取文档详情
  getDocument: (knowledgeBaseId: string, documentId: string): Promise<KnowledgeDocument> => 
    api.get(`/knowledge-bases/${knowledgeBaseId}/documents/${documentId}`),

  // 删除文档
  deleteDocument: (knowledgeBaseId: string, documentId: string) => 
    api.delete(`/knowledge-bases/${knowledgeBaseId}/documents/${documentId}`),

  // 重新处理文档
  reprocessDocument: (knowledgeBaseId: string, documentId: string) => 
    api.post(`/knowledge-bases/${knowledgeBaseId}/documents/${documentId}/reprocess`),

  // === 知识检索 ===
  // 搜索知识库
  searchKnowledge: (data: SearchKnowledgeRequest): Promise<SearchKnowledgeResult[]> => 
    api.post(`/knowledge-bases/${data.knowledge_base_id}/search`, {
      query: data.query,
      top_k: data.top_k || 5,
      score_threshold: data.score_threshold || 0.7
    }),

  // === 批量操作 ===
  // 批量删除知识库
  batchDeleteKnowledgeBases: (ids: string[]) => 
    api.post('/knowledge-bases/batch/delete', { ids }),

  // 批量删除文档
  batchDeleteDocuments: (knowledgeBaseId: string, documentIds: string[]) => 
    api.post(`/knowledge-bases/${knowledgeBaseId}/documents/batch/delete`, { 
      document_ids: documentIds 
    }),

  // === 统计 ===
  // 获取知识库统计
  getKnowledgeStats: () => 
    api.get('/knowledge-bases/stats'),

  // 获取知识库详细统计
  getKnowledgeBaseStats: (id: string) => 
    api.get(`/knowledge-bases/${id}/stats`)
}

// 知识库工具函数
export const knowledgeUtils = {
  // 格式化文件大小
  formatFileSize: (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  },

  // 获取文件类型图标
  getFileTypeIcon: (fileType: string): string => {
    const iconMap: Record<string, string> = {
      'pdf': 'document-pdf',
      'doc': 'document-word',
      'docx': 'document-word',
      'txt': 'document-text',
      'md': 'document-markdown',
      'html': 'document-html',
      'json': 'document-json'
    }
    return iconMap[fileType.toLowerCase()] || 'document'
  },

  // 获取文件类型颜色
  getFileTypeColor: (fileType: string): string => {
    const colorMap: Record<string, string> = {
      'pdf': '#F56C6C',
      'doc': '#409EFF',
      'docx': '#409EFF',
      'txt': '#909399',
      'md': '#67C23A',
      'html': '#E6A23C',
      'json': '#909399'
    }
    return colorMap[fileType.toLowerCase()] || '#909399'
  },

  // 验证知识库数据
  validateKnowledgeBase: (data: CreateKnowledgeBaseRequest | UpdateKnowledgeBaseRequest): string[] => {
    const errors: string[] = []
    
    if ('name' in data && data.name) {
      if (data.name.length > 100) {
        errors.push('知识库名称长度不能超过100个字符')
      }
    }
    
    if ('description' in data && data.description && data.description.length > 500) {
      errors.push('知识库描述长度不能超过500个字符')
    }
    
    return errors
  },

  // 检查文件类型是否支持
  isSupportedFileType: (fileType: string): boolean => {
    const supportedTypes = ['pdf', 'doc', 'docx', 'txt', 'md', 'html', 'json']
    return supportedTypes.includes(fileType.toLowerCase())
  },

  // 检查文件大小是否合法
  isValidFileSize: (fileSize: number, maxSize: number = 10 * 1024 * 1024): boolean => {
    return fileSize <= maxSize
  },

  // 格式化处理状态
  formatStatus: (status: 'processing' | 'completed' | 'failed'): string => {
    const statusMap = {
      processing: '处理中',
      completed: '已完成',
      failed: '失败'
    }
    return statusMap[status] || status
  },

  // 获取状态颜色
  getStatusColor: (status: 'processing' | 'completed' | 'failed'): string => {
    const colorMap = {
      processing: '#E6A23C',
      completed: '#67C23A',
      failed: '#F56C6C'
    }
    return colorMap[status] || '#909399'
  },

  // 计算向量化进度
  calculateVectorProgress: (vectorCount: number, estimatedTotal: number): number => {
    if (estimatedTotal === 0) return 0
    return Math.min(Math.round((vectorCount / estimatedTotal) * 100), 100)
  },

  // 格式化搜索分数
  formatSearchScore: (score: number): string => {
    return (score * 100).toFixed(1) + '%'
  },

  // 高亮搜索关键词
  highlightSearchKeywords: (text: string, keywords: string[]): string => {
    let highlightedText = text
    keywords.forEach(keyword => {
      const regex = new RegExp(`(${keyword})`, 'gi')
      highlightedText = highlightedText.replace(regex, '<mark>$1</mark>')
    })
    return highlightedText
  },

  // 截取搜索结果摘要
  truncateSearchResult: (content: string, maxLength: number = 200): string => {
    if (content.length <= maxLength) return content
    return content.substring(0, maxLength) + '...'
  }
}

export default knowledgeApi
