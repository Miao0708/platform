import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types'

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // 直接设置API基础路径
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加 token 到请求头
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加调试日志
    console.log('API Request:', {
      url: config.url,
      method: config.method,
      baseURL: config.baseURL,
      headers: config.headers,
      data: config.data
    })

    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // 添加调试日志
    console.log('API Response:', {
      url: response.config.url,
      status: response.status,
      data: response.data
    })

    const { code, message, data } = response.data

    // 成功响应
    if (code === 200) {
      return data
    }

    // 业务错误
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message || '请求失败'))
  },
  (error) => {
    console.error('Response error:', error)
    
    // 处理不同的错误状态码
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          // 跳转到登录页 - 使用路由跳转而不是直接修改location
          if (typeof window !== 'undefined') {
            window.location.href = '/login'
          }
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.message || '网络错误')
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default request

// 导出常用的请求方法
export const api = {
  get: <T = any>(url: string, config?: InternalAxiosRequestConfig): Promise<T> =>
    request.get(url, config),

  post: <T = any>(url: string, data?: any, config?: InternalAxiosRequestConfig): Promise<T> =>
    request.post(url, data, config),

  put: <T = any>(url: string, data?: any, config?: InternalAxiosRequestConfig): Promise<T> =>
    request.put(url, data, config),

  delete: <T = any>(url: string, config?: InternalAxiosRequestConfig): Promise<T> =>
    request.delete(url, config),

  patch: <T = any>(url: string, data?: any, config?: InternalAxiosRequestConfig): Promise<T> =>
    request.patch(url, data, config)
}

// 导出所有 API 模块
export * from './ai'
export * from './auth'
export * from './users'

// 暂时注释掉不存在的模块，避免编译错误
// export * from './requirements'
// export * from './git'
// export * from './prompts'
// export * from './code-review'
// export * from './test-cases'
// export * from './tasks'
// export * from './dashboard'
// export * from './knowledge'
