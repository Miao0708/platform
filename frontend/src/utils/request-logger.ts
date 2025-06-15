/**
 * 前端API请求日志工具
 */

interface RequestLogData {
  method: string
  url: string
  headers?: Record<string, string>
  body?: any
  timestamp: string
  requestId: string
}

interface ResponseLogData {
  status: number
  statusText: string
  headers?: Record<string, string>
  data?: any
  timestamp: string
  requestId: string
  duration: number
}

class RequestLogger {
  private isEnabled: boolean
  private requestMap: Map<string, number> = new Map()

  constructor(enabled = import.meta.env.DEV) {
    this.isEnabled = enabled
  }

  /**
   * 生成请求ID
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
  }

  /**
   * 记录请求信息
   */
  logRequest(config: any): string {
    if (!this.isEnabled) return ''
    
    const requestId = this.generateRequestId()
    const startTime = Date.now()
    this.requestMap.set(requestId, startTime)

    const logData: RequestLogData = {
      method: config.method?.toUpperCase() || 'GET',
      url: this.buildFullUrl(config),
      headers: this.filterSensitiveHeaders(config.headers || {}),
      body: config.data,
      timestamp: new Date().toISOString(),
      requestId
    }

    console.group(`📤 API请求 [${requestId}]`)
    console.log(`🔗 ${logData.method} ${logData.url}`)
    console.log('📋 请求头:', logData.headers)
    if (logData.body) {
      console.log('📦 请求体:', logData.body)
    }
    console.log('⏰ 发送时间:', logData.timestamp)
    console.groupEnd()

    return requestId
  }

  /**
   * 记录响应信息
   */
  logResponse(response: any, requestId: string) {
    if (!this.isEnabled || !requestId) return

    const endTime = Date.now()
    const startTime = this.requestMap.get(requestId) || endTime
    const duration = endTime - startTime
    this.requestMap.delete(requestId)

    const logData: ResponseLogData = {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      data: response.data,
      timestamp: new Date().toISOString(),
      requestId,
      duration
    }

    const statusColor = this.getStatusColor(response.status)
    
    console.group(`📥 API响应 [${requestId}] ${statusColor}`)
    console.log(`📊 状态: ${logData.status} ${logData.statusText}`)
    console.log(`⏱️ 耗时: ${duration}ms`)
    console.log('📋 响应头:', logData.headers)
    if (logData.data) {
      console.log('📦 响应数据:', logData.data)
    }
    console.log('⏰ 接收时间:', logData.timestamp)
    console.groupEnd()
  }

  /**
   * 记录请求错误
   */
  logError(error: any, requestId: string) {
    if (!this.isEnabled) return

    const endTime = Date.now()
    const startTime = this.requestMap.get(requestId) || endTime
    const duration = endTime - startTime
    this.requestMap.delete(requestId)

    console.group(`❌ API错误 [${requestId}]`)
    console.error('💥 错误信息:', error.message)
    if (error.response) {
      console.error('📊 响应状态:', error.response.status, error.response.statusText)
      console.error('📦 错误数据:', error.response.data)
    }
    console.error(`⏱️ 耗时: ${duration}ms`)
    console.error('⏰ 错误时间:', new Date().toISOString())
    console.groupEnd()
  }

  /**
   * 构建完整URL
   */
  private buildFullUrl(config: any): string {
    if (config.baseURL && config.url) {
      return `${config.baseURL}${config.url}`
    }
    return config.url || ''
  }

  /**
   * 过滤敏感请求头
   */
  private filterSensitiveHeaders(headers: Record<string, string>): Record<string, string> {
    const sensitiveHeaders = ['authorization', 'cookie', 'x-api-key']
    const filtered: Record<string, string> = {}
    
    for (const [key, value] of Object.entries(headers)) {
      if (sensitiveHeaders.includes(key.toLowerCase())) {
        filtered[key] = '***'
      } else {
        filtered[key] = value
      }
    }
    
    return filtered
  }

  /**
   * 获取状态码颜色
   */
  private getStatusColor(status: number): string {
    if (status >= 200 && status < 300) return '✅'
    if (status >= 300 && status < 400) return '🔄'
    if (status >= 400 && status < 500) return '⚠️'
    if (status >= 500) return '💥'
    return '❓'
  }

  /**
   * 启用/禁用日志
   */
  setEnabled(enabled: boolean) {
    this.isEnabled = enabled
  }

  /**
   * 清理过期的请求记录
   */
  cleanup() {
    const now = Date.now()
    for (const [requestId, startTime] of this.requestMap.entries()) {
      // 清理超过10分钟的未完成请求
      if (now - startTime > 10 * 60 * 1000) {
        this.requestMap.delete(requestId)
      }
    }
  }
}

// 创建全局实例
export const requestLogger = new RequestLogger()

// 定期清理
setInterval(() => {
  requestLogger.cleanup()
}, 5 * 60 * 1000) // 每5分钟清理一次

export default requestLogger 