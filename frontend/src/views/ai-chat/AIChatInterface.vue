<template>
  <div class="ai-chat-container">
    <div class="page-header">
      <h1 class="page-title">AI助手</h1>
      <p class="page-description">与AI大模型进行智能对话，支持需求分析、代码评审等任务</p>
    </div>

    <div class="chat-layout">
      <!-- 左侧对话列表 -->
      <div class="chat-sidebar">
        <div class="sidebar-header">
          <el-button type="primary" @click="createNewConversation" class="new-chat-btn">
            <el-icon><Plus /></el-icon>
            新建对话
          </el-button>
        </div>
        
        <div class="conversation-list">
          <div
            v-for="conversation in conversations"
            :key="conversation.id"
            :class="['conversation-item', { active: currentConversationId === conversation.id }]"
            @click="selectConversation(conversation.id)"
          >
            <div class="conversation-title">{{ conversation.title }}</div>
            <div class="conversation-time">{{ formatTime(conversation.lastMessageAt) }}</div>
          </div>
        </div>
      </div>

      <!-- 右侧对话区域 -->
      <div class="chat-main">
        <div v-if="currentConversation" class="chat-content">
          <!-- 对话配置栏 -->
          <div class="chat-config">
            <div class="config-item">
              <label>模型选择：</label>
              <el-select v-model="currentModelId" @change="onModelChange" style="width: 200px">
                <el-option
                  v-for="model in availableModels"
                  :key="model.id"
                  :label="model.name"
                  :value="model.id"
                />
              </el-select>
            </div>
            
            <div class="config-item">
              <label>标签筛选：</label>
              <el-select
                v-model="selectedTags"
                placeholder="选择标签"
                multiple
                clearable
                style="width: 200px"
                @change="onTagsChange"
              >
                <el-option
                  v-for="tag in availableTags"
                  :key="tag"
                  :label="tag"
                  :value="tag"
                />
              </el-select>
            </div>
            
            <div class="config-item">
              <label>Prompt：</label>
              <el-select
                v-model="selectedPromptId"
                placeholder="选择Prompt"
                clearable
                style="width: 250px"
                @change="onPromptChange"
              >
                <el-option
                  v-for="prompt in filteredPrompts"
                  :key="prompt.id"
                  :label="prompt.name"
                  :value="prompt.id"
                >
                  <div class="prompt-option">
                    <span class="prompt-name">{{ prompt.name }}</span>
                    <div class="prompt-tags">
                      <el-tag
                        v-for="tag in prompt.tags"
                        :key="tag"
                        size="small"
                        class="prompt-tag"
                      >
                        {{ tag }}
                      </el-tag>
                    </div>
                  </div>
                </el-option>
              </el-select>
            </div>
          </div>

          <!-- 消息列表 -->
          <div class="message-list" ref="messageListRef">
            <div
              v-for="message in currentConversation.messages"
              :key="message.id"
              :class="['message-item', message.role]"
            >
              <div class="message-avatar">
                <el-avatar v-if="message.role === 'user'" :size="32">
                  {{ userInfo?.username?.charAt(0).toUpperCase() }}
                </el-avatar>
                <div v-else class="ai-avatar">
                  <el-icon><ChatDotRound /></el-icon>
                </div>
              </div>
              
              <div class="message-content">
                <div class="message-header">
                  <span class="message-role">
                    {{ message.role === 'user' ? '我' : 'AI助手' }}
                  </span>
                  <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                  <span v-if="message.tokens" class="message-tokens">{{ message.tokens }} tokens</span>
                </div>
                
                <div class="message-text">
                  <MarkdownEditor
                    v-if="message.role === 'assistant'"
                    :model-value="message.content"
                    :preview="true"
                    :readonly="true"
                    height="auto"
                  />
                  <div v-else class="user-message">{{ message.content }}</div>
                </div>
                
                <div v-if="message.promptTemplate" class="message-meta">
                  <el-tag size="small" type="info">使用模板: {{ message.promptTemplate }}</el-tag>
                </div>
              </div>
            </div>
            
            <!-- 加载状态 -->
            <div v-if="isGenerating" class="message-item assistant generating">
              <div class="message-avatar">
                <div class="ai-avatar">
                  <el-icon><ChatDotRound /></el-icon>
                </div>
              </div>
              <div class="message-content">
                <div class="generating-indicator">
                  <el-icon class="rotating"><Loading /></el-icon>
                  AI正在思考中...
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <div class="input-toolbar">
              <el-button-group>
                <el-button @click="insertVariable('{{code_diff}}')" size="small">
                  <el-icon><Document /></el-icon>
                  代码Diff
                </el-button>
                <el-button @click="insertVariable('{{requirement}}')" size="small">
                  <el-icon><Document /></el-icon>
                  需求文档
                </el-button>
                <el-button @click="insertVariable('{{context}}')" size="small">
                  <el-icon><Collection /></el-icon>
                  上下文
                </el-button>
              </el-button-group>
              
              <div class="toolbar-right">
                <el-button @click="clearConversation" size="small" type="danger" text>
                  <el-icon><Delete /></el-icon>
                  清空对话
                </el-button>
              </div>
            </div>
            
            <div class="input-container">
              <el-input
                v-model="inputMessage"
                type="textarea"
                :rows="4"
                placeholder="输入您的问题或需求..."
                @keydown.ctrl.enter="sendMessage"
                @keydown.meta.enter="sendMessage"
              />
              
              <div class="input-actions">
                <div class="input-tips">
                  <span>Ctrl + Enter 发送</span>
                  <span v-if="selectedPrompt">使用模板: {{ selectedPrompt.name }}</span>
                </div>
                <el-button
                  type="primary"
                  @click="sendMessage"
                  :loading="isGenerating"
                  :disabled="!inputMessage.trim() || !currentModelId"
                >
                  发送
                </el-button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="选择或创建一个对话开始聊天" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Loading,
  Document,
  Collection,
  Delete,
  User,
  ChatDotRound
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'
import MarkdownEditor from '@/components/common/MarkdownEditor.vue'
import type { AIConversation, AIMessage, AIModelConfig, PromptTemplate } from '@/types'
import { formatDate } from '@/utils/formatter'
import { aiModelApi, promptApi } from '@/api/ai'

