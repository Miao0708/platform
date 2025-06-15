import { api } from './index'

// Prompt模板分类
export type PromptCategory = 'requirement' | 'code_review' | 'test_case' | 'general'

// Prompt模板接口
export interface PromptTemplate {
  id: string
  name: string
  identifier: string
  content: string
  description?: string
  category: PromptCategory
  tags: string[]
  variables: string[]
  is_public: boolean
  usage_count: number
  created_at: string
  updated_at: string
}

// 创建Prompt模板请求
export interface CreatePromptRequest {
  name: string
  identifier: string
  content: string
  description?: string
  category: PromptCategory
  tags?: string[]
  is_public?: boolean
}

// 更新Prompt模板请求
export interface UpdatePromptRequest {
  name?: string
  content?: string
  description?: string
  category?: PromptCategory
  tags?: string[]
  is_public?: boolean
}

// Prompt模板列表查询参数
export interface PromptListParams {
  page?: number
  limit?: number
  category?: PromptCategory
  tags?: string[]
  is_public?: boolean
  search?: string
}

// 渲染Prompt请求
export interface RenderPromptRequest {
  variables: Record<string, any>
}

// Prompt模板API
export const promptsApi = {
  // 获取Prompt模板列表
  getPrompts: (params?: PromptListParams) => 
    api.get('/ai/prompts', { params }),

  // 创建Prompt模板
  createPrompt: (data: CreatePromptRequest): Promise<PromptTemplate> => 
    api.post('/ai/prompts', data),

  // 获取Prompt模板详情
  getPrompt: (id: string): Promise<PromptTemplate> => 
    api.get(`/ai/prompts/${id}`),

  // 更新Prompt模板
  updatePrompt: (id: string, data: UpdatePromptRequest): Promise<PromptTemplate> => 
    api.put(`/ai/prompts/${id}`, data),

  // 删除Prompt模板
  deletePrompt: (id: string) => 
    api.delete(`/ai/prompts/${id}`),

  // 渲染Prompt模板（替换变量）
  renderPrompt: (id: string, data: RenderPromptRequest) => 
    api.post(`/ai/prompts/${id}/render`, data),

  // 复制Prompt模板
  copyPrompt: (id: string, name?: string) => 
    api.post(`/ai/prompts/${id}/copy`, { name }),

  // 获取Prompt模板使用统计
  getPromptStats: (id: string) => 
    api.get(`/ai/prompts/${id}/stats`),

  // 批量操作
  batchDelete: (ids: string[]) => 
    api.post('/ai/prompts/batch/delete', { ids }),

  batchUpdateCategory: (ids: string[], category: PromptCategory) => 
    api.post('/ai/prompts/batch/category', { ids, category }),

  // 导出Prompt模板
  exportPrompt: (id: string, format: 'json' | 'md' = 'json') => 
    api.get(`/ai/prompts/${id}/export`, { 
      params: { format },
      responseType: 'blob'
    }),

  // 导入Prompt模板
  importPrompt: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/ai/prompts/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

// Prompt工具函数
export const promptUtils = {
  // 格式化分类显示
  formatCategory: (category: PromptCategory): string => {
    const categoryMap = {
      requirement: '需求分析',
      code_review: '代码评审',
      test_case: '测试用例',
      general: '通用对话'
    }
    return categoryMap[category] || category
  },

  // 获取分类颜色
  getCategoryColor: (category: PromptCategory): string => {
    const colorMap = {
      requirement: '#409EFF',
      code_review: '#67C23A',
      test_case: '#E6A23C',
      general: '#909399'
    }
    return colorMap[category] || '#909399'
  },

  // 提取Prompt中的变量
  extractVariables: (content: string): string[] => {
    const variableRegex = /\{\{([^}]+)\}\}/g
    const variables: string[] = []
    let match

    while ((match = variableRegex.exec(content)) !== null) {
      const variable = match[1].trim()
      if (!variables.includes(variable) && !variable.startsWith('GENERATE_FROM:')) {
        variables.push(variable)
      }
    }

    return variables
  },

  // 验证Prompt标识符
  isValidIdentifier: (identifier: string): boolean => {
    // 标识符只能包含字母、数字、下划线和连字符
    const identifierRegex = /^[a-zA-Z][a-zA-Z0-9_-]*$/
    return identifierRegex.test(identifier)
  },

  // 验证Prompt数据
  validatePrompt: (data: CreatePromptRequest | UpdatePromptRequest): string[] => {
    const errors: string[] = []
    
    if ('name' in data && data.name) {
      if (data.name.length > 100) {
        errors.push('模板名称长度不能超过100个字符')
      }
    }
    
    if ('identifier' in data && data.identifier) {
      if (!promptUtils.isValidIdentifier(data.identifier)) {
        errors.push('标识符只能包含字母、数字、下划线和连字符，且必须以字母开头')
      }
    }
    
    if ('content' in data && data.content) {
      if (data.content.length > 10000) {
        errors.push('模板内容长度不能超过10000个字符')
      }
    }
    
    return errors
  },

  // 渲染Prompt预览
  renderPreview: (content: string, variables: Record<string, any>): string => {
    let rendered = content
    
    // 替换变量
    Object.entries(variables).forEach(([key, value]) => {
      const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g')
      rendered = rendered.replace(regex, String(value))
    })
    
    return rendered
  },

  // 生成示例变量
  generateExampleVariables: (variables: string[]): Record<string, string> => {
    const examples: Record<string, string> = {}
    
    variables.forEach(variable => {
      switch (variable.toLowerCase()) {
        case 'code_diff':
          examples[variable] = '+ 新增代码行\n- 删除代码行'
          break
        case 'requirement':
          examples[variable] = '用户需要实现登录功能'
          break
        case 'context':
          examples[variable] = '这是一个Web应用项目'
          break
        case 'user_input':
          examples[variable] = '用户输入的内容'
          break
        default:
          examples[variable] = `示例${variable}`
      }
    })
    
    return examples
  },

  // 检查链式调用
  hasChainedCalls: (content: string): boolean => {
    return /\{\{\s*GENERATE_FROM:\s*\w+\s*\}\}/.test(content)
  },

  // 提取链式调用的模板ID
  extractChainedTemplates: (content: string): string[] => {
    const chainRegex = /\{\{\s*GENERATE_FROM:\s*(\w+)\s*\}\}/g
    const templates: string[] = []
    let match

    while ((match = chainRegex.exec(content)) !== null) {
      templates.push(match[1])
    }

    return templates
  },

  // 格式化使用次数
  formatUsageCount: (count: number): string => {
    if (count < 1000) {
      return count.toString()
    } else if (count < 1000000) {
      return (count / 1000).toFixed(1) + 'K'
    } else {
      return (count / 1000000).toFixed(1) + 'M'
    }
  }
}

export default promptsApi
