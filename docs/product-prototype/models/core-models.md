# 核心数据模型定义

## 1. 基础模型

### 1.1 通用基础模型
```typescript
// 基础实体接口
interface BaseEntity {
  id: string
  createdAt: string
  updatedAt?: string
}

// 分页参数
interface PaginationParams {
  page?: number
  size?: number
  skip?: number
  limit?: number
}

// 分页响应
interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
  hasNext: boolean
  hasPrev: boolean
}

// API响应格式
interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp?: string
}

// 错误响应
interface ErrorResponse {
  code: number
  message: string
  detail?: any
  errors?: any[]
}
```

### 1.2 任务状态枚举
```typescript
export enum TaskStatus {
  PENDING = 'pending',
  QUEUED = 'queued',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent'
}
```

## 2. 用户相关模型

### 2.1 用户信息
```typescript
interface UserInfo extends BaseEntity {
  username: string
  email: string
  fullName?: string
  avatar?: string
  department?: string
  position?: string
  roles: UserRole[]
  isActive: boolean
  lastLoginAt?: string
  preferences: UserPreferences
}

interface UserRole {
  id: string
  name: string
  displayName: string
  permissions: Permission[]
}

interface Permission {
  id: string
  resource: string
  action: string
  scope?: string
}

interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: string
  timezone: string
  notifications: NotificationSettings
  dashboard: DashboardSettings
}

interface NotificationSettings {
  email: boolean
  browser: boolean
  taskCompleted: boolean
  taskFailed: boolean
  systemUpdates: boolean
}

interface DashboardSettings {
  autoRefresh: boolean
  refreshInterval: number
  defaultTimeRange: string
  hiddenWidgets: string[]
}
```

### 2.2 认证相关
```typescript
interface LoginRequest {
  username: string
  password: string
  remember?: boolean
  captcha?: string
}

interface LoginResponse {
  accessToken: string
  refreshToken: string
  tokenType: string
  expiresIn: number
  user: UserInfo
}

interface TokenInfo {
  accessToken: string
  refreshToken: string
  expiresAt: number
  isValid: boolean
}
```

## 3. AI相关模型

### 3.1 AI模型配置
```typescript
interface AIModelConfig extends BaseEntity {
  name: string
  identifier: string
  provider: AIProvider
  baseUrl: string
  apiKey: string
  model: string
  
  // 模型参数
  parameters: ModelParameters
  
  // 状态和配置
  isDefault: boolean
  isActive: boolean
  timeout: number
  
  // 使用统计
  usageStats: UsageStats
  
  // 额外配置
  extraConfig?: Record<string, any>
}

enum AIProvider {
  OPENAI = 'openai',
  DEEPSEEK = 'deepseek',
  SPARK = 'spark',
  DOUBAO = 'doubao',
  GEMINI = 'gemini',
  CLAUDE = 'claude',
  CUSTOM = 'custom'
}

interface ModelParameters {
  maxTokens?: number
  temperature?: number
  topP?: number
  frequencyPenalty?: number
  presencePenalty?: number
  stopSequences?: string[]
}

interface UsageStats {
  totalRequests: number
  totalTokensUsed: number
  avgResponseTime: number
  successRate: number
  lastUsedAt?: string
}
```

### 3.2 AI对话模型
```typescript
interface AIConversation extends BaseEntity {
  title: string
  messages: ChatMessage[]
  modelConfigId: string
  
  // 统计信息
  messageCount: number
  totalTokens: number
  lastMessageAt: string
  
  // 配置
  systemPrompt?: string
  context?: ConversationContext
  
  // 状态
  isArchived: boolean
  tags: string[]
}

interface ChatMessage extends BaseEntity {
  conversationId: string
  role: MessageRole
  content: string
  
  // 扩展信息
  model?: string
  promptTemplate?: string
  tokens?: number
  responseTime?: number
  
  // 附件
  attachments?: MessageAttachment[]
  
  // 状态
  status: MessageStatus
  error?: string
  
  // 用户反馈
  feedback?: MessageFeedback
}

enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}

enum MessageStatus {
  SENDING = 'sending',
  SENT = 'sent',
  FAILED = 'failed',
  REGENERATING = 'regenerating'
}

interface MessageAttachment {
  id: string
  type: 'image' | 'file' | 'code' | 'link'
  name: string
  size?: number
  url?: string
  mimeType?: string
  metadata?: Record<string, any>
}

interface MessageFeedback {
  rating: 'like' | 'dislike'
  comment?: string
  timestamp: string
}

interface ConversationContext {
  knowledgeBaseIds?: string[]
  documentIds?: string[]
  customContext?: Record<string, any>
}
```

