import { api } from './index'

// 需求状态类型
export type RequirementStatus = 'pending' | 'processing' | 'completed' | 'failed'

// 需求优先级类型
export type RequirementPriority = 'low' | 'medium' | 'high' | 'urgent'

// 需求分类类型
export type RequirementCategory = 'functional' | 'non_functional' | 'business' | 'technical' | 'security' | 'performance'

// 需求信息接口
export interface RequirementInfo {
  id: string
  name: string
  original_content: string
  optimized_content?: string
  parsed_content?: string
  structured_requirements?: Record<string, any>
  category?: RequirementCategory
  priority: RequirementPriority
  status: RequirementStatus
  input_type: 'file' | 'manual'
  file_name?: string
  file_size?: number
  complexity?: 'low' | 'medium' | 'high'
  estimated_hours?: number
  tags?: string[]

}

// 创建需求请求
export interface CreateRequirementRequest {
  name: string
  original_content: string
  category?: RequirementCategory
  priority?: RequirementPriority
  tags?: string[]
}

// 更新需求请求
export interface UpdateRequirementRequest {
  name?: string
  original_content?: string
  category?: RequirementCategory
  priority?: RequirementPriority
  tags?: string[]
}

// 需求列表查询参数
export interface RequirementListParams {
  page?: number
  limit?: number
  status?: RequirementStatus
  category?: RequirementCategory
  priority?: RequirementPriority
  search?: string
}

// 需求管理API
export const requirementsApi = {
  // 获取需求列表
  getRequirements: (params?: RequirementListParams) => 
    api.get('/requirements', { params }),

  // 创建需求（文本输入）
  createRequirement: (data: CreateRequirementRequest): Promise<RequirementInfo> => 
    api.post('/requirements', data),

  // 上传需求文件（标准化版本）
  uploadRequirement: (data: {
    file: File
    name: string
    category?: string
    priority?: 'low' | 'medium' | 'high' | 'urgent'
    taskMetadata?: Record<string, any>
  }) => {
    const formData = new FormData()
    formData.append('file', data.file)
    formData.append('name', data.name)
    
    if (data.category) {
      formData.append('category', data.category)
    }
    
    if (data.priority) {
      formData.append('priority', data.priority)
    }
    
    if (data.taskMetadata) {
      formData.append('task_metadata', JSON.stringify(data.taskMetadata))
    }
    
    return api.post('/requirements/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 简化的上传方法（向后兼容）
  uploadRequirementSimple: (file: File, name?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (name) {
      formData.append('name', name)
    }
    return api.post('/requirements/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取需求详情
  getRequirement: (id: string): Promise<RequirementInfo> => 
    api.get(`/requirements/${id}`),

  // 更新需求
  updateRequirement: (id: string, data: UpdateRequirementRequest): Promise<RequirementInfo> => 
    api.put(`/requirements/${id}`, data),

  // 删除需求
  deleteRequirement: (id: string) => 
    api.delete(`/requirements/${id}`),

  // 优化需求（AI处理）
  optimizeRequirement: (id: string, promptTemplateId?: string) => 
    api.post(`/requirements/${id}/optimize`, { 
      prompt_template_id: promptTemplateId 
    }),

  // 解析需求（AI处理）
  parseRequirement: (id: string, promptTemplateId?: string) => 
    api.post(`/requirements/${id}/parse`, { 
      prompt_template_id: promptTemplateId 
    }),

  // 获取需求解析状态
  getRequirementStatus: (id: string) => 
    api.get(`/requirements/${id}/status`),

  // 导出需求
  exportRequirement: (id: string, format: 'md' | 'pdf' | 'docx' = 'md') => 
    api.get(`/requirements/${id}/export`, { 
      params: { format },
      responseType: 'blob'
    }),

  // 批量操作
  batchDelete: (ids: string[]) => 
    api.post('/requirements/batch/delete', { ids }),

  batchUpdateStatus: (ids: string[], status: RequirementStatus) => 
    api.post('/requirements/batch/status', { ids, status }),

  // 获取需求统计
  getRequirementStats: () => 
    api.get('/requirements/stats')
}

// 需求工具函数
export const requirementUtils = {
  // 格式化需求状态
  formatStatus: (status: RequirementStatus): string => {
    const statusMap = {
      pending: '待处理',
      processing: '处理中',
      completed: '已完成',
      failed: '失败'
    }
    return statusMap[status] || status
  },

  // 格式化优先级
  formatPriority: (priority: RequirementPriority): string => {
    const priorityMap = {
      low: '低',
      medium: '中',
      high: '高',
      urgent: '紧急'
    }
    return priorityMap[priority] || priority
  },

  // 格式化分类
  formatCategory: (category?: RequirementCategory): string => {
    if (!category) return '未分类'
    const categoryMap = {
      functional: '功能需求',
      non_functional: '非功能需求',
      business: '业务需求',
      technical: '技术需求',
      security: '安全需求',
      performance: '性能需求'
    }
    return categoryMap[category] || category
  },

  // 获取状态颜色
  getStatusColor: (status: RequirementStatus): string => {
    const colorMap = {
      pending: '#909399',
      processing: '#409EFF',
      completed: '#67C23A',
      failed: '#F56C6C'
    }
    return colorMap[status] || '#909399'
  },

  // 获取优先级颜色
  getPriorityColor: (priority: RequirementPriority): string => {
    const colorMap = {
      low: '#909399',
      medium: '#E6A23C',
      high: '#F56C6C',
      urgent: '#F56C6C'
    }
    return colorMap[priority] || '#909399'
  },

  // 验证需求数据
  validateRequirement: (data: CreateRequirementRequest | UpdateRequirementRequest): string[] => {
    const errors: string[] = []
    
    if ('name' in data && data.name && data.name.length > 100) {
      errors.push('需求名称长度不能超过100个字符')
    }
    
    if ('original_content' in data && data.original_content && data.original_content.length > 10000) {
      errors.push('需求内容长度不能超过10000个字符')
    }
    
    return errors
  },

  // 计算需求复杂度
  calculateComplexity: (content: string): 'low' | 'medium' | 'high' => {
    const length = content.length
    const keywordCount = (content.match(/需求|功能|接口|数据库|性能|安全/g) || []).length
    
    if (length < 500 && keywordCount < 5) {
      return 'low'
    } else if (length < 2000 && keywordCount < 15) {
      return 'medium'
    } else {
      return 'high'
    }
  },

  // 估算开发时间（小时）
  estimateHours: (complexity: 'low' | 'medium' | 'high', priority: RequirementPriority): number => {
    const baseHours = {
      low: 8,
      medium: 24,
      high: 72
    }
    
    const priorityMultiplier = {
      low: 0.8,
      medium: 1.0,
      high: 1.2,
      urgent: 1.5
    }
    
    return Math.round(baseHours[complexity] * priorityMultiplier[priority])
  },

  // 格式化文件大小
  formatFileSize: (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
}

export default requirementsApi