const userStore = useUserStore()
const { userInfo } = storeToRefs(userStore)

// 引用
const messageListRef = ref<HTMLElement>()

// 状态
const isGenerating = ref(false)
const inputMessage = ref('')
const currentConversationId = ref('')
const currentModelId = ref('')
const selectedPromptId = ref('')
const selectedTags = ref<string[]>([])

// 数据
const conversations = ref<AIConversation[]>([])
const availableModels = ref<AIModelConfig[]>([])
const availablePrompts = ref<PromptTemplate[]>([])
const availableTags = ref<string[]>([])
const filteredPrompts = ref<PromptTemplate[]>([])

// 当前对话
const currentConversation = computed(() => {
  return conversations.value.find(c => c.id === currentConversationId.value)
})

// 当前选择的Prompt
const selectedPrompt = computed(() => {
  return availablePrompts.value.find(p => p.id === selectedPromptId.value)
})

// 根据选择的标签过滤Prompt
const updateFilteredPrompts = () => {
  if (selectedTags.value.length === 0) {
    filteredPrompts.value = availablePrompts.value
  } else {
    filteredPrompts.value = availablePrompts.value.filter(prompt => {
      return selectedTags.value.some(tag => prompt.tags.includes(tag))
    })
  }
}

// 格式化时间
const formatTime = (timestamp: string) => {
  return formatDate(timestamp, 'MM-DD HH:mm')
}

// 创建新对话
const createNewConversation = () => {
  const newConversation: AIConversation = {
    id: Date.now().toString(),
    title: '新对话',
    messages: [],
    modelConfigId: currentModelId.value || availableModels.value[0]?.id || '',
    totalTokens: 0,
    lastMessageAt: new Date().toISOString(),

  }
  
  conversations.value.unshift(newConversation)
  currentConversationId.value = newConversation.id
}

// 选择对话
const selectConversation = (conversationId: string) => {
  currentConversationId.value = conversationId
  const conversation = conversations.value.find(c => c.id === conversationId)
  if (conversation) {
    currentModelId.value = conversation.modelConfigId
  }
}

// 模型变化
const onModelChange = (modelId: string) => {
  if (currentConversation.value) {
    currentConversation.value.modelConfigId = modelId
  }
}

// 标签变化
const onTagsChange = () => {
  updateFilteredPrompts()
  // 如果当前选择的Prompt不在过滤结果中，清空选择
  if (selectedPromptId.value && !filteredPrompts.value.find(p => p.id === selectedPromptId.value)) {
    selectedPromptId.value = ''
  }
}

// Prompt变化
const onPromptChange = (promptId: string) => {
  if (promptId && selectedPrompt.value) {
    // 将Prompt内容插入到输入框
    if (inputMessage.value) {
      inputMessage.value = selectedPrompt.value.content + '\n\n' + inputMessage.value
    } else {
      inputMessage.value = selectedPrompt.value.content
    }
  }
}

