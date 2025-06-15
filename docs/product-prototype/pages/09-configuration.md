# 配置管理页面原型

## 页面概述
配置管理页面提供系统全局配置功能，包括AI模型配置、Git仓库配置、知识库管理、Prompt模板管理等核心系统设置，支持多环境配置和版本管理。

## 页面布局

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            系统配置管理                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ [环境选择▼] [配置版本▼] [导入配置] [导出配置] [备份配置] [配置历史]              │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────┐ ┌───────────────────────────────────────────────┐ │
│ │       配置分类菜单       │ │              配置详情区域                     │ │
│ │                         │ │                                               │ │
│ │ 🤖 AI模型配置           │ │ ┌───────────────────────────────────────────┐ │ │
│ │   ● OpenAI             │ │ │            OpenAI 模型配置                 │ │ │
│ │   ● Azure OpenAI       │ │ │                                           │ │ │
│ │   ● 本地模型           │ │ │ 🔑 API 配置:                              │ │ │
│ │   ● 模型测试           │ │ │ • API Key: [sk-****************************] │ │ │
│ │                         │ │ │ • Base URL: [https://api.openai.com/v1/] │ │ │
│ │ 📁 Git仓库配置          │ │ │ • Organization: [可选]                   │ │ │
│ │   ● 仓库列表           │ │ │ • 连接状态: 🟢 已连接                     │ │ │
│ │   ● 认证配置           │ │ │                                           │ │ │
│ │   ● 访问权限           │ │ │ 🎯 模型设置:                              │ │ │
│ │   ● 分支策略           │ │ │ ┌─────────────────────────────────────────┐ │ │ │
│ │                         │ │ │ │ 模型名称     │ 用途        │ 状态 │ 操作 │ │ │ │
│ │ 📚 知识库管理           │ │ │ ├─────────────────────────────────────────┤ │ │ │
│ │   ● 知识库列表         │ │ │ │ gpt-4o      │ 代码分析    │ ✅  │ [测试] │ │ │ │
│ │   ● 向量数据库         │ │ │ │ gpt-4o-mini │ 代码评审    │ ✅  │ [测试] │ │ │ │
│ │   ● 索引管理           │ │ │ │ gpt-3.5     │ 聊天对话    │ ✅  │ [测试] │ │ │ │
│ │   ● 内容同步           │ │ │ │ dall-e-3    │ 图像生成    │ ❌  │ [配置] │ │ │ │
│ │                         │ │ │ └─────────────────────────────────────────┘ │ │ │
│ │ 💬 Prompt模板           │ │ │                                           │ │ │
│ │   ● 模板分类           │ │ │ ⚙️ 高级设置:                              │ │ │
│ │   ● 变量管理           │ │ │ • 请求超时: [30] 秒                       │ │ │
│ │   ● 版本控制           │ │ │ • 最大Token: [4096]                       │ │ │
│ │   ● 效果评估           │ │ │ • 温度参数: [0.7]                         │ │ │
│ │                         │ │ │ • 频率惩罚: [0.0]                         │ │ │
│ │ 🔧 系统设置             │ │ │ • 存在惩罚: [0.0]                         │ │ │
│ │   ● 基础配置           │ │ │ • 并发限制: [5]                           │ │ │
│ │   ● 性能设置           │ │ │                                           │ │ │
│ │   ● 安全策略           │ │ │ 📊 使用统计:                              │ │ │
│ │   ● 通知配置           │ │ │ • 今日调用: 1,234 次                      │ │ │
│ │                         │ │ │ • 本月消耗: $45.67                       │ │ │
│ │ 🔐 权限管理             │ │ │ • 平均响应: 1.2秒                         │ │ │
│ │   ● 角色定义           │ │ │ • 成功率: 98.5%                           │ │ │
│ │   ● 权限分配           │ │ │                                           │ │ │
│ │   ● 访问控制           │ │ │ [保存配置] [测试连接] [重置默认值]        │ │ │
│ │   ● 审计日志           │ │ └───────────────────────────────────────────┘ │ │
│ │                         │ └───────────────────────────────────────────────┘ │
│ │ ⚡ 性能监控              │                                                   │
│ │   ● 系统状态           │                                                   │
│ │   ● 资源使用           │                                                   │
│ │   ● 性能指标           │                                                   │
│ │   ● 报警设置           │                                                   │
│ └─────────────────────────┘                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 数据模型

### 配置管理接口
```typescript
interface Configuration {
  id: string
  category: ConfigCategory
  name: string
  displayName: string
  description: string
  value: any
  defaultValue: any
  type: ConfigType
  validation: ConfigValidation
  environment: Environment
  version: string
  isEncrypted: boolean
  isRequired: boolean
  isVisible: boolean
  dependencies: string[]
  lastModified: string
  modifiedBy: string
  status: ConfigStatus
}

interface AIModelConfig {
  id: string
  provider: 'openai' | 'azure_openai' | 'anthropic' | 'local' | 'custom'
  name: string
  displayName: string
  apiKey: string
  baseUrl: string
  organization?: string
  models: ModelSetting[]
  timeout: number
  maxTokens: number
  temperature: number
  frequencyPenalty: number
  presencePenalty: number
  concurrencyLimit: number
  rateLimitPerMinute: number
  status: 'active' | 'inactive' | 'testing'
  health: HealthStatus
  usage: UsageStatistics
  lastTested: string
  testResults: TestResult[]
}

interface ModelSetting {
  modelName: string
  purpose: 'chat' | 'completion' | 'embedding' | 'image' | 'analysis' | 'review'
  isDefault: boolean
  maxTokens: number
  temperature: number
  enabled: boolean
  costPerToken: number
  features: string[]
}

interface GitRepositoryConfig {
  id: string
  name: string
  url: string
  provider: 'github' | 'gitlab' | 'bitbucket' | 'gitee' | 'custom'
  authType: 'token' | 'ssh' | 'oauth' | 'username_password'
  credentials: GitCredentials
  defaultBranch: string
  allowedBranches: string[]
  webhookUrl?: string
  webhookSecret?: string
  accessLevel: 'read' | 'write' | 'admin'
  isActive: boolean
  lastSync: string
  syncStatus: 'success' | 'failed' | 'syncing'
  repositories: RepositoryInfo[]
}

interface GitCredentials {
  token?: string
  username?: string
  password?: string
  sshKey?: string
  sshKeyPassphrase?: string
  oauthToken?: string
}

interface KnowledgeBaseConfig {
  id: string
  name: string
  description: string
  type: 'vector' | 'graph' | 'hybrid'
  vectorDatabase: VectorDbConfig
  indexConfig: IndexConfig
  syncSources: SyncSource[]
  contentTypes: string[]
  embeddingModel: string
  chunkSize: number
  chunkOverlap: number
  isActive: boolean
  lastIndexed: string
  documentCount: number
  vectorCount: number
  storageUsed: number
}

interface VectorDbConfig {
  provider: 'pinecone' | 'weaviate' | 'qdrant' | 'milvus' | 'local'
  endpoint: string
  apiKey?: string
  index: string
  dimension: number
  metric: 'cosine' | 'euclidean' | 'dotproduct'
  namespace?: string
}

interface PromptTemplate {
  id: string
  name: string
  category: string
  description: string
  content: string
  variables: PromptVariable[]
  version: string
  isActive: boolean
  usage: TemplateUsage
  effectiveness: TemplateEffectiveness
  author: string
  createdAt: string
  updatedAt: string
  tags: string[]
}

interface PromptVariable {
  name: string
  type: 'string' | 'number' | 'boolean' | 'array' | 'object'
  description: string
  defaultValue?: any
  required: boolean
  validation?: string
  examples: any[]
}

interface SystemConfig {
  database: DatabaseConfig
  cache: CacheConfig
  security: SecurityConfig
  notification: NotificationConfig
  performance: PerformanceConfig
  logging: LoggingConfig
  backup: BackupConfig
}

interface PermissionConfig {
  roles: Role[]
  permissions: Permission[]
  policies: AccessPolicy[]
  auditConfig: AuditConfig
}

type ConfigCategory = 'ai_model' | 'git' | 'knowledge_base' | 'prompt' | 'system' | 'permission' | 'performance'
type ConfigType = 'string' | 'number' | 'boolean' | 'array' | 'object' | 'password' | 'url' | 'email' | 'json'
type ConfigStatus = 'active' | 'inactive' | 'pending' | 'error'
type Environment = 'development' | 'testing' | 'staging' | 'production'
```

### 状态管理
```typescript
interface ConfigurationState {
  // 配置数据
  configurations: Record<ConfigCategory, Configuration[]>
  currentCategory: ConfigCategory
  currentConfig: Configuration | null
  
  // AI模型配置
  aiModels: AIModelConfig[]
  currentAiModel: AIModelConfig | null
  modelTestResults: Record<string, TestResult>
  
  // Git仓库配置
  gitRepositories: GitRepositoryConfig[]
  currentGitRepo: GitRepositoryConfig | null
  
  // 知识库配置
  knowledgeBases: KnowledgeBaseConfig[]
  currentKnowledgeBase: KnowledgeBaseConfig | null
  
  // Prompt模板
  promptTemplates: PromptTemplate[]
  currentPromptTemplate: PromptTemplate | null
  promptCategories: string[]
  
  // 系统配置
  systemConfig: SystemConfig
  performanceMetrics: PerformanceMetrics
  healthStatus: HealthStatus
  
  // 权限配置
  permissionConfig: PermissionConfig
  
  // 环境和版本
  currentEnvironment: Environment
  configVersions: ConfigVersion[]
  
  // UI状态
  loading: boolean
  saving: boolean
  testing: boolean
  error: string | null
  
  // 搜索和筛选
  searchTerm: string
  filters: {
    category: ConfigCategory[]
    status: ConfigStatus[]
    environment: Environment[]
    modified: [string, string] | null
  }
  
  // 对话框状态
  dialogs: {
    createConfig: boolean
    editConfig: boolean
    testConnection: boolean
    importConfig: boolean
    exportConfig: boolean
    configHistory: boolean
    backupManager: boolean
    permissionEditor: boolean
  }
}

interface ConfigurationActions {
  // 配置管理
  loadConfigurations(category?: ConfigCategory): Promise<void>
  createConfiguration(config: CreateConfigRequest): Promise<void>
  updateConfiguration(id: string, updates: Partial<Configuration>): Promise<void>
  deleteConfiguration(id: string): Promise<void>
  resetConfiguration(id: string): Promise<void>
  
  // AI模型配置
  loadAIModels(): Promise<void>
  createAIModel(model: CreateAIModelRequest): Promise<void>
  updateAIModel(id: string, updates: Partial<AIModelConfig>): Promise<void>
  deleteAIModel(id: string): Promise<void>
  testAIModel(id: string): Promise<TestResult>
  testAllAIModels(): Promise<TestResult[]>
  
  // Git仓库配置
  loadGitRepositories(): Promise<void>
  createGitRepository(repo: CreateGitRepoRequest): Promise<void>
  updateGitRepository(id: string, updates: Partial<GitRepositoryConfig>): Promise<void>
  deleteGitRepository(id: string): Promise<void>
  testGitConnection(id: string): Promise<TestResult>
  syncGitRepository(id: string): Promise<void>
  
  // 知识库配置
  loadKnowledgeBases(): Promise<void>
  createKnowledgeBase(kb: CreateKnowledgeBaseRequest): Promise<void>
  updateKnowledgeBase(id: string, updates: Partial<KnowledgeBaseConfig>): Promise<void>
  deleteKnowledgeBase(id: string): Promise<void>
  rebuildIndex(id: string): Promise<void>
  
  // Prompt模板管理
  loadPromptTemplates(): Promise<void>
  createPromptTemplate(template: CreatePromptTemplateRequest): Promise<void>
  updatePromptTemplate(id: string, updates: Partial<PromptTemplate>): Promise<void>
  deletePromptTemplate(id: string): Promise<void>
  testPromptTemplate(id: string, variables: Record<string, any>): Promise<string>
  
  // 系统配置
  loadSystemConfig(): Promise<void>
  updateSystemConfig(updates: Partial<SystemConfig>): Promise<void>
  loadPerformanceMetrics(): Promise<void>
  loadHealthStatus(): Promise<void>
  
  // 权限配置
  loadPermissionConfig(): Promise<void>
  updatePermissionConfig(updates: Partial<PermissionConfig>): Promise<void>
  
  // 配置版本管理
  loadConfigVersions(): Promise<void>
  createConfigSnapshot(name: string, description?: string): Promise<void>
  restoreConfigVersion(versionId: string): Promise<void>
  compareConfigVersions(version1: string, version2: string): Promise<ConfigDiff>
  
  // 导入导出
  exportConfiguration(options: ExportOptions): Promise<void>
  importConfiguration(file: File): Promise<void>
  
  // 备份管理
  createBackup(name: string): Promise<void>
  restoreBackup(backupId: string): Promise<void>
  
  // UI操作
  setCurrentCategory(category: ConfigCategory): void
  setCurrentConfig(config: Configuration | null): void
  updateFilters(filters: Partial<ConfigurationState['filters']>): void
  toggleDialog(dialog: keyof ConfigurationState['dialogs']): void
}
```

## 页面交互逻辑

### AI模型配置管理
```typescript
// 创建AI模型配置
async function createAIModel() {
  const modelData = {
    provider: aiModelForm.provider,
    name: aiModelForm.name,
    displayName: aiModelForm.displayName,
    apiKey: aiModelForm.apiKey,
    baseUrl: aiModelForm.baseUrl,
    organization: aiModelForm.organization,
    models: aiModelForm.models,
    timeout: aiModelForm.timeout,
    maxTokens: aiModelForm.maxTokens,
    temperature: aiModelForm.temperature,
    concurrencyLimit: aiModelForm.concurrencyLimit
  }
  
  await configStore.createAIModel(modelData)
  showSuccessMessage('AI模型配置创建成功')
  dialogs.createConfig = false
  await loadAIModels()
}

// 测试AI模型连接
async function testAIModel(model: AIModelConfig) {
  testing.value = true
  
  try {
    const testResult = await configStore.testAIModel(model.id)
    
    if (testResult.success) {
      showSuccessMessage(`模型 ${model.name} 连接测试成功`)
      ElMessage.success({
        message: `响应时间: ${testResult.responseTime}ms`,
        duration: 3000
      })
    } else {
      showErrorMessage(`模型 ${model.name} 连接测试失败: ${testResult.error}`)
    }
    
    // 更新测试结果
    modelTestResults.value[model.id] = testResult
    
  } catch (error) {
    showErrorMessage(`测试连接时发生错误: ${error.message}`)
  } finally {
    testing.value = false
  }
}

// 批量测试所有模型
async function testAllAIModels() {
  const results = await configStore.testAllAIModels()
  
  const successCount = results.filter(r => r.success).length
  const totalCount = results.length
  
  if (successCount === totalCount) {
    showSuccessMessage(`所有 ${totalCount} 个模型测试通过`)
  } else {
    showWarningMessage(`${successCount}/${totalCount} 个模型测试通过`)
  }
  
  // 显示详细测试报告
  showTestReportModal(results)
}

// 智能模型推荐
function getModelRecommendations(purpose: string): ModelRecommendation[] {
  const recommendations = []
  
  switch (purpose) {
    case 'code_analysis':
      recommendations.push({
        model: 'gpt-4o',
        reason: '最强代码理解能力，适合复杂代码分析',
        confidence: 0.95
      })
      break
    case 'chat':
      recommendations.push({
        model: 'gpt-4o-mini',
        reason: '成本效益最佳，响应速度快',
        confidence: 0.9
      })
      break
    case 'code_review':
      recommendations.push({
        model: 'gpt-4o',
        reason: '能够识别复杂的代码问题和安全漏洞',
        confidence: 0.93
      })
      break
  }
  
  return recommendations
}
```

### Git仓库配置管理
```typescript
// 添加Git仓库
async function addGitRepository() {
  const repoData = {
    name: gitRepoForm.name,
    url: gitRepoForm.url,
    provider: gitRepoForm.provider,
    authType: gitRepoForm.authType,
    credentials: {
      token: gitRepoForm.token,
      username: gitRepoForm.username,
      password: gitRepoForm.password,
      sshKey: gitRepoForm.sshKey
    },
    defaultBranch: gitRepoForm.defaultBranch,
    allowedBranches: gitRepoForm.allowedBranches,
    accessLevel: gitRepoForm.accessLevel
  }
  
  await configStore.createGitRepository(repoData)
  showSuccessMessage('Git仓库配置添加成功')
  dialogs.createConfig = false
  await loadGitRepositories()
}

// 测试Git连接
async function testGitConnection(repo: GitRepositoryConfig) {
  testing.value = true
  
  try {
    const testResult = await configStore.testGitConnection(repo.id)
    
    if (testResult.success) {
      showSuccessMessage(`仓库 ${repo.name} 连接测试成功`)
      
      // 显示仓库信息
      ElMessage.info({
        message: `分支: ${testResult.branches?.length || 0} 个`,
        duration: 2000
      })
    } else {
      showErrorMessage(`仓库 ${repo.name} 连接测试失败: ${testResult.error}`)
    }
    
  } catch (error) {
    showErrorMessage(`测试连接时发生错误: ${error.message}`)
  } finally {
    testing.value = false
  }
}

// 同步Git仓库
async function syncGitRepository(repo: GitRepositoryConfig) {
  await configStore.syncGitRepository(repo.id)
  
  showSuccessMessage(`仓库 ${repo.name} 同步开始`)
  
  // 实时监控同步状态
  const syncStatusCheck = setInterval(async () => {
    await loadGitRepositories()
    
    const updatedRepo = gitRepositories.value.find(r => r.id === repo.id)
    if (updatedRepo?.syncStatus !== 'syncing') {
      clearInterval(syncStatusCheck)
      
      if (updatedRepo?.syncStatus === 'success') {
        showSuccessMessage(`仓库 ${repo.name} 同步完成`)
      } else {
        showErrorMessage(`仓库 ${repo.name} 同步失败`)
      }
    }
  }, 3000)
}

// 自动检测Git提供商
function detectGitProvider(url: string): string {
  if (url.includes('github.com')) return 'github'
  if (url.includes('gitlab.com')) return 'gitlab'
  if (url.includes('bitbucket.org')) return 'bitbucket'
  if (url.includes('gitee.com')) return 'gitee'
  return 'custom'
}

// 验证Git URL格式
function validateGitUrl(url: string): ValidationResult {
  const patterns = {
    https: /^https:\/\/[\w\.-]+\/[\w\.-]+\/[\w\.-]+\.git$/,
    ssh: /^git@[\w\.-]+:[\w\.-]+\/[\w\.-]+\.git$/
  }
  
  if (patterns.https.test(url) || patterns.ssh.test(url)) {
    return { valid: true }
  }
  
  return {
    valid: false,
    error: 'Git URL格式不正确'
  }
}
```

### 知识库配置管理
```typescript
// 创建知识库
async function createKnowledgeBase() {
  const kbData = {
    name: knowledgeBaseForm.name,
    description: knowledgeBaseForm.description,
    type: knowledgeBaseForm.type,
    vectorDatabase: {
      provider: knowledgeBaseForm.vectorProvider,
      endpoint: knowledgeBaseForm.vectorEndpoint,
      apiKey: knowledgeBaseForm.vectorApiKey,
      index: knowledgeBaseForm.vectorIndex,
      dimension: knowledgeBaseForm.dimension,
      metric: knowledgeBaseForm.metric
    },
    embeddingModel: knowledgeBaseForm.embeddingModel,
    chunkSize: knowledgeBaseForm.chunkSize,
    chunkOverlap: knowledgeBaseForm.chunkOverlap,
    syncSources: knowledgeBaseForm.syncSources
  }
  
  await configStore.createKnowledgeBase(kbData)
  showSuccessMessage('知识库配置创建成功')
  dialogs.createConfig = false
  await loadKnowledgeBases()
}

// 重建知识库索引
async function rebuildKnowledgeBaseIndex(kb: KnowledgeBaseConfig) {
  const confirmed = await showConfirmDialog({
    title: '确认重建索引',
    message: `确定要重建知识库 "${kb.name}" 的索引吗？这可能需要较长时间。`,
    type: 'warning'
  })
  
  if (!confirmed) return
  
  await configStore.rebuildIndex(kb.id)
  
  showSuccessMessage(`知识库 ${kb.name} 索引重建已开始`)
  
  // 监控重建进度
  const progressCheck = setInterval(async () => {
    await loadKnowledgeBases()
    
    const updatedKb = knowledgeBases.value.find(k => k.id === kb.id)
    if (updatedKb?.lastIndexed && updatedKb.lastIndexed !== kb.lastIndexed) {
      clearInterval(progressCheck)
      showSuccessMessage(`知识库 ${kb.name} 索引重建完成`)
    }
  }, 5000)
}

// 智能推荐向量维度
function recommendVectorDimension(embeddingModel: string): number {
  const dimensionMap = {
    'text-embedding-ada-002': 1536,
    'text-embedding-3-small': 1536,
    'text-embedding-3-large': 3072,
    'sentence-transformers': 768,
    'all-MiniLM-L6-v2': 384
  }
  
  return dimensionMap[embeddingModel] || 1536
}

// 估算存储需求
function estimateStorageRequirements(
  documentCount: number,
  averageDocSize: number,
  vectorDimension: number
): StorageEstimate {
  const textStorage = documentCount * averageDocSize
  const vectorStorage = documentCount * vectorDimension * 4 // 4 bytes per float
  const metadataStorage = documentCount * 0.5 * 1024 // 估算500B元数据
  
  const totalStorage = textStorage + vectorStorage + metadataStorage
  
  return {
    textStorage: formatBytes(textStorage),
    vectorStorage: formatBytes(vectorStorage),
    metadataStorage: formatBytes(metadataStorage),
    totalStorage: formatBytes(totalStorage),
    recommendation: totalStorage > 1024 * 1024 * 1024 ? 
      '建议使用云端向量数据库' : '可以使用本地存储'
  }
}
```

### Prompt模板管理
```typescript
// 创建Prompt模板
async function createPromptTemplate() {
  const templateData = {
    name: promptTemplateForm.name,
    category: promptTemplateForm.category,
    description: promptTemplateForm.description,
    content: promptTemplateForm.content,
    variables: promptTemplateForm.variables,
    tags: promptTemplateForm.tags
  }
  
  await configStore.createPromptTemplate(templateData)
  showSuccessMessage('Prompt模板创建成功')
  dialogs.createConfig = false
  await loadPromptTemplates()
}

// 测试Prompt模板
async function testPromptTemplate(template: PromptTemplate) {
  const testVariables = {}
  
  // 收集测试变量值
  for (const variable of template.variables) {
    if (variable.required || variable.defaultValue === undefined) {
      testVariables[variable.name] = await promptForVariable(variable)
    } else {
      testVariables[variable.name] = variable.defaultValue
    }
  }
  
  testing.value = true
  
  try {
    const result = await configStore.testPromptTemplate(template.id, testVariables)
    
    showPromptTestResultModal({
      template,
      variables: testVariables,
      result,
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    showErrorMessage(`Prompt测试失败: ${error.message}`)
  } finally {
    testing.value = false
  }
}

// 智能变量检测
function detectPromptVariables(content: string): PromptVariable[] {
  const variablePattern = /\{\{(\w+)\}\}/g
  const variables: PromptVariable[] = []
  let match
  
  while ((match = variablePattern.exec(content)) !== null) {
    const variableName = match[1]
    
    if (!variables.find(v => v.name === variableName)) {
      variables.push({
        name: variableName,
        type: inferVariableType(variableName),
        description: generateVariableDescription(variableName),
        required: true,
        examples: generateVariableExamples(variableName)
      })
    }
  }
  
  return variables
}

// 推断变量类型
function inferVariableType(variableName: string): string {
  const typePatterns = {
    number: /count|num|size|length|id$/i,
    boolean: /is|has|can|should|enable|disable$/i,
    array: /list|items|tags|options$/i
  }
  
  for (const [type, pattern] of Object.entries(typePatterns)) {
    if (pattern.test(variableName)) {
      return type
    }
  }
  
  return 'string'
}

// Prompt效果评估
function evaluatePromptEffectiveness(template: PromptTemplate): TemplateEffectiveness {
  const usage = template.usage
  
  return {
    usageCount: usage.totalUsage,
    successRate: usage.successfulRuns / usage.totalUsage,
    averageResponseTime: usage.averageResponseTime,
    userSatisfaction: usage.averageRating,
    commonIssues: usage.commonErrors.slice(0, 3),
    recommendations: generatePromptRecommendations(template)
  }
}
```

### 系统配置管理
```typescript
// 更新系统配置
async function updateSystemConfig() {
  const configData = {
    database: {
      ...systemConfigForm.database,
      connectionPool: {
        minConnections: systemConfigForm.dbMinConnections,
        maxConnections: systemConfigForm.dbMaxConnections,
        connectionTimeout: systemConfigForm.dbConnectionTimeout
      }
    },
    cache: {
      provider: systemConfigForm.cacheProvider,
      ttl: systemConfigForm.cacheTtl,
      maxSize: systemConfigForm.cacheMaxSize
    },
    security: {
      ...systemConfigForm.security,
      sessionTimeout: systemConfigForm.sessionTimeout,
      passwordPolicy: systemConfigForm.passwordPolicy
    },
    performance: {
      ...systemConfigForm.performance,
      maxConcurrentRequests: systemConfigForm.maxConcurrentRequests,
      requestTimeout: systemConfigForm.requestTimeout
    }
  }
  
  await configStore.updateSystemConfig(configData)
  showSuccessMessage('系统配置更新成功')
  
  // 检查是否需要重启服务
  if (requiresRestart(configData)) {
    showRestartWarning()
  }
}

// 性能监控
async function loadPerformanceMetrics() {
  const metrics = await configStore.loadPerformanceMetrics()
  
  performanceMetrics.value = {
    ...metrics,
    alerts: generatePerformanceAlerts(metrics)
  }
}

// 生成性能告警
function generatePerformanceAlerts(metrics: PerformanceMetrics): Alert[] {
  const alerts: Alert[] = []
  
  if (metrics.cpuUsage > 80) {
    alerts.push({
      type: 'warning',
      message: 'CPU使用率过高',
      recommendation: '考虑增加服务器资源或优化代码'
    })
  }
  
  if (metrics.memoryUsage > 85) {
    alerts.push({
      type: 'critical',
      message: '内存使用率过高',
      recommendation: '立即检查内存泄漏或增加内存'
    })
  }
  
  if (metrics.responseTime > 3000) {
    alerts.push({
      type: 'warning',
      message: '响应时间过长',
      recommendation: '检查数据库查询和网络延迟'
    })
  }
  
  return alerts
}

// 健康检查
async function performHealthCheck(): Promise<HealthStatus> {
  const checks = [
    checkDatabaseConnection(),
    checkCacheConnection(),
    checkAIModelStatus(),
    checkGitRepositoryStatus(),
    checkKnowledgeBaseStatus()
  ]
  
  const results = await Promise.allSettled(checks)
  
  const healthStatus = {
    overall: 'healthy' as HealthLevel,
    components: results.map((result, index) => ({
      name: getComponentName(index),
      status: result.status === 'fulfilled' ? 'healthy' : 'unhealthy',
      message: result.status === 'fulfilled' ? result.value : result.reason
    }))
  }
  
  // 判断整体健康状态
  const unhealthyCount = healthStatus.components.filter(c => c.status === 'unhealthy').length
  if (unhealthyCount === 0) {
    healthStatus.overall = 'healthy'
  } else if (unhealthyCount <= 2) {
    healthStatus.overall = 'degraded'
  } else {
    healthStatus.overall = 'unhealthy'
  }
  
  return healthStatus
}
```

### 配置版本管理
```typescript
// 创建配置快照
async function createConfigSnapshot() {
  const snapshotData = {
    name: snapshotForm.name,
    description: snapshotForm.description,
    environment: currentEnvironment.value,
    includeSecrets: snapshotForm.includeSecrets
  }
  
  await configStore.createConfigSnapshot(snapshotData.name, snapshotData.description)
  showSuccessMessage('配置快照创建成功')
  dialogs.backupManager = false
  await loadConfigVersions()
}

// 恢复配置版本
async function restoreConfigVersion(version: ConfigVersion) {
  const confirmed = await showConfirmDialog({
    title: '确认恢复配置',
    message: `确定要恢复到版本 "${version.name}" 吗？当前配置将被覆盖。`,
    type: 'warning'
  })
  
  if (!confirmed) return
  
  await configStore.restoreConfigVersion(version.id)
  showSuccessMessage(`配置已恢复到版本 ${version.name}`)
  
  // 重新加载所有配置
  await Promise.all([
    loadConfigurations(),
    loadAIModels(),
    loadGitRepositories(),
    loadKnowledgeBases(),
    loadPromptTemplates()
  ])
}

// 比较配置版本
async function compareConfigVersions(version1: ConfigVersion, version2: ConfigVersion) {
  const diff = await configStore.compareConfigVersions(version1.id, version2.id)
  
  showConfigDiffModal({
    version1,
    version2,
    differences: diff.differences,
    summary: diff.summary
  })
}

// 自动备份策略
function setupAutoBackup() {
  const backupInterval = systemConfig.value.backup.autoBackupInterval
  
  if (backupInterval > 0) {
    setInterval(async () => {
      try {
        const timestamp = formatDate(new Date(), 'yyyy-MM-dd_HH-mm-ss')
        await configStore.createConfigSnapshot(
          `auto_backup_${timestamp}`,
          '自动备份'
        )
        
        console.log('自动备份完成:', timestamp)
      } catch (error) {
        console.error('自动备份失败:', error)
      }
    }, backupInterval * 60 * 1000) // 转换为毫秒
  }
}
```

## 响应式设计适配

### 桌面端布局 (≥1200px)
- 左侧配置分类菜单，右侧详情区域
- 多标签页支持
- 展开的配置项详情
- 完整的统计和监控面板

### 平板端布局 (768px-1199px)
- 可折叠的侧边栏
- 卡片式配置项展示
- 简化的配置表单
- 基础的性能监控

### 移动端布局 (<768px)
- 全屏单栏布局
- 底部导航栏
- 分步式配置流程
- 精简的配置选项

```typescript
// 响应式适配
const isMobile = computed(() => screenWidth.value < 768)
const isTablet = computed(() => screenWidth.value >= 768 && screenWidth.value < 1200)
const isDesktop = computed(() => screenWidth.value >= 1200)

const configFormLayout = computed(() => ({
  labelPosition: isMobile.value ? 'top' : 'right',
  labelWidth: isMobile.value ? 'auto' : '120px',
  size: isMobile.value ? 'large' : 'default'
}))

const sidebarCollapsed = computed(() => isMobile.value || isTablet.value)
```

## 性能优化

### 配置缓存
```typescript
// 配置缓存管理
const configCache = new Map<string, any>()

function getCachedConfig(key: string): any {
  return configCache.get(key)
}

function setCachedConfig(key: string, value: any): void {
  configCache.set(key, value)
  
  // 设置过期时间
  setTimeout(() => {
    configCache.delete(key)
  }, 5 * 60 * 1000) // 5分钟
}

// 智能预加载
async function preloadRelatedConfigs(category: ConfigCategory) {
  const relatedCategories = getRelatedCategories(category)
  
  for (const relatedCategory of relatedCategories) {
    if (!getCachedConfig(relatedCategory)) {
      loadConfigurations(relatedCategory)
    }
  }
}
```

### 配置验证优化
```typescript
// 异步配置验证
const validateConfig = debounce(async (config: Configuration) => {
  try {
    const result = await configService.validateConfiguration(config)
    updateValidationResult(config.id, result)
  } catch (error) {
    updateValidationResult(config.id, { valid: false, error: error.message })
  }
}, 1000)

// 批量配置测试
async function batchTestConfigurations(configs: Configuration[]) {
  const testPromises = configs.map(config => 
    configService.testConfiguration(config).catch(error => ({
      configId: config.id,
      success: false,
      error: error.message
    }))
  )
  
  const results = await Promise.allSettled(testPromises)
  return results.map((result, index) => ({
    configId: configs[index].id,
    result: result.status === 'fulfilled' ? result.value : result.reason
  }))
}
```

## 安全考虑

### 敏感配置保护
```typescript
// 配置加密
function encryptSensitiveConfig(value: string): string {
  // 使用AES加密敏感配置
  return CryptoJS.AES.encrypt(value, getEncryptionKey()).toString()
}

function decryptSensitiveConfig(encryptedValue: string): string {
  const bytes = CryptoJS.AES.decrypt(encryptedValue, getEncryptionKey())
  return bytes.toString(CryptoJS.enc.Utf8)
}

// 配置脱敏显示
function maskSensitiveValue(value: string, type: ConfigType): string {
  switch (type) {
    case 'password':
    case 'api_key':
      return value.substring(0, 4) + '*'.repeat(value.length - 8) + value.substring(value.length - 4)
    case 'url':
      if (value.includes('@')) {
        return value.replace(/\/\/[^@]+@/, '//***@')
      }
      return value
    default:
      return value
  }
}

// 配置访问审计
async function auditConfigAccess(
  configId: string,
  action: 'view' | 'edit' | 'delete' | 'test',
  userId: string
) {
  await auditService.log({
    resourceType: 'configuration',
    resourceId: configId,
    action,
    userId,
    timestamp: new Date().toISOString(),
    ipAddress: getClientIpAddress()
  })
}
```

### 权限验证
```typescript
// 配置权限检查
function canAccessConfig(config: Configuration, user: User): boolean {
  // 检查基础权限
  if (!user.permissions.includes('config:read')) {
    return false
  }
  
  // 检查环境权限
  if (!user.environments.includes(config.environment)) {
    return false
  }
  
  // 检查敏感配置权限
  if (config.isEncrypted && !user.permissions.includes('config:view_sensitive')) {
    return false
  }
  
  return true
}

function canModifyConfig(config: Configuration, user: User): boolean {
  return canAccessConfig(config, user) && 
         user.permissions.includes('config:write') &&
         (config.environment !== 'production' || 
          user.permissions.includes('config:write_production'))
}
``` 