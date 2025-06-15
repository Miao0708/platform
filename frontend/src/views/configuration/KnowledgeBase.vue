<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">知识库管理</h1>
      <p class="page-description">管理项目相关文档，为AI提供背景知识</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>知识库列表</span>
          <el-button type="primary" @click="showAddDialog">
            新建知识库
          </el-button>
        </div>
      </template>
      
      <el-table :data="knowledgeBases" style="width: 100%">
        <el-table-column prop="name" label="知识库名称" />
        <el-table-column prop="description" label="说明" show-overflow-tooltip />
        <el-table-column prop="documentCount" label="文档数量" />
        <el-table-column prop="createdAt" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="text" @click="manageDocuments(scope.row)">
              管理文档
            </el-button>
            <el-button type="text" @click="editKnowledgeBase(scope.row)">
              编辑
            </el-button>
            <el-button type="text" @click="deleteKnowledgeBase(scope.row)" style="color: #f56c6c">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑知识库对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑知识库' : '新建知识库'"
      width="500px"
    >
      <el-form
        ref="knowledgeBaseFormRef"
        :model="knowledgeBaseForm"
        :rules="knowledgeBaseRules"
        label-width="120px"
      >
        <el-form-item label="知识库名称" prop="name">
          <el-input
            v-model="knowledgeBaseForm.name"
            placeholder="请输入知识库名称"
          />
        </el-form-item>
        
        <el-form-item label="说明">
          <el-input
            v-model="knowledgeBaseForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入知识库说明"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveKnowledgeBase" :loading="saving">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 文档管理对话框 -->
    <el-dialog
      v-model="documentsDialogVisible"
      :title="`管理文档 - ${currentKnowledgeBase?.name}`"
      width="800px"
    >
      <div class="documents-management">
        <div class="upload-section">
          <el-upload
            ref="uploadRef"
            :action="uploadAction"
            :headers="uploadHeaders"
            :data="uploadData"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            multiple
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 .md, .txt, .pdf 格式文件，单个文件不超过10MB
              </div>
            </template>
          </el-upload>
        </div>
        
        <el-divider />
        
        <div class="documents-list">
          <el-table :data="documents" style="width: 100%">
            <el-table-column prop="filename" label="文件名" />
            <el-table-column prop="fileType" label="类型" width="80" />
            <el-table-column prop="fileSize" label="大小" width="100">
              <template #default="scope">
                {{ formatFileSize(scope.row.fileSize) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusTagType(scope.row.status)">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="上传时间" />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button type="text" @click="deleteDocument(scope.row)" style="color: #f56c6c">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadInstance } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { knowledgeApi } from '@/api/knowledge'
import type { KnowledgeBase, KnowledgeDocument } from '@/types'

// 表单引用
const knowledgeBaseFormRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()

// 加载状态
const saving = ref(false)

// 知识库列表
const knowledgeBases = ref<KnowledgeBase[]>([])

// 对话框状态
const dialogVisible = ref(false)
const documentsDialogVisible = ref(false)
const isEdit = ref(false)

// 当前操作的知识库
const currentKnowledgeBase = ref<KnowledgeBase | null>(null)

// 文档列表
const documents = ref<KnowledgeDocument[]>([])

// 知识库表单
const knowledgeBaseForm = reactive({
  id: '',
  name: '',
  description: ''
})

// 表单验证规则
const knowledgeBaseRules: FormRules = {
  name: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' }
  ]
}

// 上传配置
const uploadAction = computed(() => '/api/knowledge-base/upload')
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))
const uploadData = computed(() => ({
  knowledgeBaseId: currentKnowledgeBase.value?.id
}))

// 显示添加对话框
const showAddDialog = () => {
  isEdit.value = false
  Object.assign(knowledgeBaseForm, {
    id: '',
    name: '',
    description: ''
  })
  dialogVisible.value = true
}

// 编辑知识库
const editKnowledgeBase = (knowledgeBase: KnowledgeBase) => {
  isEdit.value = true
  Object.assign(knowledgeBaseForm, knowledgeBase)
  dialogVisible.value = true
}

