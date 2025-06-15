/**
 * 任务管理相关类型定义 - 支持三级分离架构
 */

import type { BaseModel } from './models'

// 任务状态枚举
export type TaskStatus = 
  | 'pending'
  | 'queued' 
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'

// 任务优先级
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

// 流水线类型
export type PipelineType = 
  | 'code_review'
  | 'test_generation' 
  | 'documentation'
  | 'requirement_testing'
  | 'security_check'

// ===== 第一级：代码差异任务 =====
export interface CodeDiffTask extends BaseModel {
  name: string
  description?: string
  repositoryId: number
  sourceBranch: string
  targetBranch: string
  diffType: 'branch' | 'commit' | 'file_upload'
  diffFilePath?: string
  diffContent?: string
  diffSummary?: string
  fileCount: number
  addedLines: number
  deletedLines: number
  modifiedFiles: string[]
  status: TaskStatus
  errorMessage?: string
  generatedAt?: string
  metadata?: Record<string, any>
}

export interface CreateCodeDiffTaskRequest {
  name: string
  description?: string
  repositoryId: number
  sourceBranch: string
  targetBranch: string
  diffType: 'branch' | 'commit' | 'file_upload'
  generateSummary?: boolean
}

// ===== 第二级：需求解析任务 =====
export interface RequirementParseTask extends BaseModel {
  name: string
  inputType: 'text' | 'file'
  originalContent?: string
  filePath?: string
  fileName?: string
  fileSize?: number
  parsedContent?: string
  structuredRequirements?: {
    summary?: string
    category?: string
    priority?: TaskPriority
    complexity?: string
    estimatedHours?: number
    requirements?: Array<{
      id: string
      title: string
      description: string
      type: string
      priority: TaskPriority
    }>
    testCriteria?: string[]
    dependencies?: string[]
    risks?: string[]
  }
  category?: string
  priority: TaskPriority
  complexity?: 'simple' | 'medium' | 'complex'
  estimatedHours?: number
  status: TaskStatus
  errorMessage?: string
  llmModel?: string
  tokensUsed?: number
  processingTime?: number
  taskMetadata?: Record<string, any>
}

export interface CreateRequirementParseTaskRequest {
  name: string
  inputType: 'text' | 'file'
  originalContent?: string
  category?: string
  priority?: TaskPriority
  autoGenerate?: boolean
}

// ===== 第三级：流水线任务 =====
export interface PipelineTask extends BaseModel {
  name: string
  description?: string
  
  // 关联的子任务（三级架构核心）
  codeDiffTaskId?: number
  requirementTaskId?: number
  
  // 直接关联资源（兼容性）
  codeDiffId?: number
  requirementTextId?: number
  
  // 流水线配置
  pipelineType: PipelineType
  promptTemplateId?: number
  knowledgeBaseId?: number
  
  // 执行配置
  config?: {
    temperature?: number
    maxTokens?: number
    enableRag?: boolean
    ragThreshold?: number
    customPrompt?: string
    outputFormat?: string
    [key: string]: any
  }
  
  // 任务状态
  status: TaskStatus
  
  // 执行结果
  result?: string
  resultData?: {
    summary?: string
    recommendations?: string[]
    issues?: Array<{
      type: string
      severity: 'low' | 'medium' | 'high' | 'critical'
      description: string
      suggestion?: string
    }>
    metrics?: Record<string, number>
    [key: string]: any
  }
  
  // 执行信息
  startedAt?: string
  completedAt?: string
  executionTime?: number
  errorMessage?: string
  llmModel?: string
  tokensUsed?: number
  taskMetadata?: Record<string, any>
}

export interface CreatePipelineTaskRequest {
  name: string
  description?: string
  pipelineType: PipelineType
  codeDiffTaskId?: number
  requirementTaskId?: number
  promptTemplateId?: number
  knowledgeBaseId?: number
  config?: Record<string, any>
  autoStart?: boolean
}

// ===== 任务执行跟踪 =====
export interface TaskExecution extends BaseModel {
  taskType: 'code_diff' | 'requirement_parse' | 'pipeline'
  taskId: number
  executionId: string
  status: TaskStatus
  startedAt?: string
  completedAt?: string
  stepsTotal: number
  stepsCompleted: number
  currentStep?: string
  result?: string
  errorMessage?: string
  logs?: string
  resourcesUsed?: {
    llmModel?: string
    tokensUsed?: number
    processingTime?: number
    [key: string]: any
  }
}

// ===== 任务统计 =====
export interface TaskStats {
  totalTasks: number
  pendingTasks: number
  runningTasks: number
  completedTasks: number
  failedTasks: number
  
  // 按类型分组
  tasksByType: {
    codeDiff: number
    requirementParse: number
    pipeline: number
  }
  
  // 按流水线类型分组
  pipelinesByType: {
    codeReview: number
    testGeneration: number
    documentation: number
    requirementTesting: number
    securityCheck: number
  }
  
  // 资源使用统计
  resourceUsage: {
    totalTokensUsed: number
    averageProcessingTime: number
    totalExecutionTime: number
  }
}

// ===== 任务选择器（用于关联任务） =====
export interface TaskSelector {
  id: number
  name: string
  status: TaskStatus
  createdAt: string
  description?: string
}

export interface CodeDiffTaskSelector extends TaskSelector {
  repositoryName?: string
  sourceBranch: string
  targetBranch: string
  fileCount: number
}

export interface RequirementTaskSelector extends TaskSelector {
  category?: string
  priority: TaskPriority
  complexity?: string
}

// ===== API响应类型 =====
export interface TaskListResponse<T> {
  tasks: T[]
  total: number
  page: number
  limit: number
  pages: number
  hasNext: boolean
  hasPrev: boolean
}

export interface TaskExecutionResponse {
  executionId: string
  status: TaskStatus
  progress: {
    stepsTotal: number
    stepsCompleted: number
    currentStep?: string
  }
  result?: any
  error?: string
} 