// 插入变量
const insertVariable = (variable: string) => {
  const textarea = document.querySelector('.input-container textarea') as HTMLTextAreaElement
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const text = inputMessage.value
    inputMessage.value = text.substring(0, start) + variable + text.substring(end)
    
    nextTick(() => {
      textarea.focus()
      textarea.setSelectionRange(start + variable.length, start + variable.length)
    })
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || !currentModelId.value || isGenerating.value) {
    return
  }
  
  if (!currentConversation.value) {
    createNewConversation()
  }
  
  const userMessage: AIMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage.value.trim(),
    timestamp: new Date().toISOString(),
    modelConfig: currentModelId.value,
    promptTemplate: selectedPrompt.value?.name
  }
  
  currentConversation.value!.messages.push(userMessage)
  
  // 更新对话标题
  if (currentConversation.value!.messages.length === 1) {
    currentConversation.value!.title = inputMessage.value.slice(0, 20) + '...'
  }
  
  const messageContent = inputMessage.value
  inputMessage.value = ''
  selectedPromptId.value = ''
  
  // 滚动到底部
  nextTick(() => {
    scrollToBottom()
  })
  
  try {
    isGenerating.value = true
    
    // TODO: 调用AI API生成回复
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const aiMessage: AIMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: generateMockResponse(messageContent),
      timestamp: new Date().toISOString(),
      modelConfig: currentModelId.value,
      tokens: Math.floor(Math.random() * 500) + 100
    }
    
    currentConversation.value!.messages.push(aiMessage)
    currentConversation.value!.lastMessageAt = new Date().toISOString()
    currentConversation.value!.totalTokens += (aiMessage.tokens || 0)
    
    nextTick(() => {
      scrollToBottom()
    })
  } catch (error) {
    console.error('Send message failed:', error)
    ElMessage.error('发送消息失败')
  } finally {
    isGenerating.value = false
  }
}

// 生成模拟回复
const generateMockResponse = (userMessage: string) => {
  if (userMessage.includes('需求') || userMessage.includes('requirement')) {
    return `# 需求分析结果

## 功能需求
基于您提供的需求，我分析出以下关键功能点：

1. **用户管理功能**
   - 用户注册和登录
   - 个人信息管理
   - 权限控制

2. **数据处理功能**
   - 数据录入和验证
   - 数据查询和展示
   - 数据导出功能

## 非功能需求
- **性能要求**：响应时间 < 2秒
- **安全要求**：数据加密传输
- **可用性要求**：7x24小时服务

## 建议优化
1. 增加数据缓存机制
2. 实现分页查询
3. 添加操作日志记录`
  } else if (userMessage.includes('代码') || userMessage.includes('code')) {
    return `# 代码评审报告

## 总体评价
代码结构清晰，逻辑合理，但存在一些可以改进的地方。

## 发现的问题

### 🔴 严重问题
- **安全漏洞**：SQL注入风险
- **性能问题**：N+1查询问题

### 🟡 一般问题
- **代码规范**：变量命名不规范
- **注释缺失**：关键逻辑缺少注释

## 修改建议

\`\`\`javascript
// 修改前
const users = await db.query('SELECT * FROM users WHERE id = ' + userId);

// 修改后
const users = await db.query('SELECT * FROM users WHERE id = ?', [userId]);
\`\`\`

## 评分
- **代码质量**：7/10
- **安全性**：6/10
- **可维护性**：8/10`
  } else {
    return `我理解您的问题。基于您的描述，我建议：

1. **分析现状**：首先明确当前的具体情况和面临的挑战
2. **制定方案**：根据分析结果制定可行的解决方案
3. **实施计划**：制定详细的实施步骤和时间安排
4. **监控评估**：建立监控机制，及时评估效果

如果您能提供更多具体信息，我可以给出更精准的建议。`
  }
}

