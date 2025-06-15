import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AIModelConfig, AIConversation, PromptTemplate } from '@/types'
import { aiModelApi, aiChatApi, promptApi } from '@/api/ai'

export const useAIStore = defineStore('ai', () => {
  // 状态
  const modelConfigs = ref<AIModelConfig[]>([])
  const conversations = ref<AIConversation[]>([])
  const promptTemplates = ref<PromptTemplate[]>([])
  const currentConversationId = ref<string>('')
  const isLoading = ref(false)

  // 计算属性
  const defaultModel = computed(() => {
    return modelConfigs.value.find(model => model.isDefault && model.isActive)
  })

  const activeModels = computed(() => {
    return modelConfigs.value.filter(model => model.isActive)
  })

  const currentConversation = computed(() => {
    return conversations.value.find(conv => conv.id === currentConversationId.value)
  })

  const promptsByCategory = computed(() => {
    const categories = {
      requirement: [] as PromptTemplate[],
      code_review: [] as PromptTemplate[],
      test_case: [] as PromptTemplate[],
      general: [] as PromptTemplate[]
    }
    
    promptTemplates.value.forEach(prompt => {
      if (categories[prompt.category]) {
        categories[prompt.category].push(prompt)
      }
    })
    
    return categories
  })

  // 模型配置相关方法
  const loadModelConfigs = async () => {
    try {
      isLoading.value = true
      const configs = await aiModelApi.getModelConfigs()
      modelConfigs.value = configs
    } catch (error) {
      console.error('Load model configs failed:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const createModelConfig = async (data: Omit<AIModelConfig, 'id' | 'createdAt' | 'updatedAt'>) => {
    try {
      const newConfig = await aiModelApi.createModelConfig(data)
      modelConfigs.value.push(newConfig)
      return newConfig
    } catch (error) {
      console.error('Create model config failed:', error)
      throw error
    }
  }

  const updateModelConfig = async (id: string, data: Partial<AIModelConfig>) => {
    try {
      const updatedConfig = await aiModelApi.updateModelConfig(id, data)
      const index = modelConfigs.value.findIndex(config => config.id === id)
      if (index !== -1) {
        modelConfigs.value[index] = updatedConfig
      }
      return updatedConfig
    } catch (error) {
      console.error('Update model config failed:', error)
      throw error
    }
  }

  const deleteModelConfig = async (id: string) => {
    try {
      await aiModelApi.deleteModelConfig(id)
      const index = modelConfigs.value.findIndex(config => config.id === id)
      if (index !== -1) {
        modelConfigs.value.splice(index, 1)
      }
    } catch (error) {
      console.error('Delete model config failed:', error)
      throw error
    }
  }

  const testModelConnection = async (id: string) => {
    try {
      const result = await aiModelApi.testModelConnection(id)
      return result
    } catch (error) {
      console.error('Test model connection failed:', error)
      throw error
    }
  }

  const setDefaultModel = async (id: string) => {
    try {
      await aiModelApi.setDefaultModel(id)
      // 更新本地状态
      modelConfigs.value.forEach(config => {
        config.isDefault = config.id === id
      })
    } catch (error) {
      console.error('Set default model failed:', error)
      throw error
    }
  }

  // 对话相关方法
  const loadConversations = async () => {
    try {
      isLoading.value = true
      const convs = await aiChatApi.getConversations()
      conversations.value = convs
    } catch (error) {
      console.error('Load conversations failed:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const createConversation = async (title: string, modelConfigId?: string) => {
    try {
      const modelId = modelConfigId || defaultModel.value?.id
      if (!modelId) {
        throw new Error('没有可用的模型配置')
      }
      
      const newConversation = await aiChatApi.createConversation({
        title,
        modelConfigId: modelId
      })
      
      conversations.value.unshift(newConversation)
      currentConversationId.value = newConversation.id
      return newConversation
    } catch (error) {
      console.error('Create conversation failed:', error)
      throw error
    }
  }

  const updateConversation = async (id: string, data: Partial<AIConversation>) => {
    try {
      const updatedConversation = await aiChatApi.updateConversation(id, data)
      const index = conversations.value.findIndex(conv => conv.id === id)
      if (index !== -1) {
        conversations.value[index] = updatedConversation
      }
      return updatedConversation
    } catch (error) {
      console.error('Update conversation failed:', error)
      throw error
    }
  }

  const deleteConversation = async (id: string) => {
    try {
      await aiChatApi.deleteConversation(id)
      const index = conversations.value.findIndex(conv => conv.id === id)
      if (index !== -1) {
        conversations.value.splice(index, 1)
      }
      if (currentConversationId.value === id) {
        currentConversationId.value = ''
      }
    } catch (error) {
      console.error('Delete conversation failed:', error)
      throw error
    }
  }

  const sendMessage = async (
    conversationId: string,
    content: string,
    modelConfigId: string,
    promptTemplateId?: string,
    context?: Record<string, any>
  ) => {
    try {
      const message = await aiChatApi.sendMessage(conversationId, {
        content,
        modelConfigId,
        promptTemplateId,
        context
      })
      
      // 更新对话中的消息
      const conversation = conversations.value.find(conv => conv.id === conversationId)
      if (conversation) {
        conversation.messages.push(message)
        conversation.lastMessageAt = message.timestamp
        if (message.tokens) {
          conversation.totalTokens += message.tokens
        }
      }
      
      return message
    } catch (error) {
      console.error('Send message failed:', error)
      throw error
    }
  }

  // Prompt模板相关方法
  const loadPromptTemplates = async (params?: {
    category?: string
    tags?: string[]
    isPublic?: boolean
  }) => {
    try {
      isLoading.value = true
      const templates = await promptApi.getPromptTemplates(params)
      promptTemplates.value = templates
    } catch (error) {
      console.error('Load prompt templates failed:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const createPromptTemplate = async (data: Omit<PromptTemplate, 'id' | 'createdAt' | 'updatedAt' | 'usageCount'>) => {
    try {
      const newTemplate = await promptApi.createPromptTemplate(data)
      promptTemplates.value.push(newTemplate)
      return newTemplate
    } catch (error) {
      console.error('Create prompt template failed:', error)
      throw error
    }
  }

  const updatePromptTemplate = async (id: string, data: Partial<PromptTemplate>) => {
    try {
      const updatedTemplate = await promptApi.updatePromptTemplate(id, data)
      const index = promptTemplates.value.findIndex(template => template.id === id)
      if (index !== -1) {
        promptTemplates.value[index] = updatedTemplate
      }
      return updatedTemplate
    } catch (error) {
      console.error('Update prompt template failed:', error)
      throw error
    }
  }

  const deletePromptTemplate = async (id: string) => {
    try {
      await promptApi.deletePromptTemplate(id)
      const index = promptTemplates.value.findIndex(template => template.id === id)
      if (index !== -1) {
        promptTemplates.value.splice(index, 1)
      }
    } catch (error) {
      console.error('Delete prompt template failed:', error)
      throw error
    }
  }

  const renderPromptTemplate = async (id: string, variables: Record<string, any>) => {
    try {
      const result = await promptApi.renderPromptTemplate(id, variables)
      return result.content
    } catch (error) {
      console.error('Render prompt template failed:', error)
      throw error
    }
  }

  // 工具方法
  const setCurrentConversation = (id: string) => {
    currentConversationId.value = id
  }

  const clearCurrentConversation = () => {
    currentConversationId.value = ''
  }

  const getModelById = (id: string) => {
    return modelConfigs.value.find(model => model.id === id)
  }

  const getPromptById = (id: string) => {
    return promptTemplates.value.find(prompt => prompt.id === id)
  }

  return {
    // 状态
    modelConfigs,
    conversations,
    promptTemplates,
    currentConversationId,
    isLoading,
    
    // 计算属性
    defaultModel,
    activeModels,
    currentConversation,
    promptsByCategory,
    
    // 模型配置方法
    loadModelConfigs,
    createModelConfig,
    updateModelConfig,
    deleteModelConfig,
    testModelConnection,
    setDefaultModel,
    
    // 对话方法
    loadConversations,
    createConversation,
    updateConversation,
    deleteConversation,
    sendMessage,
    
    // Prompt模板方法
    loadPromptTemplates,
    createPromptTemplate,
    updatePromptTemplate,
    deletePromptTemplate,
    renderPromptTemplate,
    
    // 工具方法
    setCurrentConversation,
    clearCurrentConversation,
    getModelById,
    getPromptById
  }
})
