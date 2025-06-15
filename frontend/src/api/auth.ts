import { api } from './index'

// 认证相关API接口

// 登录请求参数
export interface LoginRequest {
  username: string
  password: string
}

// 登录响应数据
export interface LoginResponse {
  accessToken: string
  tokenType: string
  user: {
    id: number
    username: string
    isSuperuser: boolean
  }
}

// 注册请求参数
export interface RegisterRequest {
  username: string
  password: string
}

// 认证API
export const authApi = {
  // 用户登录
  login: (data: LoginRequest): Promise<LoginResponse> =>
    api.post('/auth/login', data),

  // 用户注册
  register: (data: RegisterRequest) =>
    api.post('/auth/register', data)
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
  }
}

export default authApi
