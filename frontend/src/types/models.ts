// 基础类型定义
export interface BaseModel {
  id: string
}

// 用户相关类型
export interface UserInfo {
  id: string
  username: string
  email: string
  nickname?: string
  avatar?: string
  department?: string
  position?: string
  roles: string[]
}

// Git 配置相关类型
export interface GitCredential {
  username: string
  token: string
}

export interface GitRepository extends BaseModel {
  alias: string
  url: string
  defaultBaseBranch?: string
}

// Prompt 模板相关类型
export interface PromptTemplate extends BaseModel {
  name: string
  identifier: string
  content: string
  description?: string
  tags: string[]
  category: 'requirement' | 'code_review' | 'test_case' | 'general'
  variables: string[]
  isPublic: boolean
  usageCount: number
}

// 知识库相关类型
export interface KnowledgeBase extends BaseModel {
  name: string
  description?: string
}

export interface KnowledgeDocument extends BaseModel {
  knowledgeBaseId: string
  filename: string
  fileType: string
  fileSize: number
  status: 'uploading' | 'processing' | 'completed' | 'failed'
}

// 任务相关类型
export type TaskStatus = 'pending' | 'queued' | 'running' | 'completed' | 'failed'

// 代码Diff相关类型
export interface CodeDiffTask extends BaseModel {
  name: string
  repositoryId: string
  sourceRef: string
  targetRef: string
  compareType: 'branch' | 'commit'
  status: TaskStatus
  diffContent?: string
  errorMessage?: string
}

// 需求文档相关类型
export interface RequirementDocument extends BaseModel {
  name: string
  originalContent: string
  optimizedContent?: string
  source: 'upload' | 'manual'
  originalFilename?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  parseTaskId?: string
}

// 流水线任务相关类型
export interface PipelineTask extends BaseModel {
  name: string
  type: 'code_review' | 'test_case' | 'requirement_testing'
  codeDiffTaskId?: string
  requirementDocumentId?: string
  promptTemplateId: string
  knowledgeBaseId?: string
  status: TaskStatus
  result?: string
  errorMessage?: string
}

export interface TestCaseTask extends BaseModel {
  name: string
  requirementTextId: string
  promptTemplateId: string
  caseTemplateId?: string
  status: TaskStatus
  result?: TestCase[]
  errorMessage?: string
}

export interface TestCase extends BaseModel {
  title: string
  preconditions: string
  steps: string
  expectedResult: string
  priority: 'P0' | 'P1' | 'P2'
}

export interface CaseTemplate extends BaseModel {
  name: string
  structure: Record<string, string>
}

// AI大模型配置相关类型
export interface AIModelConfig extends BaseModel {
  name: string
  provider: 'openai' | 'deepseek' | 'spark' | 'doubao' | 'gemini' | 'claude'
  baseUrl: string
  apiKey: string
  model: string
  maxTokens?: number
  temperature?: number
  isDefault: boolean
  isActive: boolean
}

// AI对话相关类型
export interface AIMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  modelConfig?: string
  promptTemplate?: string
  tokens?: number
}

export interface AIConversation extends BaseModel {
  title: string
  messages: AIMessage[]
  modelConfigId: string
  totalTokens: number
  lastMessageAt: string
}

// Prompt模板标签
export interface PromptTag {
  id: string
  name: string
  color: string
  category: 'requirement' | 'code_review' | 'test_case' | 'general'
}

// 测试点相关类型
export interface TestPoint extends BaseModel {
  name: string
  description: string
  type: TestPointType
  priority: TestPriority
  category: TestCategory
  preconditions: string[]
  steps: TestStep[]
  expectedResult: string
  actualResult?: string
  status: TestStatus
  requirementId: string
  assignee?: string
  estimatedTime?: number // 预估执行时间（分钟）
  tags: string[]
}

export interface TestStep {
  id: string
  stepNumber: number
  action: string
  expectedResult: string
  actualResult?: string
  status?: TestStatus
}

export type TestPointType = 'functional' | 'performance' | 'security' | 'usability' | 'compatibility' | 'integration'

export type TestPriority = 'high' | 'medium' | 'low'

export type TestCategory = 'smoke' | 'regression' | 'acceptance' | 'system' | 'unit' | 'api'

export type TestStatus = 'pending' | 'in_progress' | 'passed' | 'failed' | 'blocked' | 'skipped'

// 测试套件
export interface TestSuite extends BaseModel {
  name: string
  description: string
  requirementId: string
  testPointIds: string[]
  totalCount: number
  passedCount: number
  failedCount: number
  blockedCount: number
  progress: number
}

// 测试执行记录
export interface TestExecution extends BaseModel {
  testPointId: string
  executorId: string
  executorName: string
  status: TestStatus
  actualResult: string
  defects: string[]
  executionTime: number // 实际执行时间（分钟）
  screenshots: string[]
  notes: string
  executedAt: string
}

// 需求测试结果
export interface RequirementTestResult {
  id: string
  testName: string
  testType: 'functional' | 'performance' | 'security' | 'usability' | 'compatibility'
  priority: 'high' | 'medium' | 'low'
  description: string
  preconditions: string[]
  testSteps: RequirementTestStep[]
  expectedResult: string
  testData?: string
  notes?: string
  estimatedTime?: number // 预估执行时间（分钟）
  tags: string[]
}

export interface RequirementTestStep {
  stepNumber: number
  action: string
  expectedResult: string
  testData?: string
}

// 需求测试任务结果
export interface RequirementTestTaskResult {
  taskId: string
  requirementId: string
  requirementName: string
  promptTemplate: string
  totalTests: number
  testsByType: Record<string, number>
  testsByPriority: Record<string, number>
  testResults: RequirementTestResult[]
  summary: string
  recommendations: string[]
  generatedAt: string
}
