/**
 * API响应相关类型定义
 */

// 标准API响应格式
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp?: string
}

// 分页响应格式
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
  hasNext: boolean
  hasPrev: boolean
}

// 错误响应格式
export interface ErrorResponse {
  code: number
  message: string
  detail?: any
  errors?: any[]
}

// 统一ID类型定义（与后端保持一致）
export type EntityId = string

// 基础实体接口
export interface BaseEntity {
  id: EntityId
  createdAt: string
  updatedAt?: string
}

// 分页查询参数
export interface PaginationParams {
  page?: number
  size?: number
  skip?: number
  limit?: number
}

// 排序参数
export interface SortParams {
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

// 筛选参数
export interface FilterParams {
  status?: string
  category?: string
  [key: string]: any
}

// 通用查询参数
export interface QueryParams extends PaginationParams, SortParams, FilterParams {}

// 文件上传响应
export interface UploadResponse {
  id: EntityId
  filename: string
  originalFilename: string
  fileSize: number
  fileType: string
  filePath: string
  uploadedAt: string
}

// 任务状态
export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

// 任务进度
export interface TaskProgress {
  taskId: EntityId
  executionId: string
  status: TaskStatus
  progress: number
  currentStep: string
  stepsCompleted: number
  stepsTotal: number
  estimatedRemainingTime?: number
}

export default ApiResponse