### 3.3 Prompt模板模型
```typescript
interface PromptTemplate extends BaseEntity {
  name: string
  identifier: string
  content: string
  description?: string
  
  // 分类和标签
  category: PromptCategory
  tags: string[]
  
  // 变量定义
  variables: PromptVariable[]
  
  // 状态和权限
  isPublic: boolean
  isSystem: boolean
  
  // 使用统计
  usageCount: number
  
  // 版本控制
  version: string
  parentId?: string
}

enum PromptCategory {
  REQUIREMENT = 'requirement',
  CODE_REVIEW = 'code_review',
  TEST_CASE = 'test_case',
  DOCUMENTATION = 'documentation',
  GENERAL = 'general'
}

interface PromptVariable {
  name: string
  type: VariableType
  description?: string
  defaultValue?: string
  required: boolean
  options?: string[]
  validation?: VariableValidation
}

enum VariableType {
  TEXT = 'text',
  TEXTAREA = 'textarea',
  NUMBER = 'number',
  SELECT = 'select',
  CHECKBOX = 'checkbox',
  DATE = 'date'
}

interface VariableValidation {
  minLength?: number
  maxLength?: number
  pattern?: string
  min?: number
  max?: number
}
```

## 4. 任务相关模型

### 4.1 代码差异任务
```typescript
interface CodeDiffTask extends BaseEntity {
  name: string
  description?: string
  
  // Git信息
  repositoryId: string
  sourceBranch: string
  targetBranch: string
  compareType: 'branch' | 'commit' | 'file_upload'
  
  // 差异内容
  diffContent?: string
  diffSummary?: DiffSummary
  
  // 状态
  status: TaskStatus
  errorMessage?: string
  
  // 统计信息
  fileCount: number
  addedLines: number
  deletedLines: number
  modifiedFiles: string[]
  
  // 执行信息
  startedAt?: string
  completedAt?: string
  executionTime?: number
  
  // 元数据
  metadata?: Record<string, any>
}

interface DiffSummary {
  totalFiles: number
  totalAdditions: number
  totalDeletions: number
  fileChanges: FileChange[]
}

interface FileChange {
  path: string
  changeType: 'added' | 'modified' | 'deleted' | 'renamed'
  additions: number
  deletions: number
  oldPath?: string
}
```

### 4.2 需求解析任务
```typescript
interface RequirementParseTask extends BaseEntity {
  name: string
  
  // 输入信息
  inputType: 'text' | 'file'
  originalContent?: string
  filePath?: string
  fileName?: string
  fileSize?: number
  
  // 解析结果
  parsedContent?: string
  structuredRequirements?: StructuredRequirement
  
  // 分类信息
  category?: RequirementCategory
  priority: TaskPriority
  complexity?: RequirementComplexity
  estimatedHours?: number
  
  // 状态
  status: TaskStatus
  errorMessage?: string
  
  // AI处理信息
  llmModel?: string
  tokensUsed?: number
  processingTime?: number
  
  // 元数据
  taskMetadata?: Record<string, any>
}

interface StructuredRequirement {
  summary?: string
  category?: string
  priority?: TaskPriority
  complexity?: RequirementComplexity
  estimatedHours?: number
  
  requirements?: RequirementItem[]
  testCriteria?: string[]
  dependencies?: string[]
  risks?: string[]
  acceptanceCriteria?: string[]
}

interface RequirementItem {
  id: string
  title: string
  description: string
  type: RequirementType
  priority: TaskPriority
  status: 'draft' | 'approved' | 'rejected'
}

enum RequirementCategory {
  FUNCTIONAL = 'functional',
  NON_FUNCTIONAL = 'non_functional',
  BUSINESS = 'business',
  TECHNICAL = 'technical',
  SECURITY = 'security',
  PERFORMANCE = 'performance'
}

enum RequirementComplexity {
  SIMPLE = 'simple',
  MEDIUM = 'medium',
  COMPLEX = 'complex'
}

enum RequirementType {
  FEATURE = 'feature',
  ENHANCEMENT = 'enhancement',
  BUG_FIX = 'bug_fix',
  REFACTOR = 'refactor'
}
```

