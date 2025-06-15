<template>
  <div class="requirement-test-container">
    <div class="page-header">
      <h1 class="page-title">需求测试分析</h1>
      <p class="page-description">输入需求内容或选择已有需求文档，使用AI进行测试用例分析</p>
    </div>

    <!-- 创建测试任务卡片 -->
    <el-card class="create-task-card" header="创建测试分析任务">
      <el-form
        ref="taskFormRef"
        :model="taskForm"
        :rules="taskRules"
        label-width="120px"
        class="task-form"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="需求来源">
          <el-radio-group v-model="requirementSource" @change="onSourceChange">
            <el-radio value="document">选择需求文档</el-radio>
            <el-radio value="input">直接输入</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item 
          v-if="requirementSource === 'document'" 
          label="需求文档" 
          prop="requirement_id"
        >
          <el-select
            v-model="taskForm.requirement_id"
            placeholder="选择需求文档"
            style="width: 100%"
            filterable
            @change="onDocumentChange"
          >
            <el-option
              v-for="doc in requirementDocuments"
              :key="doc.id"
              :label="doc.name"
              :value="doc.id"
            >
              <div class="document-option">
                <span class="doc-name">{{ doc.name }}</span>
                <el-tag :type="getStatusColor(doc.status)" size="small">
                  {{ getStatusLabel(doc.status) }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item 
          v-if="requirementSource === 'input'" 
          label="需求内容" 
          prop="requirement_content"
        >
          <el-input
            v-model="taskForm.requirement_content"
            type="textarea"
            :rows="8"
            placeholder="请输入需求内容..."
          />
        </el-form-item>
        
        <el-form-item label="测试Prompt" prop="prompt_template_id">
          <el-select
            v-model="taskForm.prompt_template_id"
            placeholder="选择测试分析Prompt模板"
            style="width: 100%"
          >
            <el-option
              v-for="prompt in testPrompts"
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
            v-model="taskForm.model_config_id"
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
        
        <el-form-item>
          <el-button type="primary" @click="createTask" :loading="createLoading">
            创建并执行任务
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 任务列表 -->
    <el-card class="task-list-card" header="测试分析任务">
      <template #header>
        <div class="card-header">
          <span>测试分析任务</span>
          <div class="header-actions">
            <el-select
              v-model="statusFilter"
              placeholder="筛选状态"
              clearable
              style="width: 150px; margin-right: 12px"
              @change="loadTasks"
            >
              <el-option
                v-for="option in taskStatusOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
            
            <el-button @click="loadTasks">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        v-loading="loading"
        :data="tasks"
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        
        <el-table-column prop="name" label="任务名称" min-width="200">
          <template #default="{ row }">
            <span class="task-name" @click="viewTask(row)">{{ row.name }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="需求来源" width="200">
          <template #default="{ row }">
            <div v-if="row.requirement_id" class="requirement-source">
              <el-icon><Document /></el-icon>
              <span>{{ getRequirementName(row.requirement_id) }}</span>
            </div>
            <div v-else class="requirement-source">
              <el-icon><Edit /></el-icon>
              <span>直接输入</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getTaskStatusColor(row.status)">
              {{ getTaskStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="执行信息" width="200">
          <template #default="{ row }">
            <div class="execution-info">
              <div v-if="row.tokens_used" class="info-item">
                <el-icon><Cpu /></el-icon>
                <span>{{ row.tokens_used }} tokens</span>
              </div>
              <div v-if="row.execution_time" class="info-item">
                <el-icon><Timer /></el-icon>
                <span>{{ row.execution_time.toFixed(2) }}s</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="viewTask(row)">
                <el-icon><View /></el-icon>
                查看结果
              </el-button>
              
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteTask(row)"
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
          @current-change="loadTasks"
          @size-change="loadTasks"
        />
      </div>
    </el-card>

    <!-- 任务结果详情对话框 -->
    <el-dialog
      v-model="showResultDialog"
      title="测试分析结果"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="currentTask" class="result-content">
        <div class="task-info">
          <h3>{{ currentTask.name }}</h3>
          <div class="meta-info">
            <el-tag :type="getTaskStatusColor(currentTask.status)">
              {{ getTaskStatusLabel(currentTask.status) }}
            </el-tag>
            <span v-if="currentTask.tokens_used" class="tokens">
              {{ currentTask.tokens_used }} tokens
            </span>
            <span v-if="currentTask.execution_time" class="time">
              {{ currentTask.execution_time.toFixed(2) }}s
            </span>
          </div>
        </div>
        
        <el-divider />
        
        <div v-if="currentTask.status === 'completed' && currentTask.result" class="analysis-result">
          <h4>分析结果</h4>
          <div class="result-display">
            <!-- 如果是JSON格式，尝试格式化显示 -->
            <div v-if="isJsonResult(currentTask.result)" class="json-result">
              <JsonViewer :data="currentTask.result" />
            </div>
            
            <!-- 否则使用Markdown显示 -->
            <div v-else class="markdown-result">
              <MarkdownEditor
                :model-value="String(currentTask.result.analysis || currentTask.result)"
                :preview="true"
                :readonly="true"
                height="400px"
              />
            </div>
          </div>
        </div>
        
        <div v-else-if="currentTask.status === 'failed'" class="error-info">
          <h4>执行失败</h4>
          <el-alert
            :title="currentTask.error_message || '未知错误'"
            type="error"
            show-icon
            :closable="false"
          />
        </div>
        
        <div v-else-if="currentTask.status === 'running'" class="running-info">
          <el-result icon="loading" title="任务执行中" sub-title="请耐心等待...">
            <template #extra>
              <el-button @click="loadTaskDetail">刷新状态</el-button>
            </template>
          </el-result>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showResultDialog = false">关闭</el-button>
        <el-button v-if="currentTask?.status === 'running'" @click="loadTaskDetail">
          刷新状态
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, ElForm } from 'element-plus'
import {
  Refresh,
  Document,
  Edit,
  View,
  Delete,
  Cpu,
  Timer
} from '@element-plus/icons-vue'
import { formatDate } from '@/utils/formatter'
import {
  getRequirementTestTasks,
  createRequirementTestTask,
  deleteRequirementTestTask,
  getRequirementTestTask,
  getRequirementDocuments,
  pollTaskStatus
} from '@/api/requirement'
import { aiModelApi, promptApi } from '@/api/ai'
import MarkdownEditor from '@/components/common/MarkdownEditor.vue'
import JsonViewer from '@/components/common/JsonViewer.vue'
import type {
  RequirementTestTask,
  CreateRequirementTestTaskRequest,
  RequirementDocument,
  TaskStatus,
  RequirementStatus
} from '@/types/requirement'
import type { AIModelConfig, PromptTemplate } from '@/types'
import {
  TASK_STATUS_OPTIONS,
  STATUS_COLOR_MAP,
  REQUIREMENT_STATUS_OPTIONS
} from '@/types/requirement'

// 状态数据
const loading = ref(false)
const createLoading = ref(false)
const tasks = ref<RequirementTestTask[]>([])
const selectedRows = ref<RequirementTestTask[]>([])
const statusFilter = ref<TaskStatus>()
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 弹窗状态
const showResultDialog = ref(false)
const currentTask = ref<RequirementTestTask>()

// 配置数据
const models = ref<AIModelConfig[]>([])
const prompts = ref<PromptTemplate[]>([])
const requirementDocuments = ref<RequirementDocument[]>([])

// 表单数据
const requirementSource = ref<'document' | 'input'>('input')
const taskFormRef = ref<InstanceType<typeof ElForm>>()

const taskForm = reactive<CreateRequirementTestTaskRequest>({
  name: '',
  requirement_id: undefined,
  requirement_content: '',
  prompt_template_id: undefined as any,
  model_config_id: undefined as any
})

// 表单验证规则
const taskRules = computed(() => ({
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  requirement_id: requirementSource.value === 'document' 
    ? [{ required: true, message: '请选择需求文档', trigger: 'change' }] 
    : [],
  requirement_content: requirementSource.value === 'input' 
    ? [{ required: true, message: '请输入需求内容', trigger: 'blur' }] 
    : [],
  prompt_template_id: [{ required: true, message: '请选择Prompt模板', trigger: 'change' }],
  model_config_id: [{ required: true, message: '请选择AI模型', trigger: 'change' }]
}))

// 计算属性
const taskStatusOptions = computed(() => TASK_STATUS_OPTIONS)

const testPrompts = computed(() => {
  return prompts.value.filter(p => 
    p.tags.includes('测试') || 
    p.tags.includes('test') ||
    p.tags.includes('测试用例') ||
    p.name.includes('测试')
  )
})

// 方法
const getStatusLabel = (status: RequirementStatus) => {
  const option = REQUIREMENT_STATUS_OPTIONS.find(opt => opt.value === status)
  return option?.label || status
}

const getStatusColor = (status: RequirementStatus) => {
  return STATUS_COLOR_MAP[status] || 'info'
}

const getTaskStatusLabel = (status: TaskStatus) => {
  const option = taskStatusOptions.value.find(opt => opt.value === status)
  return option?.label || status
}

const getTaskStatusColor = (status: TaskStatus) => {
  return STATUS_COLOR_MAP[status] || 'info'
}

const getRequirementName = (id: number) => {
  const doc = requirementDocuments.value.find(d => d.id === id)
  return doc?.name || `需求 ${id}`
}

const isJsonResult = (result: any): boolean => {
  return typeof result === 'object' && result !== null
}

// 数据加载
const loadTasks = async () => {
  try {
    loading.value = true
    const params = {
      status: statusFilter.value,
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    const response = await getRequirementTestTasks(params)
    tasks.value = response
    total.value = response.length
  } catch (error) {
    console.error('加载测试任务失败:', error)
    ElMessage.error('加载测试任务失败')
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
    const promptsResponse = await promptApi.getPromptTemplates({ tags: '测试' })
    prompts.value = promptsResponse
    
    // 加载需求文档
    const docsResponse = await getRequirementDocuments({ status: 'completed' })
    requirementDocuments.value = docsResponse
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

const loadTaskDetail = async () => {
  if (!currentTask.value) return
  
  try {
    const task = await getRequirementTestTask(currentTask.value.id)
    currentTask.value = task
    
    // 更新列表中的任务状态
    const index = tasks.value.findIndex(t => t.id === task.id)
    if (index !== -1) {
      tasks.value[index] = task
    }
  } catch (error) {
    console.error('加载任务详情失败:', error)
  }
}

// 表单操作
const onSourceChange = () => {
  // 清空相关字段
  if (requirementSource.value === 'document') {
    taskForm.requirement_content = ''
  } else {
    taskForm.requirement_id = undefined
  }
  taskFormRef.value?.clearValidate()
}

const onDocumentChange = (docId: number) => {
  const doc = requirementDocuments.value.find(d => d.id === docId)
  if (doc && !taskForm.name) {
    taskForm.name = `${doc.name} - 测试分析`
  }
}

const createTask = async () => {
  if (!taskFormRef.value) return
  
  try {
    await taskFormRef.value.validate()
    createLoading.value = true
    
    const task = await createRequirementTestTask(taskForm)
    
    ElMessage.success('测试分析任务创建成功')
    resetForm()
    loadTasks()
    
    // 开始轮询任务状态
    pollTaskStatus(
      () => getRequirementTestTask(task.id),
      (updatedTask) => {
        // 更新列表中的任务
        const index = tasks.value.findIndex(t => t.id === updatedTask.id)
        if (index !== -1) {
          tasks.value[index] = updatedTask
        }
      },
      (finalTask) => {
        ElMessage.success('测试分析完成')
        const index = tasks.value.findIndex(t => t.id === finalTask.id)
        if (index !== -1) {
          tasks.value[index] = finalTask
        }
      }
    )
  } catch (error) {
    console.error('创建测试任务失败:', error)
    ElMessage.error('创建测试任务失败')
  } finally {
    createLoading.value = false
  }
}

const resetForm = () => {
  Object.assign(taskForm, {
    name: '',
    requirement_id: undefined,
    requirement_content: '',
    prompt_template_id: undefined,
    model_config_id: undefined
  })
  requirementSource.value = 'input'
  taskFormRef.value?.clearValidate()
}

const viewTask = (task: RequirementTestTask) => {
  currentTask.value = task
  showResultDialog.value = true
  
  // 如果任务还在运行，开始轮询
  if (task.status === 'running') {
    pollTaskStatus(
      () => getRequirementTestTask(task.id),
      (updatedTask) => {
        currentTask.value = updatedTask
      },
      (finalTask) => {
        currentTask.value = finalTask
      }
    )
  }
}

const deleteTask = async (task: RequirementTestTask) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试任务 "${task.name}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    
    await deleteRequirementTestTask(task.id)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const onSelectionChange = (selection: RequirementTestTask[]) => {
  selectedRows.value = selection
}

// 生命周期
onMounted(() => {
  loadTasks()
  loadConfigurations()
})
</script>

<style scoped lang="scss">
.requirement-test-container {
  padding: 20px;
  
  .page-header {
    margin-bottom: 20px;
  }
}

.create-task-card {
  margin-bottom: 20px;
  
  .task-form {
    max-width: 800px;
  }
}

.task-list-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .header-actions {
      display: flex;
      align-items: center;
    }
  }
}

.document-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .doc-name {
    flex: 1;
    margin-right: 12px;
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

.task-name {
  cursor: pointer;
  color: #409eff;
  
  &:hover {
    text-decoration: underline;
  }
}

.requirement-source {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.execution-info {
  .info-item {
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

.pagination {
  margin-top: 20px;
  text-align: right;
}

.result-content {
  .task-info {
    .meta-info {
      margin-top: 8px;
      display: flex;
      align-items: center;
      gap: 12px;
      
      .tokens,
      .time {
        font-size: 12px;
        color: #666;
      }
    }
  }
  
  .analysis-result {
    .result-display {
      margin-top: 12px;
    }
  }
  
  .running-info,
  .error-info {
    text-align: center;
    padding: 20px;
  }
}
</style> 