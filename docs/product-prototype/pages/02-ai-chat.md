# AI聊天对话页面 (AI Chat)

## 页面概述
AI聊天页面是平台的核心功能之一，提供智能对话服务，支持多种AI模型，具备上下文记忆、对话管理、文件上传等功能。

## 页面布局

### 页面结构
```
┌─────────────────────────────────────────────────────────────┐
│                      顶部导航栏                               │
├─────────────────────────────────────────────────────────────┤
│ 侧边栏 │                  主聊天区域                        │
│ ┌─────┐│ ┌─────────────────────────────────────────────────┐ │
│ │会话 ││ │                聊天标题栏                       │ │
│ │列表 ││ │ ┌─────────────┐ ┌─────────┐ ┌─────────────┐    │ │
│ │     ││ │ │新建对话     │ │模型选择 │ │设置         │    │ │
│ │会话1││ │ └─────────────┘ └─────────┘ └─────────────┘    │ │
│ │会话2││ ├─────────────────────────────────────────────────┤ │
│ │会话3││ │                                                │ │
│ │     ││ │                 消息区域                        │ │
│ │     ││ │                                                │ │
│ │     ││ │ ┌───────────────────────────────────────────┐  │ │
│ │     ││ │ │ 用户消息                              时间 │  │ │
│ │     ││ │ └───────────────────────────────────────────┘  │ │
│ │     ││ │ ┌───────────────────────────────────────────┐  │ │
│ │     ││ │ │ AI回复                                时间 │  │ │
│ │     ││ │ │ [复制] [重新生成] [点赞] [点踩]          │  │ │
│ │     ││ │ └───────────────────────────────────────────┘  │ │
│ │     ││ ├─────────────────────────────────────────────────┤ │
│ │     ││ │                 输入区域                        │ │
│ │     ││ │ ┌─────────────────────────────────────────────┐ │ │
│ │     ││ │ │             消息输入框                      │ │ │
│ │     ││ │ │ [附件] [Prompt] [发送]                     │ │ │
│ │     ││ │ └─────────────────────────────────────────────┘ │ │
│ └─────┘│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 功能组件详述

### 1. 对话列表侧边栏

#### 1.1 对话列表
```typescript
interface ConversationSidebar {
  conversations: AIConversation[]
  currentConversationId: string | null
  searchQuery: string
  loading: boolean
  
  // 操作功能
  actions: {
    createNew: () => void
    selectConversation: (id: string) => void
    deleteConversation: (id: string) => void
    renameConversation: (id: string, title: string) => void
    searchConversations: (query: string) => void
  }
}

interface ConversationListItem {
  id: string
  title: string
  lastMessage: string
  lastMessageTime: string
  messageCount: number
  isActive: boolean
  model: string
  
  // 显示状态
  isHovered: boolean
  isEditing: boolean
  
  // 快捷操作
  quickActions: {
    rename: boolean
    delete: boolean
    duplicate: boolean
  }
}
```

#### 1.2 搜索和筛选
```typescript
interface ConversationFilter {
  searchQuery: string
  timeRange: 'today' | 'week' | 'month' | 'all'
  modelFilter: string | 'all'
  sortBy: 'time' | 'title' | 'messages'
  sortOrder: 'asc' | 'desc'
}
```

### 2. 聊天标题栏

```typescript
interface ChatHeader {
  conversation: AIConversation | null
  
  // 标题信息
  title: string
  subtitle: string  // 显示模型信息、消息数量等
  
  // 操作按钮
  actions: {
    newChat: () => void
    exportChat: () => void
    clearHistory: () => void
    shareChat: () => void
    settings: () => void
  }
  
  // 模型选择
  modelSelector: {
    currentModel: string
    availableModels: AIModelConfig[]
    onModelChange: (modelId: string) => void
  }
}
```

### 3. 消息区域

#### 3.1 消息列表
```typescript
interface MessageArea {
  messages: ChatMessage[]
  loading: boolean
  streaming: boolean
  
  // 显示控制
  showTimestamps: boolean
  showModelInfo: boolean
  autoScroll: boolean
  
  // 操作功能
  messageActions: {
    copyMessage: (messageId: string) => void
    regenerateResponse: (messageId: string) => void
    editMessage: (messageId: string) => void
    deleteMessage: (messageId: string) => void
    likeMessage: (messageId: string) => void
    dislikeMessage: (messageId: string) => void
  }
}
```

#### 3.2 消息项组件
```typescript
interface MessageItem {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  
  // 扩展信息
  model?: string
  tokens?: number
  responseTime?: number
  
