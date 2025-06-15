import { api } from './index'

// Git托管平台类型
export type GitPlatform = 'github' | 'gitlab' | 'gitee' | 'coding' | 'custom'

// Git平台配置接口
export interface GitPlatformConfig {
  id: string
  name: string  // 平台名称，如：公司GitHub、个人GitLab
  platform: GitPlatform  // 平台类型
  username: string
  token: string
  baseUrl?: string  // 自定义平台的基础URL
  isActive: boolean
  createdAt: string
  updatedAt: string
}

// Git仓库接口
export interface GitRepository {
  id: string
  alias: string
  url: string
  defaultBaseBranch: string
  platformConfigId: string  // 关联的平台配置ID
  platformName?: string  // 平台配置名称（用于显示）
  isActive: boolean
  createdAt: string
  updatedAt: string
}

// 创建Git平台配置请求
export interface CreateGitPlatformRequest {
  name: string
  platform: GitPlatform
  username: string
  token: string
  baseUrl?: string
}

// 创建Git仓库请求
export interface CreateGitRepositoryRequest {
  alias: string
  url: string
  defaultBaseBranch?: string
  platformConfigId: string
}

// 测试Git连接请求
export interface TestGitConnectionRequest {
  platformConfigId?: string
  testUrl?: string
}

// 保持旧接口兼容性
export interface GitCredential extends GitPlatformConfig {}
export interface CreateGitCredentialRequest extends CreateGitPlatformRequest {}

// Git配置API
export const gitApi = {
  // === Git平台配置管理 ===
  // 获取Git平台配置列表
  getPlatformConfigs: () => 
    api.get('/git/platform-configs'),

  // 创建Git平台配置
  createPlatformConfig: (data: CreateGitPlatformRequest) => 
    api.post('/git/platform-configs', data),

  // 更新Git平台配置
  updatePlatformConfig: (id: string, data: Partial<CreateGitPlatformRequest>) => 
    api.put(`/git/platform-configs/${id}`, data),

  // 删除Git平台配置
  deletePlatformConfig: (id: string) => 
    api.delete(`/git/platform-configs/${id}`),

  // 测试Git平台连接
  testPlatformConnection: (data: TestGitConnectionRequest) => 
    api.post('/git/platform-configs/test', data),

  // 兼容旧API
  getCredentials: () => 
    api.get('/git/platform-configs'),

  createCredential: (data: CreateGitCredentialRequest) => 
    api.post('/git/platform-configs', data),

  updateCredential: (id: string, data: Partial<CreateGitCredentialRequest>) => 
    api.put(`/git/platform-configs/${id}`, data),

  deleteCredential: (id: string) => 
    api.delete(`/git/platform-configs/${id}`),

  testConnection: (data?: TestGitConnectionRequest) => 
    api.post('/git/platform-configs/test', data || {}),

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
  // Git平台选项
  platformOptions: [
    { label: 'GitHub', value: 'github' as GitPlatform },
    { label: 'GitLab', value: 'gitlab' as GitPlatform },
    { label: '码云 Gitee', value: 'gitee' as GitPlatform },
    { label: 'Coding', value: 'coding' as GitPlatform },
    { label: '自定义平台', value: 'custom' as GitPlatform }
  ],

  // 获取平台图标
  getPlatformIcon: (platform: GitPlatform): string => {
    const iconMap: Record<GitPlatform, string> = {
      github: 'github',
      gitlab: 'gitlab',
      gitee: 'gitee',
      coding: 'coding',
      custom: 'git'
    }
    return iconMap[platform] || 'git'
  },

  // 获取平台颜色
  getPlatformColor: (platform: GitPlatform): string => {
    const colorMap: Record<GitPlatform, string> = {
      github: '#24292e',
      gitlab: '#fc6d26',
      gitee: '#c71d23',
      coding: '#00d8ff',
      custom: '#666666'
    }
    return colorMap[platform] || '#666666'
  },

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
    const branchRegex = /^[a-zA-Z0-9._/-]+$/
    return branchRegex.test(branch) && !branch.startsWith('-') && !branch.endsWith('.')
  },

  // 从URL自动识别Git平台
  detectPlatform: (url: string): GitPlatform => {
    if (url.includes('github.com')) return 'github'
    if (url.includes('gitlab.com')) return 'gitlab'
    if (url.includes('gitee.com')) return 'gitee'
    if (url.includes('coding.net')) return 'coding'
    return 'custom'
  },

  // 验证Git平台配置
  validatePlatformConfig: (data: CreateGitPlatformRequest): string[] => {
    const errors: string[] = []
    
    if (!data.name || data.name.trim().length === 0) {
      errors.push('平台名称不能为空')
    }
    
    if (!data.username || data.username.trim().length === 0) {
      errors.push('用户名不能为空')
    }
    
    if (!data.token || data.token.trim().length === 0) {
      errors.push('访问令牌不能为空')
    }
    
    if (data.token && data.token.length < 10) {
      errors.push('访问令牌长度不能少于10位')
    }
    
    if (data.platform === 'custom' && (!data.baseUrl || data.baseUrl.trim().length === 0)) {
      errors.push('自定义平台需要提供基础URL')
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
    
    if (!data.platformConfigId || data.platformConfigId.trim().length === 0) {
      errors.push('请选择Git平台配置')
    }
    
    if (data.defaultBaseBranch && !gitUtils.isValidBranchName(data.defaultBaseBranch)) {
      errors.push('默认分支名称格式不正确')
    }
    
    return errors
  }
}

export default gitApi
