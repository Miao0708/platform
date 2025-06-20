<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">AI大模型配置</h1>
      <p class="page-description">配置和管理AI大模型接入信息</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>模型配置列表</span>
          <el-button type="primary" @click="showAddDialog">
            添加模型配置
          </el-button>
        </div>
      </template>
      
      <!-- 模型配置表格 -->
      <el-table :data="modelConfigs" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="配置名称" />
        <el-table-column prop="provider" label="服务商" width="120">
          <template #default="scope">
            <el-tag :type="getProviderTagType(scope.row.provider)">
              {{ getProviderName(scope.row.provider) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="模型" />
        <el-table-column prop="baseUrl" label="API地址" show-overflow-tooltip />
        <el-table-column prop="isDefault" label="默认" width="80">
          <template #default="scope">
            <el-switch
              v-model="scope.row.isDefault"
              @change="setDefaultModel(scope.row)"
              :disabled="!scope.row.isActive"
            />
          </template>
        </el-table-column>
        <el-table-column prop="isActive" label="状态" width="80">
          <template #default="scope">
            <el-switch
              v-model="scope.row.isActive"
              @change="toggleModelStatus(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="testConnection(scope.row)" :loading="scope.row.testing">
              测试连接
            </el-button>
            <el-button type="text" size="small" @click="editModel(scope.row)">
              编辑
            </el-button>
            <el-button type="text" size="small" @click="deleteModel(scope.row)" style="color: #f56c6c">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑模型配置对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑模型配置' : '添加模型配置'"
      width="600px"
    >
      <el-form
        ref="modelFormRef"
        :model="modelForm"
        :rules="modelRules"
        label-width="120px"
      >
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="modelForm.name" placeholder="请输入配置名称" />
        </el-form-item>
        
        <el-form-item label="服务商" prop="provider">
          <el-select v-model="modelForm.provider" placeholder="请选择服务商" @change="onProviderChange">
            <el-option label="OpenAI" value="openai" />
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="讯飞星火" value="spark" />
            <el-option label="字节豆包" value="doubao" />
            <el-option label="Google Gemini" value="gemini" />
            <el-option label="Anthropic Claude" value="claude" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="API地址" prop="baseUrl">
          <el-input v-model="modelForm.baseUrl" placeholder="请输入API基础地址" />
          <div class="form-tip">
            <span>常用地址：</span>
            <el-button type="text" @click="setCommonUrl('openai')">OpenAI官方</el-button>
            <el-button type="text" @click="setCommonUrl('deepseek')">DeepSeek</el-button>
            <el-button type="text" @click="setCommonUrl('spark')">讯飞星火</el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="API密钥" prop="apiKey">
          <el-input
            v-model="modelForm.apiKey"
            type="password"
            placeholder="请输入API密钥"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="模型名称" prop="model">
          <el-select v-model="modelForm.model" placeholder="请选择或输入模型名称" filterable allow-create>
            <el-option
              v-for="model in getAvailableModels(modelForm.provider)"
              :key="model.value"
              :label="model.label"
              :value="model.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="最大Token数">
          <el-input-number
            v-model="modelForm.maxTokens"
            :min="1"
            :max="32000"
            placeholder="默认4096"
          />
        </el-form-item>
        
        <el-form-item label="温度参数">
          <el-slider
            v-model="modelForm.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            show-input
            :input-size="'small'"
          />
          <div class="form-tip">控制输出的随机性，0为确定性输出，2为最大随机性</div>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="modelForm.isDefault">设为默认模型</el-checkbox>
          <el-checkbox v-model="modelForm.isActive">启用此配置</el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveModel" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { AIModelConfig } from '@/types'

// 表单引用
const modelFormRef = ref<FormInstance>()

// 加载状态
const loading = ref(false)
const saving = ref(false)

// 对话框状态
const dialogVisible = ref(false)
const isEdit = ref(false)

// 模型配置列表
const modelConfigs = ref<(AIModelConfig & { testing?: boolean })[]>([])

// 模型表单
const modelForm = reactive({
  id: '',
  name: '',
  provider: 'openai' as AIModelConfig['provider'],
  baseUrl: '',
  apiKey: '',
  model: '',
  maxTokens: 4096,
  temperature: 0.7,
  isDefault: false,
  isActive: true
})

// 表单验证规则
const modelRules: FormRules = {
  name: [
    { required: true, message: '请输入配置名称', trigger: 'blur' }
  ],
  provider: [
    { required: true, message: '请选择服务商', trigger: 'change' }
  ],
  baseUrl: [
    { required: true, message: '请输入API地址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' }
  ],
  apiKey: [
    { required: true, message: '请输入API密钥', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请选择模型', trigger: 'blur' }
  ]
}

// 获取服务商标签类型
const getProviderTagType = (provider: string) => {
  const typeMap: Record<string, string> = {
    openai: 'primary',
    deepseek: 'success',
    spark: 'warning',
    doubao: 'info',
    gemini: 'danger',
    claude: ''
  }
  return typeMap[provider] || 'info'
}

// 获取服务商名称
const getProviderName = (provider: string) => {
  const nameMap: Record<string, string> = {
    openai: 'OpenAI',
    deepseek: 'DeepSeek',
    spark: '讯飞星火',
    doubao: '字节豆包',
    gemini: 'Google Gemini',
    claude: 'Anthropic Claude'
  }
  return nameMap[provider] || provider
}

// 获取可用模型列表
const getAvailableModels = (provider: string) => {
  const modelMap: Record<string, Array<{ label: string; value: string }>> = {
    openai: [
      { label: 'GPT-4o', value: 'gpt-4o' },
      { label: 'GPT-4o-mini', value: 'gpt-4o-mini' },
      { label: 'GPT-4 Turbo', value: 'gpt-4-turbo' },
      { label: 'GPT-3.5 Turbo', value: 'gpt-3.5-turbo' }
    ],
    deepseek: [
      { label: 'DeepSeek Chat', value: 'deepseek-chat' },
      { label: 'DeepSeek Coder', value: 'deepseek-coder' }
    ],
    spark: [
      { label: 'Spark Max', value: 'generalv3.5' },
      { label: 'Spark Pro', value: 'generalv3' },
      { label: 'Spark Lite', value: 'general' }
    ],
    doubao: [
      { label: 'Doubao Pro 128k', value: 'ep-20241230140952-8xvpz' },
      { label: 'Doubao Pro 32k', value: 'ep-20241230140952-8xvpz' }
    ],
    gemini: [
      { label: 'Gemini Pro', value: 'gemini-pro' },
      { label: 'Gemini Pro Vision', value: 'gemini-pro-vision' }
    ],
    claude: [
      { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20241022' },
      { label: 'Claude 3 Haiku', value: 'claude-3-haiku-20240307' }
    ]
  }
  return modelMap[provider] || []
}

// 设置常用URL
const setCommonUrl = (provider: string) => {
  const urlMap: Record<string, string> = {
    openai: 'https://api.openai.com/v1',
    deepseek: 'https://api.deepseek.com/v1',
    spark: 'https://spark-api-open.xf-yun.com/v1'
  }
  if (urlMap[provider]) {
    modelForm.baseUrl = urlMap[provider]
  }
}

// 服务商变化时的处理
const onProviderChange = (provider: string) => {
  // 清空模型选择
  modelForm.model = ''
  // 设置默认URL
  setCommonUrl(provider)
  // 设置默认参数
  if (provider === 'spark') {
    modelForm.maxTokens = 8192
  } else if (provider === 'claude') {
    modelForm.maxTokens = 8192
  }
}

// 显示添加对话框
const showAddDialog = () => {
  isEdit.value = false
  Object.assign(modelForm, {
    id: '',
    name: '',
    provider: 'openai',
    baseUrl: 'https://api.openai.com/v1',
    apiKey: '',
    model: '',
    maxTokens: 4096,
    temperature: 0.7,
    isDefault: false,
    isActive: true
  })
  dialogVisible.value = true
}

// 编辑模型
const editModel = (model: AIModelConfig) => {
  isEdit.value = true
  Object.assign(modelForm, model)
  dialogVisible.value = true
}

// 保存模型配置
const saveModel = async () => {
  if (!modelFormRef.value) return
  
  try {
    await modelFormRef.value.validate()
    saving.value = true
    
    // TODO: 调用API保存模型配置
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success(isEdit.value ? '模型配置更新成功' : '模型配置添加成功')
    dialogVisible.value = false
    loadModelConfigs()
  } catch (error) {
    console.error('Save model config failed:', error)
  } finally {
    saving.value = false
  }
}

// 测试连接
const testConnection = async (model: AIModelConfig & { testing?: boolean }) => {
  try {
    model.testing = true
    
    // TODO: 调用API测试连接
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success('连接测试成功')
  } catch (error) {
    console.error('Test connection failed:', error)
    ElMessage.error('连接测试失败')
  } finally {
    model.testing = false
  }
}

// 设置默认模型
const setDefaultModel = async (model: AIModelConfig) => {
  try {
    // TODO: 调用API设置默认模型
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 取消其他模型的默认状态
    modelConfigs.value.forEach(config => {
      if (config.id !== model.id) {
        config.isDefault = false
      }
    })
    
    ElMessage.success('默认模型设置成功')
  } catch (error) {
    console.error('Set default model failed:', error)
    model.isDefault = false
  }
}

// 切换模型状态
const toggleModelStatus = async (model: AIModelConfig) => {
  try {
    // TODO: 调用API切换状态
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 如果禁用了默认模型，需要取消默认状态
    if (!model.isActive && model.isDefault) {
      model.isDefault = false
    }
    
    ElMessage.success(model.isActive ? '模型已启用' : '模型已禁用')
  } catch (error) {
    console.error('Toggle model status failed:', error)
    model.isActive = !model.isActive
  }
}

// 删除模型
const deleteModel = async (model: AIModelConfig) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模型配置 "${model.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API删除模型
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('模型配置删除成功')
    loadModelConfigs()
  } catch {
    // 用户取消
  }
}

// 加载模型配置列表
const loadModelConfigs = async () => {
  try {
    loading.value = true
    
    // TODO: 调用API加载模型配置列表
    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    modelConfigs.value = [
      {
        id: '1',
        name: 'OpenAI GPT-4o',
        provider: 'openai',
        baseUrl: 'https://api.openai.com/v1',
        apiKey: 'sk-***',
        model: 'gpt-4o',
        maxTokens: 4096,
        temperature: 0.7,
        isDefault: true,
        isActive: true,
        createdAt: '2024-01-15 10:30:00',
        updatedAt: '2024-01-15 10:30:00'
      },
      {
        id: '2',
        name: 'DeepSeek Chat',
        provider: 'deepseek',
        baseUrl: 'https://api.deepseek.com/v1',
        apiKey: 'sk-***',
        model: 'deepseek-chat',
        maxTokens: 4096,
        temperature: 0.7,
        isDefault: false,
        isActive: true,
        createdAt: '2024-01-15 10:30:00',
        updatedAt: '2024-01-15 10:30:00'
      }
    ]
  } catch (error) {
    console.error('Load model configs failed:', error)
    ElMessage.error('加载模型配置失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadModelConfigs()
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  
  .el-button {
    padding: 0;
    margin-left: 8px;
    font-size: 12px;
  }
}
</style>