  // 附件信息
  attachments?: Array<{
    id: string
    type: 'image' | 'file' | 'code'
    name: string
    size?: number
    url?: string
  }>
  
  // 状态信息
  status: 'sending' | 'sent' | 'failed' | 'regenerating'
  error?: string
  
  // 交互状态
  isHovered: boolean
  isSelected: boolean
  showActions: boolean
  
  // 反馈信息
  feedback?: {
    rating: 'like' | 'dislike' | null
    comment?: string
  }
}
```

#### 3.3 流式响应显示
```typescript
interface StreamingMessage {
  id: string
  content: string
  isComplete: boolean
  
  // 流式状态
  chunks: string[]
  currentChunk: string
  
  // 显示效果
  typewriterEffect: boolean
  cursor: boolean
  
  // 停止控制
  stopGeneration: () => void
}
```

### 4. 输入区域

#### 4.1 消息输入框
```typescript
interface MessageInput {
  content: string
  placeholder: string
  maxLength: number
  rows: number
  
  // 输入状态
  isFocused: boolean
  isComposing: boolean
  
  // 功能按钮
  features: {
    attachFile: boolean
    insertPrompt: boolean
    voiceInput: boolean
    sendOnEnter: boolean
  }
  
  // 事件处理
  handlers: {
    onInput: (value: string) => void
    onKeyDown: (event: KeyboardEvent) => void
    onPaste: (event: ClipboardEvent) => void
    onFocus: () => void
    onBlur: () => void
  }
}
```

#### 4.2 文件上传
```typescript
interface FileUpload {
  supportedTypes: string[]
  maxFileSize: number
  maxFiles: number
  
  // 上传状态
  uploadQueue: Array<{
    id: string
    file: File
    progress: number
    status: 'pending' | 'uploading' | 'completed' | 'failed'
    error?: string
  }>
  
  // 预览
  previews: Array<{
    id: string
    type: 'image' | 'document' | 'code'
    thumbnail?: string
    name: string
    size: string
  }>
  
  // 操作
  actions: {
    selectFiles: () => void
    removeFile: (id: string) => void
    uploadFiles: () => Promise<void>
  }
}
```

#### 4.3 Prompt模板选择
```typescript
interface PromptSelector {
  templates: PromptTemplate[]
  categories: string[]
  
  // 筛选状态
  filter: {
    category: string
    search: string
    favorites: boolean
  }
  
  // 选择状态
  selectedTemplate: PromptTemplate | null
  variables: Record<string, string>
  
  // 操作
  actions: {
    selectTemplate: (template: PromptTemplate) => void
    setVariable: (key: string, value: string) => void
    insertTemplate: () => void
    saveAsFavorite: (templateId: string) => void
  }
}
```

## 页面状态管理

### State 定义
```typescript
interface AIChatState {
  // 对话管理
  conversations: {
    list: AIConversation[]
    current: AIConversation | null
    loading: boolean
    filter: ConversationFilter
  }
  
  // 消息管理
  messages: {
    list: ChatMessage[]
    streaming: StreamingMessage | null
    loading: boolean
    error: string | null
  }
  
  // 输入状态
  input: {
    content: string
    attachments: FileUpload['uploadQueue']
    selectedPrompt: PromptTemplate | null
    variables: Record<string, string>
  }
  
  // UI状态
  ui: {
    sidebarCollapsed: boolean
    showSettings: boolean
    showPromptSelector: boolean
    autoScroll: boolean
    messageActions: boolean
  }
  
  // 配置
  config: {
    currentModel: string
    temperature: number
    maxTokens: number
    enableContext: boolean
    systemPrompt: string
  }
}
```

### Actions 定义
```typescript
interface AIChatActions {
  // 对话管理
  loadConversations(): Promise<void>
  createConversation(title?: string): Promise<AIConversation>
  selectConversation(id: string): Promise<void>
  updateConversation(id: string, data: Partial<AIConversation>): Promise<void>
  deleteConversation(id: string): Promise<void>
  
  // 消息操作
  sendMessage(content: string, attachments?: File[]): Promise<void>
  sendStreamMessage(content: string): AsyncGenerator<string>
  regenerateMessage(messageId: string): Promise<void>
  editMessage(messageId: string, content: string): Promise<void>
  deleteMessage(messageId: string): Promise<void>
  
  // 文件处理
  uploadFiles(files: File[]): Promise<void>
  removeAttachment(id: string): void
  
  // Prompt操作
  loadPromptTemplates(): Promise<void>
  selectPromptTemplate(template: PromptTemplate): void
  insertPromptTemplate(): void
  
  // 配置管理
  updateModelConfig(config: Partial<AIChatConfig>): void
  loadModelList(): Promise<void>
  