### 4.3 流水线任务
```typescript
interface PipelineTask extends BaseEntity {
  name: string
  description?: string
  
  // 关联任务
  codeDiffTaskId?: string
  requirementTaskId?: string
  
  // 流水线配置
  pipelineType: PipelineType
  promptTemplateId?: string
  knowledgeBaseId?: string
  
  // 执行配置
  config?: PipelineConfig
  
  // 步骤定义
  steps: PipelineStep[]
  currentStep?: number
  
  // 状态
  status: TaskStatus
  
  // 结果
  result?: string
  resultData?: PipelineResult
  
  // 执行信息
  startedAt?: string
  completedAt?: string
  executionTime?: number
  errorMessage?: string
  
  // AI信息
  llmModel?: string
  tokensUsed?: number
  
  // 元数据
  taskMetadata?: Record<string, any>
}

enum PipelineType {
  CODE_REVIEW = 'code_review',
  TEST_GENERATION = 'test_generation',
  DOCUMENTATION = 'documentation',
  REQUIREMENT_TESTING = 'requirement_testing',
  SECURITY_CHECK = 'security_check'
}

interface PipelineConfig {
  temperature?: number
  maxTokens?: number
  enableRag?: boolean
  ragThreshold?: number
  customPrompt?: string
  outputFormat?: string
  [key: string]: any
}

interface PipelineStep {
  id: string
  name: string
  type: string
  config: Record<string, any>
  status: TaskStatus
  result?: any
  errorMessage?: string
  executionTime?: number
}

interface PipelineResult {
  summary?: string
  recommendations?: string[]
  issues?: PipelineIssue[]
  metrics?: Record<string, number>
  [key: string]: any
}

interface PipelineIssue {
  type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
  suggestion?: string
  location?: string
}
```

## 5. 测试相关模型

### 5.1 测试用例
```typescript
interface TestCase extends BaseEntity {
  title: string
  description: string
  
  // 测试内容
  preconditions: string
  steps: TestStep[]
  expectedResult: string
  
  // 分类信息
  priority: TestPriority
  type: TestType
  category: TestCategory
  
  // 关联信息
  requirementId?: string
  moduleId?: string
  
  // 状态
  status: TestStatus
  
  // 执行信息
  actualResult?: string
  executorId?: string
  executedAt?: string
  executionTime?: number
  
  // 缺陷信息
  defects?: string[]
  screenshots?: string[]
  
  // 标签和元数据
  tags: string[]
  metadata?: Record<string, any>
}

interface TestStep {
  stepNumber: number
  action: string
  expectedResult: string
  actualResult?: string
  status?: TestStatus
}

enum TestPriority {
  P0 = 'P0',
  P1 = 'P1',
  P2 = 'P2',
  P3 = 'P3'
}

enum TestType {
  FUNCTIONAL = 'functional',
  PERFORMANCE = 'performance',
  SECURITY = 'security',
  USABILITY = 'usability',
  COMPATIBILITY = 'compatibility',
  INTEGRATION = 'integration'
}

enum TestCategory {
  SMOKE = 'smoke',
  REGRESSION = 'regression',
  ACCEPTANCE = 'acceptance',
  SYSTEM = 'system',
  UNIT = 'unit',
  API = 'api'
}

enum TestStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  PASSED = 'passed',
  FAILED = 'failed',
  BLOCKED = 'blocked',
  SKIPPED = 'skipped'
}
```

