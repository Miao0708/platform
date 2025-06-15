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
  token_type: string
  expires_in: number
  user: {
    id: number
    username: string
    email: string
    full_name: string
    is_active: boolean
    created_at: string
  }
}

// 注册请求参数
export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name: string
}

// 认证API
export const authApi = {
  // 用户登录
  login: (data: LoginRequest): Promise<LoginResponse> =>
    api.post('/auth/login', data),

  // 用户注册
  register: (data: RegisterRequest) =>
    api.post('/auth/register', data),

  // 刷新Token
  refreshToken: () =>
    api.post('/auth/refresh')
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

  // 解析Token获取用户信息（简化Token格式：user_id:token:timestamp）
  parseToken: (token: string) => {
    try {
      const parts = token.split(':')
      if (parts.length !== 3) return null
      
      const [userId, tokenPart, timestamp] = parts
      return {
        userId: userId,
        timestamp: parseInt(timestamp),
        exp: parseInt(timestamp) + (30 * 24 * 60 * 60) // 30天后过期
      }
    } catch (error) {
      console.error('Token解析失败:', error)
      return null
    }
  },

  // 检查Token是否即将过期（提前1天刷新）
  isTokenExpiringSoon: (token: string): boolean => {
    const payload = authUtils.parseToken(token)
    if (!payload || !payload.exp) return true
    
    const expirationTime = payload.exp * 1000 // 转换为毫秒
    const currentTime = Date.now()
    const oneDay = 24 * 60 * 60 * 1000 // 1天
    
    return (expirationTime - currentTime) < oneDay
  }
}

export default authApi