  // 导出功能
  exportConversation(format: 'md' | 'pdf' | 'json'): Promise<void>
  shareConversation(): Promise<string>
}
```

## 交互逻辑

### 1. 页面初始化
```typescript
onMounted(async () => {
  // 1. 加载对话列表
  await loadConversations()
  
  // 2. 加载AI模型列表
  await loadModelList()
  
  // 3. 加载Prompt模板
  await loadPromptTemplates()
  
  // 4. 恢复上次的对话
  const lastConversationId = localStorage.getItem('lastConversationId')
  if (lastConversationId) {
    await selectConversation(lastConversationId)
  }
  
  // 5. 设置键盘快捷键
  setupKeyboardShortcuts()
})
```

### 2. 消息发送流程
```typescript
const sendMessage = async (content: string, attachments?: File[]) => {
  try {
    // 1. 验证输入
    if (!content.trim() && !attachments?.length) {
      ElMessage.warning('请输入消息内容')
      return
    }
    
    // 2. 添加用户消息到列表
    const userMessage = {
      id: generateId(),
      role: 'user' as const,
      content,
      timestamp: new Date().toISOString(),
      attachments: attachments?.map(f => ({
        id: generateId(),
        type: getFileType(f),
        name: f.name,
        size: f.size
      }))
    }
    
    messages.list.push(userMessage)
    
    // 3. 清空输入框
    input.content = ''
    input.attachments = []
    
    // 4. 显示AI正在思考
    const assistantMessage = {
      id: generateId(),
      role: 'assistant' as const,
      content: '',
      timestamp: new Date().toISOString(),
      status: 'generating'
    }
    
    messages.list.push(assistantMessage)
    
    // 5. 发送请求
    if (config.streamResponse) {
      await handleStreamResponse(assistantMessage.id, content)
    } else {
      await handleNormalResponse(assistantMessage.id, content)
    }
    
  } catch (error) {
    handleSendError(error)
  }
}
```

### 3. 流式响应处理
```typescript
const handleStreamResponse = async (messageId: string, content: string) => {
  try {
    const eventSource = new EventSource(`/api/ai/chat/stream`, {
      method: 'POST',
      body: JSON.stringify({
        message: content,
        conversationId: currentConversation.value?.id,
        modelId: config.currentModel
      })
    })
    
    let fullResponse = ''
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'chunk') {
        fullResponse += data.content
        updateMessageContent(messageId, fullResponse)
      } else if (data.type === 'done') {
        eventSource.close()
        updateMessageStatus(messageId, 'completed')
      } else if (data.type === 'error') {
        eventSource.close()
        updateMessageStatus(messageId, 'failed', data.error)
      }
    }
    
    eventSource.onerror = () => {
      eventSource.close()
      updateMessageStatus(messageId, 'failed', '连接中断')
    }
    
  } catch (error) {
    updateMessageStatus(messageId, 'failed', error.message)
  }
}
```

### 4. 文件上传处理
```typescript
const handleFileUpload = async (files: File[]) => {
  // 1. 验证文件
  const validFiles = files.filter(file => {
    if (file.size > maxFileSize) {
      ElMessage.error(`${file.name} 文件过大`)
      return false
    }
    
    if (!supportedTypes.includes(file.type)) {
      ElMessage.error(`${file.name} 文件类型不支持`)
      return false
    }
    
    return true
  })
  
  // 2. 添加到上传队列
  validFiles.forEach(file => {
    input.attachments.push({
      id: generateId(),
      file,
      progress: 0,
      status: 'pending'
    })
  })
  
  // 3. 执行上传
  for (const attachment of input.attachments) {
    if (attachment.status === 'pending') {
      await uploadSingleFile(attachment)
    }
  }
}

const uploadSingleFile = async (attachment: FileAttachment) => {
  try {
    attachment.status = 'uploading'
    
    const formData = new FormData()
    formData.append('file', attachment.file)
    
    const response = await axios.post('/api/files/upload', formData, {
      onUploadProgress: (progressEvent) => {
        attachment.progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
      }
    })
    
    attachment.status = 'completed'
    attachment.url = response.data.url
    
  } catch (error) {
    attachment.status = 'failed'
    attachment.error = error.message
  }
}
```

### 5. Prompt模板使用
```typescript
const usePromptTemplate = (template: PromptTemplate) => {
  // 1. 解析模板变量
  const variables = extractVariables(template.content)
  
  // 2. 如果有变量，显示变量填写对话框
  if (variables.length > 0) {
    showPromptVariableDialog(template, variables)
  } else {
    // 3. 直接插入模板内容
    insertTemplateContent(template.content)
  }
}

