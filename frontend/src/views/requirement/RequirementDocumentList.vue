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
        
        <el-upload
          ref="uploadRef"
          :action="uploadAction"
          :headers="uploadHeaders"
          :before-upload="beforeUpload"
          :on-success="onUploadSuccess"
          :on-error="onUploadError"
          :show-file-list="false"
          :data="uploadData"
        >
          <el-button type="success">
            <el-icon><Upload /></el-icon>
            上传文件
          </el-button>
        </el-upload>
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
              <span class="name-text" @click="viewDocument(row)">{{ row.name }}</span>
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
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="viewDocument(row)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
              
              <el-button 
                v-if="row.status === 'pending'" 
                size="small" 
                type="primary" 
                @click="showOptimizeDialog(row)"
              >
                <el-icon><MagicStick /></el-icon>
                优化
              </el-button>
              
              <el-button size="small" @click="editDocument(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteDocument(row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </el-button-group>
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
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="需求名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入需求名称" />
        </el-form-item>
        
        <el-form-item label="需求内容" prop="original_content">
          <el-input
            v-model="createForm.original_content"
            type="textarea"
            :rows="8"
            placeholder="请输入需求内容..."
          />
        </el-form-item>
        
        <el-form-item label="Prompt模板">
          <el-select
            v-model="createForm.prompt_template_id"
            placeholder="选择Prompt模板（可选）"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="prompt in prompts"
              :key="prompt.id"
              :label="prompt.name"
              :value="prompt.id"
            />
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
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createDocument" :loading="createLoading">
          创建
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
          >
            <el-option
              v-for="prompt in optimizePrompts"
              :key="prompt.id"
              :label="prompt.name"
              :value="prompt.id"
            />
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
import { ref, reactive, onMounted, computed } from 'vue'
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
  Cpu
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { formatDate } from '@/utils/formatter'
import {
  getRequirementDocuments,
  createRequirementDocument,
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
const supportedFileTypes = ref<string[]>([])
const maxFileSize = ref(0)

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
const createRules = {
  name: [{ required: true, message: '请输入需求名称', trigger: 'blur' }],
  original_content: [{ required: true, message: '请输入需求内容', trigger: 'blur' }]
}

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
    
    // 加载Prompt模板
    const promptsResponse = await promptApi.getPromptTemplates({ tags: '需求' })
    prompts.value = promptsResponse
    
    // 加载支持的文件类型
    const fileTypesResponse = await getSupportedFileTypes()
    supportedFileTypes.value = fileTypesResponse.supported_types
    maxFileSize.value = fileTypesResponse.max_file_size_mb
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

const createDocument = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    createLoading.value = true
    
    await createRequirementDocument(createForm)
    
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
  createFormRef.value?.clearValidate()
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

const viewDocument = (doc: RequirementDocument) => {
  router.push(`/requirement/document/${doc.id}`)
}

const editDocument = (doc: RequirementDocument) => {
  router.push(`/requirement/document/${doc.id}/edit`)
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

// 文件上传相关
const beforeUpload = (file: File) => {
  const isValidType = supportedFileTypes.value.some(type => 
    file.name.toLowerCase().endsWith(`.${type}`)
  )
  
  if (!isValidType) {
    ElMessage.error(`不支持的文件类型。支持: ${supportedFileTypes.value.join(', ')}`)
    return false
  }
  
  const isValidSize = file.size / 1024 / 1024 < maxFileSize.value
  if (!isValidSize) {
    ElMessage.error(`文件大小不能超过 ${maxFileSize.value}MB`)
    return false
  }
  
  return true
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
</style> 