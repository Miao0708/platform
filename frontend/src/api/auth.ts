import { api } from './index'

// 认证相关API接口

// 登录请求参数
export interface LoginRequest {
  username: string
  password: string
}

// 登录响应数据
export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
    id: string
    username: string
    email: string
    nickname?: string
    role: string
  }
}

// 注册请求参数
export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
}

// 刷新Token请求参数
export interface RefreshTokenRequest {
  refresh_token: string
}

// 认证API
export const authApi = {
  // 用户登录 - 使用JSON格式
  login: (data: LoginRequest): Promise<LoginResponse> =>
    api.post('/auth/login', data),

  // 用户注册
  register: (data: RegisterRequest) =>
    api.post('/auth/register', data),

  // 刷新Token
  refreshToken: (data: RefreshTokenRequest) =>
    api.post('/auth/refresh', data),

  // 用户登出
  logout: () =>
    api.post('/auth/logout'),

  // 获取当前用户会话信息
  getCurrentSession: () =>
    api.get('/auth/session'),

  // 获取用户登录日志
  getLoginLogs: (params?: { page?: number; limit?: number }) =>
    api.get('/auth/logs', { params }),

  // 获取用户统计信息
  getUserStats: () =>
    api.get('/auth/stats')
}

// 认证工具函数
export const authUtils = {
  // 保存Token到localStorage
  saveToken: (token: string) => {
    localStorage.setItem('token', token)
  },

  // 获取Token
  getToken: (): string | null => {
    return localStorage.getItem('token')
  },

  // 清除Token
  clearToken: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  },

  // 检查是否已登录
  isLoggedIn: (): boolean => {
    const token = localStorage.getItem('token')
    return !!token
  },

  // 解析Token获取用户信息（简单解析，生产环境建议使用jwt库）
  parseToken: (token: string) => {
    try {
      const payload = token.split('.')[1]
      const decoded = atob(payload)
      return JSON.parse(decoded)
    } catch (error) {
      console.error('Token解析失败:', error)
      return null
    }
  },

  // 检查Token是否即将过期（提前5分钟刷新）
  isTokenExpiringSoon: (token: string): boolean => {
    const payload = authUtils.parseToken(token)
    if (!payload || !payload.exp) return true
    
    const expirationTime = payload.exp * 1000 // 转换为毫秒
    const currentTime = Date.now()
    const fiveMinutes = 5 * 60 * 1000 // 5分钟
    
    return (expirationTime - currentTime) < fiveMinutes
  }
}

export default authApi