// 管理文档
const manageDocuments = (knowledgeBase: KnowledgeBase) => {
  currentKnowledgeBase.value = knowledgeBase
  loadDocuments(knowledgeBase.id)
  documentsDialogVisible.value = true
}

// 保存知识库
const saveKnowledgeBase = async () => {
  if (!knowledgeBaseFormRef.value) return
  
  try {
    await knowledgeBaseFormRef.value.validate()
    saving.value = true
    
    const requestData = {
      name: knowledgeBaseForm.name,
      description: knowledgeBaseForm.description
    }
    
    if (isEdit.value) {
      await knowledgeApi.updateKnowledgeBase(knowledgeBaseForm.id, requestData)
    } else {
      await knowledgeApi.createKnowledgeBase(requestData)
    }
    
    ElMessage.success(isEdit.value ? '知识库更新成功' : '知识库创建成功')
    dialogVisible.value = false
    loadKnowledgeBases()
  } catch (error) {
    console.error('Save knowledge base failed:', error)
    ElMessage.error(isEdit.value ? '知识库更新失败' : '知识库创建失败')
  } finally {
    saving.value = false
  }
}

// 删除知识库
const deleteKnowledgeBase = async (knowledgeBase: KnowledgeBase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除知识库 "${knowledgeBase.name}" 吗？这将同时删除其中的所有文档。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await knowledgeApi.deleteKnowledgeBase(knowledgeBase.id)
    
    ElMessage.success('知识库删除成功')
    loadKnowledgeBases()
  } catch (error: any) {
    if (error?.name !== 'cancel') {
      console.error('Delete knowledge base failed:', error)
      ElMessage.error('知识库删除失败')
    }
  }
}

// 文件上传前检查
const beforeUpload = (file: File) => {
  const allowedTypes = ['.md', '.txt', '.pdf']
  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
  
  if (!allowedTypes.includes(fileExtension)) {
    ElMessage.error('只支持 .md, .txt, .pdf 格式文件')
    return false
  }
  
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  
  return true
}

// 上传成功
const handleUploadSuccess = (response: any, file: File) => {
  ElMessage.success(`文件 ${file.name} 上传成功`)
  loadDocuments(currentKnowledgeBase.value!.id)
}

// 上传失败
const handleUploadError = (error: any, file: File) => {
  ElMessage.error(`文件 ${file.name} 上传失败`)
}

// 删除文档
const deleteDocument = async (document: KnowledgeDocument) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${document.filename}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API删除文档
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('文档删除成功')
    loadDocuments(currentKnowledgeBase.value!.id)
  } catch {
    // 用户取消
  }
}

// 格式化文件大小
const formatFileSize = (size: number) => {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(1) + ' MB'
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  const typeMap: Record<string, string> = {
    uploading: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    uploading: '上传中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || '未知'
}

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    const result = await knowledgeApi.getKnowledgeBases()
    
    // 转换数据格式以匹配前端类型
    knowledgeBases.value = (result || []).map((kb: any) => ({
      id: kb.id,
      name: kb.name,
      description: kb.description,
      documentCount: kb.document_count || 0,
      totalSize: kb.total_size || 0,
      isActive: kb.is_active,
      createdAt: kb.created_at,
      updatedAt: kb.updated_at
    }))
  } catch (error) {
    console.error('Load knowledge bases failed:', error)
    ElMessage.error('加载知识库列表失败')
  }
}

// 加载文档列表
const loadDocuments = async (knowledgeBaseId: string) => {
  try {
    const result = await knowledgeApi.getDocuments(knowledgeBaseId)
    
    // 转换数据格式以匹配前端类型
    documents.value = (result || []).map((doc: any) => ({
      id: doc.id,
      knowledgeBaseId: doc.knowledge_base_id,
      filename: doc.filename,
      fileType: doc.file_type,
      fileSize: doc.file_size,
      status: doc.status,
      errorMessage: doc.error_message,
      createdAt: doc.created_at,
      updatedAt: doc.updated_at
    }))
  } catch (error) {
    console.error('Load documents failed:', error)
    ElMessage.error('加载文档列表失败')
  }
}

onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.documents-management {
  .upload-section {
    margin-bottom: 20px;
  }
  
  .documents-list {
    max-height: 400px;
    overflow-y: auto;
  }
}
</style>
