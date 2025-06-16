/**
 * 需求管理系统类型定义
 */

// 需求文档状态
export type RequirementStatus = 'pending' | 'processing' | 'completed' | 'failed'

// 任务状态
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed'

// 文件类型
export type FileType = 'txt' | 'md' | 'pdf' | 'docx'

// 需求文档接口
export interface RequirementDocument {
  id: number
  name: string
  original_content: string
  optimized_content?: string
  source: 'upload' | 'manual'
  original_filename?: string
  file_type?: FileType
  status: RequirementStatus
  prompt_template_id?: number
  model_config_id?: number
  parse_task_id?: string
  error_message?: string
  task_started_at?: string
  task_completed_at?: string
  created_at: string
  updated_at?: string
  // 前端使用的临时状态
  processing?: boolean
}

// 创建需求文档请求
export interface CreateRequirementDocumentRequest {
  name: string
  original_content: string
  source: 'upload' | 'manual'
  original_filename?: string
  file_type?: FileType
  prompt_template_id?: number
  model_config_id?: number
}

// 更新需求文档请求
export interface UpdateRequirementDocumentRequest {
  name?: string
  original_content?: string
  optimized_content?: string
  prompt_template_id?: number
  model_config_id?: number
  status?: RequirementStatus
}

// 需求分析任务接口
export interface RequirementAnalysisTask {
  id: number
  requirement_document_id: number
  prompt_template_id: number
  model_config_id: number
  status: TaskStatus
  result?: string
  error_message?: string
  tokens_used?: number
  execution_time?: number
  started_at?: string
  completed_at?: string
  created_at: string
  updated_at?: string
}

// 创建需求分析任务请求
export interface CreateRequirementAnalysisTaskRequest {
  requirement_document_id: number
  prompt_template_id: number
  model_config_id: number
}

// 需求测试分析任务接口
export interface RequirementTestTask {
  id: number
  name: string
  requirement_id?: number
  requirement_content?: string
  prompt_template_id: number
  model_config_id: number
  status: TaskStatus
  result?: Record<string, any>
  error_message?: string
  tokens_used?: number
  execution_time?: number
  started_at?: string
  completed_at?: string
  created_at: string
  updated_at?: string
}

// 创建需求测试分析任务请求
export interface CreateRequirementTestTaskRequest {
  name: string
  requirement_id?: number
  requirement_content?: string
  prompt_template_id: number
  model_config_id: number
}

// 文件上传响应
export interface FileUploadResponse {
  filename: string
  file_type: string
  file_size: number
  content: string
}

// 支持的文件类型响应
export interface SupportedFileTypesResponse {
  supported_types: string[]
  max_file_size_mb: number
}

// 列表查询参数
export interface RequirementDocumentListParams {
  status?: RequirementStatus
  skip?: number
  limit?: number
}

export interface RequirementTestTaskListParams {
  status?: TaskStatus
  skip?: number
  limit?: number
}

// 状态选项
export const REQUIREMENT_STATUS_OPTIONS = [
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已完成', value: 'completed' },
  { label: '失败', value: 'failed' }
] as const

export const TASK_STATUS_OPTIONS = [
  { label: '待执行', value: 'pending' },
  { label: '执行中', value: 'running' },
  { label: '已完成', value: 'completed' },
  { label: '失败', value: 'failed' }
] as const

// 状态颜色映射
export const STATUS_COLOR_MAP = {
  pending: 'warning',
  processing: 'primary',
  running: 'primary',
  completed: 'success',
  failed: 'danger'
} as const

// 文件类型图标映射
export const FILE_TYPE_ICON_MAP = {
  txt: 'DocumentText',
  md: 'DocumentText',
  pdf: 'Document',
  docx: 'Document'
} as const 