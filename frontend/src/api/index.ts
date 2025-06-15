import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types'
import { convertKeysToCamelCase, convertKeysToSnakeCase } from '@/utils/caseConverter'
import { requestLogger } from '@/utils/request-logger'

// 根据环境设置 API 基础路径
const getBaseURL = () => {
  // 开发环境使用代理，生产环境使用环境变量或默认值
  if (import.meta.env.DEV) {
    return '/api/v1' // 开发环境通过 Vite 代理
  } else {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  }
}

// 创建 axios 实例
const request: AxiosInstance = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 记录请求日志
    const requestId = requestLogger.logRequest(config)
    // 将requestId存储在config中，供响应拦截器使用
    ;(config as any).metadata = { requestId }

    // 添加 token 到请求头
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 数据格式转换：前端camelCase -> 后端snake_case
    if (config.data && typeof config.data === 'object') {
      // 对于表单数据或特殊数据类型，跳过转换
      if (!(config.data instanceof FormData) && !(config.data instanceof ArrayBuffer)) {
        config.data = convertKeysToSnakeCase(config.data)
      }
    }

    // URL参数转换
    if (config.params && typeof config.params === 'object') {
      config.params = convertKeysToSnakeCase(config.params)
    }

    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // 记录响应日志
    const requestId = (response.config as any).metadata?.requestId
    requestLogger.logResponse(response, requestId)

    // 数据格式转换：确保响应数据为camelCase格式
    let responseData = response.data
    if (responseData && typeof responseData === 'object') {
      responseData = convertKeysToCamelCase(responseData)
    }

    // 检查是否是标准化API响应格式
    if (responseData && typeof responseData === 'object' && 'code' in responseData) {
      const { code, message, data } = responseData as ApiResponse
      
      // 成功响应
      if (code === 200) {
        return data !== null ? data : responseData  // 如果data为null，返回整个response
      }

      // 业务错误
      ElMessage.error(message || '请求失败')
      return Promise.reject(new Error(message || '请求失败'))
    }

    // 直接返回数据（非标准化格式）
    return responseData
  },
  (error) => {
    // 记录错误日志
    const requestId = (error.config as any)?.metadata?.requestId
    requestLogger.logError(error, requestId)
    
    console.error('Response error:', error)
    
    // 处理不同的错误状态码
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
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
        case 422:
          // 处理验证错误
          const errorMessage = data?.detail || '请求参数验证失败'
          ElMessage.error(errorMessage)
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          const message = data?.message || data?.detail || '网络错误'
          ElMessage.error(message)
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default request

// 导出常用的请求方法
export const api = {
  get: <T = any>(url: string, config?: any): Promise<T> =>
    request.get(url, config),

  post: <T = any>(url: string, data?: any, config?: any): Promise<T> =>
    request.post(url, data, config),

  put: <T = any>(url: string, data?: any, config?: any): Promise<T> =>
    request.put(url, data, config),

  delete: <T = any>(url: string, config?: any): Promise<T> =>
    request.delete(url, config),

  patch: <T = any>(url: string, data?: any, config?: any): Promise<T> =>
    request.patch(url, data, config)
}

// 导出所有 API 模块
export * from './ai'
export * from './auth'
export * from './users'

// 新增的API模块
export * from './ai-models'
export * from './code-diff'
export * from './pipelines'
export * from './chat'

// 现有的API模块
export * from './requirements'
export * from './prompts'
export * from './tasks'
export * from './test-cases'
export * from './knowledge'
export * from './dashboard'
export * from './git'
