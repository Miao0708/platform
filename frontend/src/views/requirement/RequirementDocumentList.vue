<template>
  <div class="requirement-document-container">
    <div class="page-header">
      <h1 class="page-title">需求文档管理</h1>
      <p class="page-description">管理需求文档，支持文件上传和手动输入，可进行AI分析和优化</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="action-left">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建需求
        </el-button>
      </div>
      
      <div class="action-right">
        <el-select
          v-model="statusFilter"
          placeholder="筛选状态"
          clearable
          style="width: 150px; margin-right: 12px"
          @change="loadDocuments"
        >
          <el-option
            v-for="option in statusOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        
        <el-button @click="loadDocuments">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="document-list">
      <el-table
        v-loading="loading"
        :data="documents"
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="name" label="需求名称" min-width="200">
          <template #default="{ row }">
            <div class="document-name">
              <el-icon v-if="row.file_type" class="file-icon">
                <Document />
              </el-icon>
              <span class="name-text" @click="viewOriginalDocument(row)">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="source" label="来源" width="100">
          <template #default="{ row }">
            <el-tag :type="row.source === 'upload' ? 'primary' : 'info'" size="small">
              {{ row.source === 'upload' ? '文件上传' : '手动输入' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="original_filename" label="原始文件" width="180">
          <template #default="{ row }">
            <span v-if="row.original_filename" class="filename">
              {{ row.original_filename }}
            </span>
            <span v-else class="no-file">-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="AI配置" width="200">
          <template #default="{ row }">
            <div class="ai-config">
              <div v-if="row.prompt_template_id" class="config-item">
                <el-icon><ChatDotRound /></el-icon>
                <span>Prompt: {{ getPromptName(row.prompt_template_id) }}</span>
              </div>
              <div v-if="row.model_config_id" class="config-item">
                <el-icon><Cpu /></el-icon>
                <span>模型: {{ getModelName(row.model_config_id) }}</span>
              </div>
              <div v-if="!row.prompt_template_id && !row.model_config_id" class="no-config">
                未配置
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <div class="operation-buttons">
              <!-- 查看原始需求 -->
              <el-button size="small" @click="viewOriginalDocument(row)">
                <el-icon><View /></el-icon>
                查看原始
              </el-button>
              
              <!-- 查看优化需求 -->
              <el-button 
                v-if="row.optimized_content" 
                size="small" 
                type="success"
                @click="viewOptimizedDocument(row)"
              >
                <el-icon><View /></el-icon>
                查看优化
              </el-button>
              
              <!-- 开始处理 -->
              <el-button 
                v-if="row.status === 'pending'" 
                size="small" 
                type="primary" 
                @click="startProcessing(row)"
                :loading="row.processing"
              >
                <el-icon><MagicStick /></el-icon>
                开始处理
              </el-button>
              
              <!-- 跳过处理 -->
              <el-button 
                v-if="row.status === 'pending'" 
                size="small" 
                type="warning"
                @click="showSkipDialog(row)"
              >
                跳过
              </el-button>
              
              <!-- 编辑 -->
              <el-button 
                v-if="row.status === 'pending' || row.status === 'completed'"
                size="small" 
                @click="editDocument(row)"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              
              <!-- 删除 -->
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteDocument(row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadDocuments"
          @size-change="loadDocuments"
        />
      </div>
    </div>

    <!-- 新建需求对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建需求文档"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="120px"
      >
        <el-form-item label="需求名称" prop="name">
          <el-input 
            v-model="createForm.name" 
            placeholder="请输入需求名称" 
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="输入方式">
          <el-radio-group v-model="createForm.source" @change="onSourceChange">
            <el-radio value="manual">
              <el-icon><Edit /></el-icon>
              手动输入
            </el-radio>
            <el-radio value="upload">
              <el-icon><Upload /></el-icon>
              文件上传
            </el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 手动输入 -->
        <el-form-item 
          v-if="createForm.source === 'manual'" 
          label="需求内容" 
          prop="original_content"
        >
          <el-input
            v-model="createForm.original_content"
            type="textarea"
            :rows="8"
            placeholder="请输入需求内容..."
            maxlength="10000"
            show-word-limit
          />
        </el-form-item>
        
        <!-- 文件上传 -->
        <el-form-item 
          v-if="createForm.source === 'upload'" 
          label="上传文件" 
          prop="file"
        >
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            :auto-upload="false"
            :limit="1"
            :accept="acceptedFileTypes"
            :before-upload="beforeUpload"
            :on-change="onFileChange"
            :on-remove="onFileRemove"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 {{ supportedFileTypes.join(', ') }} 格式，文件大小不超过 {{ maxFileSize }}MB
              </div>
            </template>
          </el-upload>
          
          <!-- 文件预览 -->
          <div v-if="uploadedFile" class="file-preview">
            <div class="file-info">
              <el-icon><Document /></el-icon>
              <span class="file-name">{{ uploadedFile.name }}</span>
              <span class="file-size">({{ formatFileSize(uploadedFile.size) }})</span>
            </div>
            <div v-if="fileContent" class="file-content-preview">
              <el-text type="info">文件内容预览：</el-text>
              <div class="content-preview">
                {{ fileContent.substring(0, 500) }}
                <span v-if="fileContent.length > 500">...</span>
              </div>
            </div>
          </div>
        </el-form-item>
        
        <el-divider />
        
        <el-form-item label="Prompt模板">
          <el-select
            v-model="createForm.prompt_template_id"
            placeholder="选择Prompt模板（可选）"
            clearable
            style="width: 100%"
            @focus="loadRequirementPrompts"
          >
            <el-option
              v-for="prompt in requirementPrompts"
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
        </el-form-item>
        
        <el-form-item label="AI模型">
          <el-select
            v-model="createForm.model_config_id"
            placeholder="选择AI模型（可选）"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="model in models"
              :key="model.id"
              :label="model.name"
              :value="model.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="cancelCreate">取消</el-button>
        <el-button type="primary" @click="createDocument" :loading="createLoading">
          创建需求
        </el-button>
      </template>
    </el-dialog>

    <!-- 跳过优化对话框 -->
    <el-dialog
      v-model="showOptimizeDialogVisible"
      title="需求优化"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="optimizeFormRef"
        :model="optimizeForm"
        :rules="optimizeRules"
        label-width="100px"
      >
        <el-form-item label="Prompt模板" prop="prompt_template_id">
          <el-select
            v-model="optimizeForm.prompt_template_id"
            placeholder="选择优化Prompt模板"
            style="width: 100%"
            @focus="loadOptimizePrompts"
          >
            <el-option
              v-for="prompt in optimizePrompts"
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
        </el-form-item>
        
        <el-form-item label="AI模型" prop="model_config_id">
          <el-select
            v-model="optimizeForm.model_config_id"
            placeholder="选择AI模型"
            style="width: 100%"
          >
            <el-option
              v-for="model in models"
              :key="model.id"
              :label="model.name"
              :value="model.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showOptimizeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="startOptimize" :loading="optimizeLoading">
          开始优化
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox, ElForm } from 'element-plus'
import {
  Plus,
  Upload,
  Refresh,
  Document,
  View,
  Edit,
  Delete,
  MagicStick,
  ChatDotRound,
  Cpu,
  UploadFilled
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { formatDate } from '@/utils/formatter'
import {
  getRequirementDocuments,
  createRequirementDocument,
  uploadRequirementFile,
  deleteRequirementDocument,
  skipToOptimizeRequirement,
  getSupportedFileTypes
} from '@/api/requirement'
import { aiModelApi, promptApi } from '@/api/ai'
import type {
  RequirementDocument,
  CreateRequirementDocumentRequest,
  RequirementStatus
} from '@/types/requirement'
import type { AIModelConfig, PromptTemplate } from '@/types'
import {
  REQUIREMENT_STATUS_OPTIONS,
  STATUS_COLOR_MAP
} from '@/types/requirement'

const router = useRouter()

// 状态数据
const loading = ref(false)
const createLoading = ref(false)
const optimizeLoading = ref(false)
const documents = ref<RequirementDocument[]>([])
const selectedRows = ref<RequirementDocument[]>([])
const statusFilter = ref<RequirementStatus>()
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 弹窗状态
const showCreateDialog = ref(false)
const showOptimizeDialogVisible = ref(false)
const currentOptimizeDoc = ref<RequirementDocument>()

// 配置数据
const models = ref<AIModelConfig[]>([])
const prompts = ref<PromptTemplate[]>([])
const requirementPrompts = ref<PromptTemplate[]>([])
const supportedFileTypes = ref<string[]>([])
const maxFileSize = ref(0)

// 文件上传相关
const uploadRef = ref()
const uploadedFile = ref<File>()
const fileContent = ref('')

// 表单引用
const createFormRef = ref<InstanceType<typeof ElForm>>()
const optimizeFormRef = ref<InstanceType<typeof ElForm>>()

// 新建表单
const createForm = reactive<CreateRequirementDocumentRequest>({
  name: '',
  original_content: '',
  source: 'manual',
  prompt_template_id: undefined,
  model_config_id: undefined
})

// 优化表单
const optimizeForm = reactive({
  prompt_template_id: undefined as number | undefined,
  model_config_id: undefined as number | undefined
})

// 表单验证规则
const createRules = computed(() => {
  const rules: any = {
    name: [{ required: true, message: '请输入需求名称', trigger: 'blur' }]
  }
  
  // 只有手动输入时才验证内容
  if (createForm.source === 'manual') {
    rules.original_content = [{ required: true, message: '请输入需求内容', trigger: 'blur' }]
  }
  
  // 只有文件上传时才验证文件
  if (createForm.source === 'upload') {
    rules.file = [{ 
      validator: (rule: any, value: any, callback: any) => {
        if (!uploadedFile.value) {
          callback(new Error('请选择要上传的文件'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }]
  }
  
  return rules
})

const optimizeRules = {
  prompt_template_id: [{ required: true, message: '请选择Prompt模板', trigger: 'change' }],
  model_config_id: [{ required: true, message: '请选择AI模型', trigger: 'change' }]
}

// 计算属性
const statusOptions = computed(() => REQUIREMENT_STATUS_OPTIONS)

const optimizePrompts = computed(() => {
  return prompts.value.filter(p => 
    p.tags.includes('优化') || 
    p.tags.includes('需求优化') ||
    p.name.includes('优化')
  )
})

const acceptedFileTypes = computed(() => {
  return supportedFileTypes.value.map(type => `.${type}`).join(',')
})

const uploadAction = computed(() => '/api/requirement-management/documents/upload')

const uploadHeaders = computed(() => ({
  // 这里可以添加认证头等
}))

const uploadData = computed(() => ({
  // 上传时的额外数据
}))

// 方法
const getStatusLabel = (status: RequirementStatus) => {
  const option = statusOptions.value.find(opt => opt.value === status)
  return option?.label || status
}

const getStatusColor = (status: RequirementStatus) => {
  return STATUS_COLOR_MAP[status] || 'info'
}

const getPromptName = (id: number) => {
  const prompt = prompts.value.find(p => Number(p.id) === id)
  return prompt?.name || `Prompt ${id}`
}

const getModelName = (id: number) => {
  const model = models.value.find(m => String(m.id) === String(id))
  return model?.name || `Model ${id}`
}

const loadDocuments = async () => {
  try {
    loading.value = true
    const params = {
      status: statusFilter.value,
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    const response = await getRequirementDocuments(params)
    documents.value = response
    // 这里需要后端返回总数，暂时用当前数据长度
    total.value = response.length
  } catch (error) {
    console.error('加载需求文档失败:', error)
    ElMessage.error('加载需求文档失败')
  } finally {
    loading.value = false
  }
}

const loadConfigurations = async () => {
  try {
    // 加载AI模型配置
    const modelsResponse = await aiModelApi.getModelConfigs()
    models.value = modelsResponse
    
    // 加载支持的文件类型
    const fileTypesResponse = await getSupportedFileTypes()
    supportedFileTypes.value = fileTypesResponse.supported_types
    maxFileSize.value = fileTypesResponse.max_file_size_mb
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

// 动态加载需求相关的Prompt模板
const loadRequirementPrompts = async () => {
  if (requirementPrompts.value.length > 0) return // 已加载过，避免重复请求
  
  try {
    console.log('Loading requirement prompts...')
    const response = await promptApi.getPromptTemplates({ 
      tags: '需求解析,需求优化,需求分析' 
    })
    requirementPrompts.value = response
    console.log('Loaded requirement prompts:', response)
  } catch (error) {
    console.error('加载需求Prompt失败:', error)
    ElMessage.error('加载需求Prompt失败')
  }
}

// 动态加载优化相关的Prompt模板
const loadOptimizePrompts = async () => {
  if (prompts.value.length > 0) return // 已加载过，避免重复请求
  
  try {
    console.log('Loading optimize prompts...')
    const response = await promptApi.getPromptTemplates({ 
      tags: '优化,需求优化' 
    })
    prompts.value = response
    console.log('Loaded optimize prompts:', response)
  } catch (error) {
    console.error('加载优化Prompt失败:', error)
    ElMessage.error('加载优化Prompt失败')
  }
}

const createDocument = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    createLoading.value = true
    
    if (createForm.source === 'upload' && uploadedFile.value) {
      // 文件上传方式
      const formData = new FormData()
      formData.append('file', uploadedFile.value)
      formData.append('name', createForm.name)
      
      if (createForm.prompt_template_id) {
        formData.append('prompt_template_id', createForm.prompt_template_id.toString())
      }
      if (createForm.model_config_id) {
        formData.append('model_config_id', createForm.model_config_id.toString())
      }
      
      await uploadRequirementFile(formData)
    } else {
      // 手动输入方式
      await createRequirementDocument(createForm)
    }
    
    ElMessage.success('需求文档创建成功')
    showCreateDialog.value = false
    resetCreateForm()
    loadDocuments()
  } catch (error) {
    console.error('创建需求文档失败:', error)
    ElMessage.error('创建需求文档失败')
  } finally {
    createLoading.value = false
  }
}

const resetCreateForm = () => {
  Object.assign(createForm, {
    name: '',
    original_content: '',
    source: 'manual',
    prompt_template_id: undefined,
    model_config_id: undefined
  })
  // 清理文件上传相关
  uploadedFile.value = undefined
  fileContent.value = ''
  uploadRef.value?.clearFiles()
  createFormRef.value?.clearValidate()
}

// 取消创建
const cancelCreate = () => {
  showCreateDialog.value = false
  resetCreateForm()
}

// 输入方式变化
const onSourceChange = () => {
  // 清空相关字段
  if (createForm.source === 'manual') {
    uploadedFile.value = undefined
    fileContent.value = ''
    uploadRef.value?.clearFiles()
  } else {
    createForm.original_content = ''
  }
  createFormRef.value?.clearValidate()
}

// 文件上传前验证
const beforeUpload = (file: File) => {
  const isValidType = supportedFileTypes.value.some(type => 
    file.name.toLowerCase().endsWith(`.${type.toLowerCase()}`)
  )
  
  if (!isValidType) {
    ElMessage.error(`不支持的文件类型，请上传 ${supportedFileTypes.value.join(', ')} 格式的文件`)
    return false
  }
  
  const isValidSize = file.size / 1024 / 1024 < maxFileSize.value
  if (!isValidSize) {
    ElMessage.error(`文件大小不能超过 ${maxFileSize.value}MB`)
    return false
  }
  
  return true
}

// 文件选择变化
const onFileChange = (file: any) => {
  if (file.raw) {
    uploadedFile.value = file.raw
    readFileContent(file.raw)
  }
}

// 文件移除
const onFileRemove = () => {
  uploadedFile.value = undefined
  fileContent.value = ''
}

// 读取文件内容
const readFileContent = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target?.result as string
    fileContent.value = content
    
    // 如果没有输入需求名称，使用文件名（去掉扩展名）
    if (!createForm.name) {
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '')
      createForm.name = nameWithoutExt
    }
    
    // 设置文件内容为需求内容
    createForm.original_content = content
  }
  reader.readAsText(file)
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const showOptimizeDialog = (doc: RequirementDocument) => {
  currentOptimizeDoc.value = doc
  showOptimizeDialogVisible.value = true
  
  // 如果已有配置，预填充表单
  if (doc.prompt_template_id) {
    optimizeForm.prompt_template_id = doc.prompt_template_id
  }
  if (doc.model_config_id) {
    optimizeForm.model_config_id = doc.model_config_id
  }
}

const startOptimize = async () => {
  if (!optimizeFormRef.value || !currentOptimizeDoc.value) return
  
  try {
    await optimizeFormRef.value.validate()
    optimizeLoading.value = true
    
    await skipToOptimizeRequirement(
      currentOptimizeDoc.value.id,
      optimizeForm.prompt_template_id!,
      optimizeForm.model_config_id!
    )
    
    ElMessage.success('优化任务已启动')
    showOptimizeDialogVisible.value = false
    loadDocuments()
  } catch (error) {
    console.error('启动优化失败:', error)
    ElMessage.error('启动优化失败')
  } finally {
    optimizeLoading.value = false
  }
}

// 查看原始需求文档
const viewOriginalDocument = (doc: RequirementDocument) => {
  // 这里可以显示一个对话框来查看原始内容
  ElMessageBox.alert(doc.original_content, `查看原始需求 - ${doc.name}`, {
    customClass: 'content-dialog',
    showClose: true,
    showConfirmButton: false
  })
}

// 查看优化后的需求文档
const viewOptimizedDocument = (doc: RequirementDocument) => {
  if (doc.optimized_content) {
    ElMessageBox.alert(doc.optimized_content, `查看优化需求 - ${doc.name}`, {
      customClass: 'content-dialog',
      showClose: true,
      showConfirmButton: false
    })
  }
}

// 开始处理需求
const startProcessing = async (doc: RequirementDocument) => {
  if (!doc.prompt_template_id || !doc.model_config_id) {
    // 如果没有配置AI模型和Prompt，显示配置对话框
    showOptimizeDialog(doc)
    return
  }
  
  try {
    // 设置processing状态
    doc.processing = true
    
    // 调用API开始处理
    await skipToOptimizeRequirement(
      doc.id,
      doc.prompt_template_id,
      doc.model_config_id
    )
    
    ElMessage.success('处理任务已启动，正在后台执行...')
    
    // 开始轮询状态
    startPolling(doc.id)
    
  } catch (error) {
    console.error('启动处理失败:', error)
    ElMessage.error('启动处理失败')
    doc.processing = false
  }
}

// 跳过处理，直接设置优化内容
const showSkipDialog = (doc: RequirementDocument) => {
  ElMessageBox.prompt('请输入优化后的需求内容', `跳过处理 - ${doc.name}`, {
    inputType: 'textarea',
    inputPlaceholder: '请输入优化后的需求内容...',
    inputValidator: (value) => {
      if (!value || value.trim().length === 0) {
        return '请输入优化内容'
      }
      return true
    }
  }).then(({ value }) => {
    skipProcessing(doc.id, value)
  }).catch(() => {
    // 用户取消
  })
}

// 跳过处理的实际操作
const skipProcessing = async (docId: number, optimizedContent: string) => {
  try {
    // 这里需要调用API直接设置优化内容
    // await setOptimizedContent(docId, optimizedContent)
    
    ElMessage.success('已设置优化内容')
    loadDocuments()
  } catch (error) {
    console.error('设置优化内容失败:', error)
    ElMessage.error('设置优化内容失败')
  }
}

// 轮询状态更新
const pollingIntervals = ref<Map<number, number>>(new Map())

const startPolling = (docId: number) => {
  // 如果已经在轮询，先清除
  if (pollingIntervals.value.has(docId)) {
    clearInterval(pollingIntervals.value.get(docId))
  }
  
  const intervalId = setInterval(async () => {
    try {
      // 这里需要调用API获取文档状态
      // const status = await getDocumentStatus(docId)
      // 暂时模拟状态更新
      const doc = documents.value.find(d => d.id === docId)
      if (doc && doc.status === 'processing') {
        // 模拟处理完成
        setTimeout(() => {
          doc.status = 'completed'
          doc.processing = false
          clearInterval(intervalId)
          pollingIntervals.value.delete(docId)
          ElMessage.success(`需求文档 "${doc.name}" 处理完成`)
        }, 5000) // 5秒后模拟完成
      }
    } catch (error) {
      console.error('轮询状态失败:', error)
      clearInterval(intervalId)
      pollingIntervals.value.delete(docId)
    }
  }, 2000) // 每2秒轮询一次
  
  pollingIntervals.value.set(docId, intervalId)
}

const editDocument = (doc: RequirementDocument) => {
  // 编辑已完成的文档时，重置状态为pending
  if (doc.status === 'completed') {
    ElMessageBox.confirm(
      '编辑已完成的需求将重置状态为待处理，是否继续？',
      '确认编辑',
      { type: 'warning' }
    ).then(() => {
      // 这里需要调用API重置状态
      // resetDocumentStatus(doc.id)
      router.push(`/requirement/document/${doc.id}/edit`)
    }).catch(() => {
      // 用户取消
    })
  } else {
    router.push(`/requirement/document/${doc.id}/edit`)
  }
}

const deleteDocument = async (doc: RequirementDocument) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除需求文档 "${doc.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await deleteRequirementDocument(doc.id)
    ElMessage.success('删除成功')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const onSelectionChange = (selection: RequirementDocument[]) => {
  selectedRows.value = selection
}

const onUploadSuccess = (response: any) => {
  ElMessage.success('文件上传成功')
  loadDocuments()
}

const onUploadError = (error: any) => {
  console.error('文件上传失败:', error)
  ElMessage.error('文件上传失败')
}

// 生命周期
onMounted(() => {
  loadDocuments()
  loadConfigurations()
})

onUnmounted(() => {
  // 清理所有轮询
  pollingIntervals.value.forEach((intervalId) => {
    clearInterval(intervalId)
  })
  pollingIntervals.value.clear()
})
</script>

<style scoped lang="scss">
.requirement-document-container {
  padding: 20px;
  
  .page-header {
    margin-bottom: 20px;
  }
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .action-left {
    display: flex;
    gap: 12px;
  }
  
  .action-right {
    display: flex;
    align-items: center;
  }
}

.document-list {
  .document-name {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .file-icon {
      color: #409eff;
    }
    
    .name-text {
      cursor: pointer;
      color: #409eff;
      
      &:hover {
        text-decoration: underline;
      }
    }
  }
  
  .filename {
    font-size: 12px;
    color: #666;
  }
  
  .no-file,
  .no-config {
    color: #999;
    font-style: italic;
  }
  
  .ai-config {
    .config-item {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      color: #666;
      margin-bottom: 2px;
      
      .el-icon {
        font-size: 14px;
      }
    }
  }
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
.operation-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  
  .el-button {
    margin: 0;
    font-size: 12px;
    padding: 4px 8px;
  }
}

.content-dialog {
  max-width: 800px;
  
  .el-message-box__content {
    max-height: 500px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.6;
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
    flex-wrap: wrap;
    
    .prompt-tag {
      font-size: 10px;
    }
  }
}

.file-preview {
  margin-top: 12px;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #f8f9fa;
  
  .file-info {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    
    .file-name {
      font-weight: 500;
      color: #303133;
    }
    
    .file-size {
      color: #909399;
      font-size: 12px;
    }
  }
  
  .file-content-preview {
    .content-preview {
      margin-top: 8px;
      padding: 8px;
      background-color: #fff;
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      font-size: 12px;
      line-height: 1.4;
      color: #606266;
      max-height: 200px;
      overflow-y: auto;
    }
  }
}

.upload-demo {
  width: 100%;
}
</style> 