### 5.2 测试套件
```typescript
interface TestSuite extends BaseEntity {
  name: string
  description: string
  
  // 关联信息
  requirementId?: string
  testCaseIds: string[]
  
  // 统计信息
  totalCount: number
  passedCount: number
  failedCount: number
  blockedCount: number
  skippedCount: number
  progress: number
  
  // 执行信息
  executorId?: string
  executedAt?: string
  executionTime?: number
  
  // 状态
  status: TestStatus
}

interface TestExecution extends BaseEntity {
  testCaseId: string
  testSuiteId?: string
  
  // 执行者信息
  executorId: string
  executorName: string
  
  // 执行结果
  status: TestStatus
  actualResult: string
  defects: string[]
  
  // 执行时间
  startedAt: string
  completedAt?: string
  executionTime: number
  
  // 附件
  screenshots: string[]
  logs?: string
  notes?: string
  
  // 环境信息
  environment?: TestEnvironment
}

interface TestEnvironment {
  os: string
  browser?: string
  version?: string
  device?: string
  resolution?: string
  [key: string]: any
}
```

## 6. 配置相关模型

### 6.1 Git配置
```typescript
interface GitCredential extends BaseEntity {
  username: string
  token: string
  provider: GitProvider
  isActive: boolean
  description?: string
}

interface GitRepository extends BaseEntity {
  alias: string
  url: string
  defaultBaseBranch: string
  credentialId?: string
  isActive: boolean
  
  // 缓存信息
  lastSyncAt?: string
  branchCount?: number
  commitCount?: number
  
  // 统计信息
  usageCount: number
  lastUsedAt?: string
}

enum GitProvider {
  GITHUB = 'github',
  GITLAB = 'gitlab',
  GITEE = 'gitee',
  CODING = 'coding',
  CUSTOM = 'custom'
}
```

### 6.2 知识库
```typescript
interface KnowledgeBase extends BaseEntity {
  name: string
  description?: string
  
  // 统计信息
  documentCount: number
  totalSize: number
  vectorCount: number
  
  // 状态
  isActive: boolean
  
  // 配置
  config?: KnowledgeBaseConfig
}

interface KnowledgeDocument extends BaseEntity {
  knowledgeBaseId: string
  filename: string
  originalFilename: string
  fileType: string
  fileSize: number
  
  // 内容
  content?: string
  summary?: string
  
  // 向量化信息
  vectorCount: number
  chunkCount: number
  
  // 状态
  status: DocumentStatus
  errorMessage?: string
  
  // 处理信息
  processedAt?: string
  processingTime?: number
  
  // 元数据
  metadata?: Record<string, any>
}

enum DocumentStatus {
  UPLOADING = 'uploading',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

interface KnowledgeBaseConfig {
  chunkSize: number
  chunkOverlap: number
  embeddingModel: string
  searchThreshold: number
  maxResults: number
}
```

## 7. 系统统计模型

### 7.1 仪表盘统计
```typescript
interface DashboardStats {
  // 任务统计
  totalTasks: number
  completedTasks: number
  runningTasks: number
  failedTasks: number
  
  // 资源使用
  totalTokensUsed: number
  apiCallsToday: number
  
  // 用户活动
  activeUsers: number
  totalUsers: number
  
  // 最近任务
  recentTasks: RecentTaskInfo[]
}

interface RecentTaskInfo {
  id: string
  name: string
  type: string
  status: TaskStatus
  createdAt: string
  progress?: number
}

interface TaskTrendData {
  date: string
  totalTasks: number
  completedTasks: number
  failedTasks: number
}

interface ModelUsageStats {
  modelName: string
  provider: string
  usageCount: number
  totalTokens: number
  averageResponseTime: number
  successRate: number
}
```

### 7.2 系统资源监控
```typescript
interface SystemResourceStats {
  cpu: ResourceMetric
  memory: ResourceMetric
  storage: ResourceMetric
  network: NetworkMetric
  
  // API统计
  apiStats: ApiStats
  
  // 数据库统计
  dbStats: DatabaseStats
}

interface ResourceMetric {
  usage: number
  total: number
  available: number
  status: 'normal' | 'warning' | 'critical'
}

interface NetworkMetric {
  inbound: number
  outbound: number
  latency: number
  status: 'normal' | 'warning' | 'critical'
}

interface ApiStats {
  totalRequests: number
  successfulRequests: number
  failedRequests: number
  averageResponseTime: number
  rateLimit: number
}

interface DatabaseStats {
  connections: number
  maxConnections: number
  queryTime: number
  cacheHitRate: number
}
``` 