import { ElMessage } from 'element-plus'

export interface ApiError {
  code?: number
  message: string
  detail?: any
}

/**
 * API错误处理工具
 */
export class ErrorHandler {
  /**
   * 处理API错误响应
   */
  static handleApiError(error: any): void {
    console.error('API Error:', error)

    if (error.response) {
      const { status, data } = error.response
      this.handleHttpError(status, data)
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查网络连接')
    } else {
      ElMessage.error('请求配置错误')
    }
  }

  /**
   * 处理HTTP状态码错误
   */
  static handleHttpError(status: number, data: any): void {
    switch (status) {
      case 400:
        ElMessage.error(data?.message || data?.detail || '请求参数错误')
        break
      case 401:
        ElMessage.error('登录已过期，请重新登录')
        this.handleUnauthorized()
        break
      case 403:
        ElMessage.error('没有权限访问该资源')
        break
      case 404:
        ElMessage.error('请求的资源不存在')
        break
      case 422:
        this.handleValidationError(data)
        break
      case 500:
        ElMessage.error('服务器内部错误')
        break
      default:
        const message = data?.message || data?.detail || `HTTP ${status} 错误`
        ElMessage.error(message)
    }
  }

  /**
   * 处理验证错误
   */
  static handleValidationError(data: any): void {
    if (data?.detail && Array.isArray(data.detail)) {
      // FastAPI验证错误格式
      const errors = data.detail.map((err: any) => 
        `${err.loc?.join('.') || 'field'}: ${err.msg}`
      ).join(', ')
      ElMessage.error(`参数验证失败: ${errors}`)
    } else {
      ElMessage.error(data?.detail || data?.message || '请求参数验证失败')
    }
  }

  /**
   * 处理未授权错误
   */
  static handleUnauthorized(): void {
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    
    // 跳转到登录页
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
  }

  /**
   * 格式化错误消息
   */
  static formatErrorMessage(error: any): string {
    if (typeof error === 'string') {
      return error
    }
    
    if (error?.message) {
      return error.message
    }
    
    if (error?.detail) {
      return error.detail
    }
    
    return '未知错误'
  }
}

export default ErrorHandler 