// API 请求响应类型定义

// 通用响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PaginationParams {
  page: number
  pageSize: number
}

export interface PaginationResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

// Git 配置 API 类型
export interface TestConnectionRequest {
  username: string
  token: string
  repositoryUrl?: string
}

export interface TestConnectionResponse {
  success: boolean
  message: string
}

export interface CreateRepositoryRequest {
  alias: string
  url: string
  defaultBaseBranch?: string
}

// Prompt 模板 API 类型
export interface CreatePromptRequest {
  name: string
  identifier: string
  content: string
  description?: string
}

export interface UpdatePromptRequest extends Partial<CreatePromptRequest> {
  id: string
}

// 知识库 API 类型
export interface CreateKnowledgeBaseRequest {
  name: string
  description?: string
}

export interface UploadDocumentRequest {
  knowledgeBaseId: string
  file: File
}

// 代码 Diff API 类型
export interface GenerateDiffRequest {
  repositoryId: string
  compareType: 'branch' | 'commit'
  sourceRef: string
  targetRef: string
}

// 需求文本 API 类型
export interface CreateRequirementRequest {
  content: string
  source: 'upload' | 'manual'
  originalFilename?: string
}

export interface OptimizeRequirementRequest {
  requirementTextId: string
  promptTemplateId: string
}

// 任务 API 类型
export interface CreateReviewTaskRequest {
  name: string
  codeDiffId: string
  requirementTextId: string
  promptTemplateId: string
  knowledgeBaseId?: string
}

export interface CreateTestCaseTaskRequest {
  name: string
  requirementTextId: string
  promptTemplateId: string
  caseTemplateId?: string
}

export interface ExecuteTaskRequest {
  taskId: string
}

// 文件上传类型
export interface FileUploadResponse {
  filename: string
  url: string
  size: number
}
