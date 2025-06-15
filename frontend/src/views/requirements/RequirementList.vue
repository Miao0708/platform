<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">需求管理</h1>
      <p class="page-description">管理项目需求文档，支持AI解析和优化</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>需求列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="showUploadDialog">
              上传需求文档
            </el-button>
            <el-button type="success" @click="showCreateDialog">
              手动创建需求
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 筛选条件 -->
      <div class="filter-section mb-3">
        <el-form :model="filterForm" inline>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="全部状态" clearable>
              <el-option label="待处理" value="pending" />
              <el-option label="解析中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="需求名称">
            <el-input
              v-model="filterForm.name"
              placeholder="请输入需求名称"
              clearable
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="loadRequirements">搜索</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 需求表格 -->
      <el-table :data="requirements" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="需求名称" />
        <el-table-column prop="source" label="来源" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.source === 'upload' ? 'primary' : 'success'">
              {{ scope.row.source === 'upload' ? '文件上传' : '手动创建' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="300">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              @click="viewOriginalContent(scope.row)"
            >
              查看原始需求
            </el-button>
            
            <el-button
              v-if="scope.row.optimizedContent"
              type="success"
              size="small"
              @click="viewOptimizedContent(scope.row)"
            >
              查看优化需求
            </el-button>
            
            <el-button
              v-if="scope.row.status === 'pending'"
              type="warning"
              size="small"
              @click="parseRequirement(scope.row)"
              :loading="scope.row.parsing"
            >
              AI解析
            </el-button>
            
            <el-button
              type="text"
              size="small"
              @click="deleteRequirement(scope.row)"
              style="color: #f56c6c"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadRequirements"
          @current-change="loadRequirements"
        />
      </div>
    </el-card>

    <!-- 上传需求文档对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传需求文档"
      width="500px"
    >
      <el-form :model="uploadForm" label-width="120px">
        <el-form-item label="需求名称">
          <el-input v-model="uploadForm.name" placeholder="请输入需求名称" />
        </el-form-item>
        
        <el-form-item label="需求文档">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".txt,.md,.doc,.docx,.pdf"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 .txt, .md, .doc, .docx, .pdf 格式文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="uploadRequirement" :loading="uploading">
          上传并解析
        </el-button>
      </template>
    </el-dialog>

    <!-- 手动创建需求对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建需求"
      width="800px"
    >
      <el-form :model="createForm" label-width="120px">
        <el-form-item label="需求名称">
          <el-input v-model="createForm.name" placeholder="请输入需求名称" />
        </el-form-item>
        
        <el-form-item label="需求内容">
          <el-input
            v-model="createForm.content"
            type="textarea"
            :rows="10"
            placeholder="请输入需求内容..."
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createRequirement" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 需求内容查看对话框 -->
    <el-dialog
      v-model="contentDialogVisible"
      :title="contentDialogTitle"
      width="90%"
      class="content-dialog"
    >
      <div class="content-viewer">
        <MarkdownEditor
          v-if="isEditing"
          v-model="editingContent"
          height="60vh"
          :enable-ai-optimize="true"
          @save="saveEditedContent"
          @ai-optimize="handleAiOptimize"
        />
        <div v-else-if="viewingContent" v-html="renderedContent" class="markdown-content"></div>
      </div>

      <template #footer>
        <el-button @click="contentDialogVisible = false">关闭</el-button>
        <el-button v-if="currentRequirement && !isEditing" type="primary" @click="startEdit">
          编辑
        </el-button>
        <el-button v-if="isEditing" @click="cancelEdit">
          取消编辑
        </el-button>
        <el-button v-if="isEditing" type="primary" @click="saveEditedContent" :loading="savingContent">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox, type UploadInstance } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import MarkdownEditor from '@/components/common/MarkdownEditor.vue'
import type { RequirementDocument, TaskStatus } from '@/types'

// 组件引用
const uploadRef = ref<UploadInstance>()

// 加载状态
const loading = ref(false)
const uploading = ref(false)
const creating = ref(false)
const savingContent = ref(false)

// 对话框状态
const uploadDialogVisible = ref(false)
const createDialogVisible = ref(false)
const contentDialogVisible = ref(false)

// 编辑状态
const isEditing = ref(false)
const editingContent = ref('')

// 当前查看的需求
const currentRequirement = ref<RequirementDocument | null>(null)
const viewingContent = ref('')
const contentDialogTitle = ref('')

// 筛选表单
const filterForm = reactive({
  status: '',
  name: ''
})

// 分页信息
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 上传表单
const uploadForm = reactive({
  name: '',
  file: null as File | null
})

// 创建表单
const createForm = reactive({
  name: '',
  content: ''
})

// 需求列表
const requirements = ref<(RequirementDocument & { parsing?: boolean })[]>([])

// 渲染的内容（简单的Markdown渲染）
const renderedContent = computed(() => {
  if (!viewingContent.value) return ''
  
  // 简单的Markdown渲染
  return viewingContent.value
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
})

// 获取状态标签类型
const getStatusTagType = (status: TaskStatus) => {
  const typeMap = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: TaskStatus) => {
  const textMap = {
    pending: '待处理',
    processing: '解析中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || '未知'
}

// 显示上传对话框
const showUploadDialog = () => {
  Object.assign(uploadForm, {
    name: '',
    file: null
  })
  uploadDialogVisible.value = true
}

// 显示创建对话框
const showCreateDialog = () => {
  Object.assign(createForm, {
    name: '',
    content: ''
  })
  createDialogVisible.value = true
}

// 处理文件变化
const handleFileChange = (file: any) => {
  uploadForm.file = file.raw
  if (!uploadForm.name) {
    uploadForm.name = file.name.replace(/\.[^/.]+$/, '')
  }
}

// 上传需求文档
const uploadRequirement = async () => {
  if (!uploadForm.name || !uploadForm.file) {
    ElMessage.error('请填写需求名称并选择文件')
    return
  }
  
  try {
    uploading.value = true
    
    // TODO: 调用API上传文件并创建需求
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success('需求文档上传成功，正在解析中...')
    uploadDialogVisible.value = false
    loadRequirements()
  } catch (error) {
    console.error('Upload requirement failed:', error)
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

// 创建需求
const createRequirement = async () => {
  if (!createForm.name || !createForm.content) {
    ElMessage.error('请填写完整信息')
    return
  }
  
  try {
    creating.value = true
    
    // TODO: 调用API创建需求
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('需求创建成功')
    createDialogVisible.value = false
    loadRequirements()
  } catch (error) {
    console.error('Create requirement failed:', error)
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

// 查看原始需求内容
const viewOriginalContent = (requirement: RequirementDocument) => {
  currentRequirement.value = requirement
  viewingContent.value = requirement.originalContent
  contentDialogTitle.value = `原始需求 - ${requirement.name}`
  contentDialogVisible.value = true
}

// 查看优化需求内容
const viewOptimizedContent = (requirement: RequirementDocument) => {
  currentRequirement.value = requirement
  viewingContent.value = requirement.optimizedContent || ''
  contentDialogTitle.value = `优化需求 - ${requirement.name}`
  contentDialogVisible.value = true
}

// 开始编辑
const startEdit = () => {
  isEditing.value = true
  editingContent.value = viewingContent.value
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
  editingContent.value = ''
}

// 保存编辑内容
const saveEditedContent = async () => {
  if (!currentRequirement.value) return

  try {
    savingContent.value = true

    // TODO: 调用API保存编辑后的内容
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 更新当前需求的内容
    if (contentDialogTitle.value.includes('原始需求')) {
      currentRequirement.value.originalContent = editingContent.value
    } else {
      currentRequirement.value.optimizedContent = editingContent.value
    }

    viewingContent.value = editingContent.value
    isEditing.value = false

    ElMessage.success('内容保存成功')
  } catch (error) {
    console.error('Save content failed:', error)
    ElMessage.error('保存失败')
  } finally {
    savingContent.value = false
  }
}

// 处理AI优化
const handleAiOptimize = async (content: string) => {
  try {
    savingContent.value = true
    ElMessage.info('正在使用AI优化内容...')

    // TODO: 调用AI API优化内容
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 模拟AI优化结果
    editingContent.value = `# 优化后的内容

${content}

## AI优化建议
- 增加了结构化描述
- 完善了功能需求细节
- 添加了非功能性需求
- 优化了表达方式`
    ElMessage.success('AI优化完成')
  } catch (error) {
    console.error('AI optimize failed:', error)
    ElMessage.error('AI优化失败')
  } finally {
    savingContent.value = false
  }
}

// AI解析需求
const parseRequirement = async (requirement: RequirementDocument & { parsing?: boolean }) => {
  try {
    requirement.parsing = true
    
    // TODO: 调用AI解析API
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    ElMessage.success('需求解析完成')
    loadRequirements()
  } catch (error) {
    console.error('Parse requirement failed:', error)
    ElMessage.error('解析失败')
  } finally {
    requirement.parsing = false
  }
}

// 删除需求
const deleteRequirement = async (requirement: RequirementDocument) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除需求 "${requirement.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API删除需求
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('需求删除成功')
    loadRequirements()
  } catch {
    // 用户取消
  }
}

// 重置筛选
const resetFilter = () => {
  Object.assign(filterForm, {
    status: '',
    name: ''
  })
  loadRequirements()
}

// 加载需求列表
const loadRequirements = async () => {
  try {
    loading.value = true
    
    // TODO: 调用API加载需求列表
    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    requirements.value = [
      {
        id: '1',
        name: '用户登录功能需求',
        originalContent: '# 用户登录功能需求\n\n## 功能描述\n用户可以通过用户名和密码登录系统...',
        optimizedContent: '# 优化后的用户登录功能需求\n\n## 功能描述\n系统应提供安全的用户认证机制...',
        source: 'upload',
        originalFilename: '登录需求.md',
        status: 'completed',

      },
      {
        id: '2',
        name: '支付流程需求',
        originalContent: '支付功能需要支持多种支付方式，包括支付宝、微信支付等...',
        source: 'manual',
        status: 'processing',

      }
    ]
    
    pagination.total = 2
  } catch (error) {
    console.error('Load requirements failed:', error)
    ElMessage.error('加载需求列表失败')
  } finally {
    loading.value = false
  }
}

// 处理编辑器快捷键事件
const handleEditorKeyboardEvents = () => {
  // 监听保存事件
  const handleSave = () => {
    if (isEditing.value) {
      saveEditedContent()
    }
  }

  // 监听AI优化事件
  const handleEditorAiOptimize = () => {
    if (isEditing.value && editingContent.value) {
      handleAiOptimize(editingContent.value)
    }
  }

  document.addEventListener('editor-save', handleSave)
  document.addEventListener('editor-ai-optimize', handleEditorAiOptimize)

  return () => {
    document.removeEventListener('editor-save', handleSave)
    document.removeEventListener('editor-ai-optimize', handleEditorAiOptimize)
  }
}

onMounted(() => {
  loadRequirements()
  const cleanup = handleEditorKeyboardEvents()

  onUnmounted(() => {
    cleanup()
  })
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .header-actions {
    display: flex;
    gap: 8px;
  }
}

.filter-section {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.content-dialog {
  .content-viewer {
    max-height: 60vh;
    overflow-y: auto;
    
    .markdown-content {
      line-height: 1.6;
      
      :deep(code) {
        background: #f5f5f5;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
      }
      
      :deep(strong) {
        font-weight: 600;
      }
      
      :deep(em) {
        font-style: italic;
      }
    }
  }
}
</style>