const showPromptVariableDialog = (template: PromptTemplate, variables: string[]) => {
  ElMessageBox.prompt(
    `请填写模板变量：${variables.join(', ')}`,
    '使用Prompt模板',
    {
      inputType: 'textarea',
      inputPlaceholder: '请输入变量值，用换行分隔'
    }
  ).then(({ value }) => {
    const variableValues = value.split('\n')
    let content = template.content
    
    variables.forEach((variable, index) => {
      const regex = new RegExp(`\\{\\{\\s*${variable}\\s*\\}\\}`, 'g')
      content = content.replace(regex, variableValues[index] || '')
    })
    
    insertTemplateContent(content)
  })
}

const insertTemplateContent = (content: string) => {
  if (input.content) {
    input.content += '\n\n' + content
  } else {
    input.content = content
  }
  
  // 聚焦到输入框
  nextTick(() => {
    inputRef.value?.focus()
  })
}
```

## 快捷键支持

### 快捷键定义
```typescript
const chatKeyboardShortcuts = [
  {
    key: 'Enter',
    ctrl: true,
    action: () => sendMessage(input.content),
    description: '发送消息'
  },
  {
    key: 'n',
    ctrl: true,
    action: () => createConversation(),
    description: '新建对话'
  },
  {
    key: 'l',
    ctrl: true,
    action: () => clearConversation(),
    description: '清空对话'
  },
  {
    key: 'k',
    ctrl: true,
    action: () => focusSearch(),
    description: '聚焦搜索'
  },
  {
    key: 'Escape',
    action: () => cancelOperation(),
    description: '取消操作'
  }
]
```

## 响应式设计

### 移动端适配
```typescript
const isMobile = computed(() => windowWidth.value < 768)

const mobileLayout = computed(() => ({
  hideSidebar: isMobile.value,
  compactHeader: isMobile.value,
  fullscreenInput: isMobile.value,
  swipeGestures: isMobile.value
}))

// 移动端手势支持
const setupMobileGestures = () => {
  if (isMobile.value) {
    // 左滑显示侧边栏
    useSwipe(chatContainer, {
      onSwipeRight: () => {
        if (!ui.sidebarCollapsed) {
          ui.sidebarCollapsed = false
        }
      },
      onSwipeLeft: () => {
        if (ui.sidebarCollapsed) {
          ui.sidebarCollapsed = true
        }
      }
    })
  }
}
```

## 性能优化

### 1. 虚拟滚动
```typescript
// 对于大量消息的对话，使用虚拟滚动
const virtualList = ref()

const virtualListConfig = {
  itemHeight: 'auto',
  buffer: 10,
  threshold: 100
}

// 消息过多时启用虚拟滚动
const useVirtualScroll = computed(() => 
  messages.list.length > virtualListConfig.threshold
)
```

### 2. 消息缓存
```typescript
// 缓存历史消息
const messageCache = new Map<string, ChatMessage[]>()

const getCachedMessages = (conversationId: string) => {
  return messageCache.get(conversationId) || []
}

const setCachedMessages = (conversationId: string, messages: ChatMessage[]) => {
  // 限制缓存大小
  if (messageCache.size > 10) {
    const firstKey = messageCache.keys().next().value
    messageCache.delete(firstKey)
  }
  
  messageCache.set(conversationId, messages)
}
```

### 3. 防抖和节流
```typescript
// 输入防抖
const debouncedInput = useDebounceFn((value: string) => {
  // 自动保存草稿
  saveDraft(currentConversation.value?.id, value)
}, 1000)

// 滚动节流
const throttledScroll = useThrottleFn(() => {
  updateScrollPosition()
}, 100)
```

## 安全考虑

### 1. 输入验证
```typescript
const validateMessage = (content: string): ValidationResult => {
  const errors: string[] = []
  
  // 长度检查
  if (content.length > maxMessageLength) {
    errors.push(`消息长度不能超过${maxMessageLength}字符`)
  }
  
  // 敏感词检查
  if (containsSensitiveWords(content)) {
    errors.push('消息包含敏感词汇')
  }
  
  // XSS防护
  if (containsHTMLTags(content)) {
    errors.push('消息不能包含HTML标签')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}
```

### 2. 文件安全
```typescript
const validateUploadFile = (file: File): boolean => {
  // 文件类型白名单
  const allowedTypes = [
    'image/jpeg',
    'image/png',
    'text/plain',
    'application/pdf'
  ]
  
  // 文件大小限制
  const maxSize = 10 * 1024 * 1024 // 10MB
  
  return allowedTypes.includes(file.type) && file.size <= maxSize
}
``` 