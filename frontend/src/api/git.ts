import { api } from './index'

// Git凭证接口
export interface GitCredential {
  id: string
  username: string
  token: string
  is_active: boolean
  created_at: string
}

// Git仓库接口
export interface GitRepository {
  id: string
  alias: string
  url: string
  default_base_branch: string
  is_active: boolean
  created_at: string
}

// 创建Git凭证请求
export interface CreateGitCredentialRequest {
  username: string
  token: string
}

// 创建Git仓库请求
export interface CreateGitRepositoryRequest {
  alias: string
  url: string
  default_base_branch?: string
}

// 测试Git连接请求
export interface TestGitConnectionRequest {
  test_url?: string
}

// Git配置API
export const gitApi = {
  // === Git凭证管理 ===
  // 获取Git凭证列表
  getCredentials: () => 
    api.get('/git/credentials'),

  // 创建Git凭证
  createCredential: (data: CreateGitCredentialRequest) => 
    api.post('/git/credentials', data),

  // 更新Git凭证
  updateCredential: (id: string, data: Partial<CreateGitCredentialRequest>) => 
    api.put(`/git/credentials/${id}`, data),

  // 删除Git凭证
  deleteCredential: (id: string) => 
    api.delete(`/git/credentials/${id}`),

  // 激活Git凭证
  activateCredential: (id: string) => 
    api.post(`/git/credentials/${id}/activate`),

  // 测试Git连接
  testConnection: (data?: TestGitConnectionRequest) => 
    api.post('/git/credentials/test', data || {}),

  // === Git仓库管理 ===
  // 获取Git仓库列表
  getRepositories: () => 
    api.get('/git/repositories'),

  // 创建Git仓库配置
  createRepository: (data: CreateGitRepositoryRequest) => 
    api.post('/git/repositories', data),

  // 更新Git仓库配置
  updateRepository: (id: string, data: Partial<CreateGitRepositoryRequest>) => 
    api.put(`/git/repositories/${id}`, data),

  // 删除Git仓库配置
  deleteRepository: (id: string) => 
    api.delete(`/git/repositories/${id}`),

  // 激活Git仓库
  activateRepository: (id: string) => 
    api.post(`/git/repositories/${id}/activate`),

  // 获取仓库分支列表
  getBranches: (repositoryId: string) => 
    api.get(`/git/repositories/${repositoryId}/branches`),

  // 获取仓库提交列表
  getCommits: (repositoryId: string, branch?: string) => 
    api.get(`/git/repositories/${repositoryId}/commits`, { 
      params: { branch } 
    })
}

// Git工具函数
export const gitUtils = {
  // 验证Git URL格式
  isValidGitUrl: (url: string): boolean => {
    const gitUrlRegex = /^(https?:\/\/|git@)[\w\.-]+[\/:][\w\.-]+\/[\w\.-]+\.git$/
    return gitUrlRegex.test(url)
  },

  // 从Git URL提取仓库名称
  extractRepoName: (url: string): string => {
    const match = url.match(/\/([^\/]+)\.git$/)
    return match ? match[1] : ''
  },

  // 格式化Git URL显示
  formatGitUrl: (url: string): string => {
    if (url.length > 50) {
      return url.substring(0, 47) + '...'
    }
    return url
  },

  // 验证分支名称
  isValidBranchName: (branch: string): boolean => {
    // Git分支名称规则：不能包含空格、特殊字符等
    const branchRegex = /^[a-zA-Z0-9._/-]+$/
    return branchRegex.test(branch) && !branch.startsWith('-') && !branch.endsWith('.')
  },

  // 获取Git服务商
  getGitProvider: (url: string): string => {
    if (url.includes('github.com')) return 'GitHub'
    if (url.includes('gitlab.com')) return 'GitLab'
    if (url.includes('gitee.com')) return '码云'
    if (url.includes('coding.net')) return 'Coding'
    return '其他'
  },

  // 格式化凭证显示
  formatCredential: (credential: GitCredential): string => {
    return `${credential.username} (${credential.is_active ? '已激活' : '未激活'})`
  },

  // 验证Git凭证
  validateCredential: (data: CreateGitCredentialRequest): string[] => {
    const errors: string[] = []
    
    if (!data.username || data.username.trim().length === 0) {
      errors.push('用户名不能为空')
    }
    
    if (!data.token || data.token.trim().length === 0) {
      errors.push('访问令牌不能为空')
    }
    
    if (data.token && data.token.length < 10) {
      errors.push('访问令牌长度不能少于10位')
    }
    
    return errors
  },

  // 验证Git仓库配置
  validateRepository: (data: CreateGitRepositoryRequest): string[] => {
    const errors: string[] = []
    
    if (!data.alias || data.alias.trim().length === 0) {
      errors.push('仓库别名不能为空')
    }
    
    if (!data.url || data.url.trim().length === 0) {
      errors.push('仓库URL不能为空')
    } else if (!gitUtils.isValidGitUrl(data.url)) {
      errors.push('仓库URL格式不正确')
    }
    
    if (data.default_base_branch && !gitUtils.isValidBranchName(data.default_base_branch)) {
      errors.push('默认分支名称格式不正确')
    }
    
    return errors
  },

  // 生成Git配置建议
  generateConfigSuggestions: (url: string) => {
    const repoName = gitUtils.extractRepoName(url)
    const provider = gitUtils.getGitProvider(url)
    
    return {
      alias: repoName || '新仓库',
      default_base_branch: 'main',
      provider: provider,
      suggestions: [
        '建议使用有意义的别名',
        '确保访问令牌有足够的权限',
        '推荐使用main作为默认分支'
      ]
    }
  }
}

export default gitApi