// 清空对话
const clearConversation = async () => {
  if (!currentConversation.value) return
  
  try {
    await ElMessageBox.confirm('确定要清空当前对话吗？', '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    currentConversation.value.messages = []
    currentConversation.value.totalTokens = 0
  } catch {
    // 用户取消
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// 加载数据
const loadData = async () => {
  try {
    // 加载可用模型
    const modelsResponse = await aiModelApi.getModelConfigs()
    availableModels.value = modelsResponse
    // 设置默认模型
    if (availableModels.value.length > 0) {
      currentModelId.value = availableModels.value.find(m => m.isDefault)?.id || availableModels.value[0].id
    }
    
    // 加载Prompt模板
    const promptsResponse = await promptApi.getPromptTemplates()
    availablePrompts.value = promptsResponse
    updateFilteredPrompts()
    
    // 加载所有标签
    const tagsResponse = await promptApi.getPromptTags()
    availableTags.value = tagsResponse
  } catch (error) {
    console.error('Load data failed:', error)
    ElMessage.error('加载数据失败')
  }
}

// 处理快捷键事件
const handleKeyboardEvents = () => {
  // 监听发送消息事件
  const handleSendMessage = () => {
    if (inputMessage.value.trim() && currentModelId.value && !isGenerating.value) {
      sendMessage()
    }
  }

  // 监听新建对话事件
  const handleNewConversation = () => {
    createNewConversation()
  }

  // 监听清空对话事件
  const handleClearConversation = () => {
    clearConversation()
  }

  document.addEventListener('ai-send-message', handleSendMessage)
  document.addEventListener('ai-new-conversation', handleNewConversation)
  document.addEventListener('ai-clear-conversation', handleClearConversation)

  return () => {
    document.removeEventListener('ai-send-message', handleSendMessage)
    document.removeEventListener('ai-new-conversation', handleNewConversation)
    document.removeEventListener('ai-clear-conversation', handleClearConversation)
  }
}

// 保存cleanup函数的引用
let keyboardCleanup: (() => void) | null = null

onMounted(() => {
  loadData()
  keyboardCleanup = handleKeyboardEvents()
})

onUnmounted(() => {
  if (keyboardCleanup) {
    keyboardCleanup()
  }
})
</script>

<style scoped lang="scss">
.ai-chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  
  .page-header {
    padding: 20px;
    border-bottom: 1px solid #e8e8e8;
    background: #fff;
  }
}

.chat-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chat-sidebar {
  width: 280px;
  border-right: 1px solid #e8e8e8;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  
  .sidebar-header {
    padding: 16px;
    border-bottom: 1px solid #e8e8e8;
    
    .new-chat-btn {
      width: 100%;
    }
  }
  
  .conversation-list {
    flex: 1;
    overflow-y: auto;
    
    .conversation-item {
      padding: 12px 16px;
      border-bottom: 1px solid #e8e8e8;
      cursor: pointer;
      transition: background-color 0.3s;
      
      &:hover {
        background: #e9ecef;
      }
      
      &.active {
        background: #409eff;
        color: #fff;
      }
      
      .conversation-title {
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .conversation-time {
        font-size: 12px;
        opacity: 0.7;
      }
    }
  }
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-config {
  padding: 16px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  gap: 20px;
  align-items: center;
  background: #f8f9fa;
  
  .config-item {
    display: flex;
    align-items: center;
    gap: 8px;
    
    label {
      font-size: 14px;
      color: #666;
      white-space: nowrap;
    }
  }
}

.prompt-option {
  .prompt-name {
    display: block;
    margin-bottom: 4px;
  }
  
  .prompt-tags {
    display: flex;
    gap: 4px;
    
    .prompt-tag {
      font-size: 10px;
    }
  }
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  
  .message-item {
    display: flex;
    margin-bottom: 20px;
    
    &.user {
      flex-direction: row-reverse;
      
      .message-content {
        margin-right: 12px;
        margin-left: 60px;
        
        .message-text {
          background: #409eff;
          color: #fff;
          
          .user-message {
            padding: 12px 16px;
            border-radius: 12px;
            line-height: 1.5;
          }
        }
      }
    }
    
    &.assistant {
      .message-content {
        margin-left: 12px;
        margin-right: 60px;
        
        .message-text {
          background: #f5f5f5;
          border-radius: 12px;
          overflow: hidden;
        }
      }
    }
    
    &.generating {
      .generating-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: #f5f5f5;
        border-radius: 12px;
        color: #666;
        
        .rotating {
          animation: rotate 1s linear infinite;
        }
      }
    }
  }
  
  .message-avatar {
    flex-shrink: 0;
    
    .ai-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #409eff;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
    }
  }
  
  .message-content {
    flex: 1;
    
    .message-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
      font-size: 12px;
      color: #666;
      
      .message-role {
        font-weight: 500;
      }
      
      .message-tokens {
        background: #e8e8e8;
        padding: 2px 6px;
        border-radius: 10px;
      }
    }
    
    .message-meta {
      margin-top: 8px;
    }
  }
}

.input-area {
  border-top: 1px solid #e8e8e8;
  background: #fff;
  
  .input-toolbar {
    padding: 12px 20px;
    border-bottom: 1px solid #e8e8e8;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .input-container {
    padding: 20px;
    
    .input-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 12px;
      
      .input-tips {
        font-size: 12px;
        color: #666;
        
        span {
          margin-right: 16px;
        }
      }
    }
  }
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
