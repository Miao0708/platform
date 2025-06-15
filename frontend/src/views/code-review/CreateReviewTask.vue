<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">创建代码评审任务</h1>
      <p class="page-description">通过4个步骤创建代码评审任务</p>
    </div>

    <el-card>
      <el-steps :active="currentStep" align-center>
        <el-step title="生成代码Diff" description="选择仓库和分支" />
        <el-step title="导入需求" description="上传或输入需求文档" />
        <el-step title="创建任务" description="配置评审参数" />
        <el-step title="执行评审" description="运行AI评审" />
      </el-steps>

      <div class="step-content">
        <!-- 步骤1: 生成代码Diff -->
        <div v-if="currentStep === 0" class="step-panel">
          <h3>生成代码Diff</h3>
          <el-form :model="diffForm" label-width="120px">
            <el-form-item label="选择仓库">
              <el-select v-model="diffForm.repositoryId" placeholder="请选择仓库">
                <el-option label="核心交易系统" value="1" />
                <el-option label="支付系统" value="2" />
              </el-select>
            </el-form-item>
            <el-form-item label="比较类型">
              <el-radio-group v-model="diffForm.compareType">
                <el-radio label="branch">分支比较</el-radio>
                <el-radio label="commit">提交比较</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="源分支/提交">
              <el-input v-model="diffForm.sourceRef" placeholder="如: feature/login" />
            </el-form-item>
            <el-form-item label="目标分支/提交">
              <el-input v-model="diffForm.targetRef" placeholder="如: main" />
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤2: 导入需求 -->
        <div v-if="currentStep === 1" class="step-panel">
          <h3>导入需求文档</h3>
          <el-tabs v-model="requirementTab">
            <el-tab-pane label="手动输入" name="manual">
              <el-input
                v-model="requirementForm.content"
                type="textarea"
                :rows="10"
                placeholder="请输入需求描述..."
              />
            </el-tab-pane>
            <el-tab-pane label="文件上传" name="upload">
              <el-upload
                drag
                :auto-upload="false"
                :on-change="handleRequirementFileChange"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
              </el-upload>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 步骤3: 创建任务 -->
        <div v-if="currentStep === 2" class="step-panel">
          <h3>配置评审任务</h3>
          <el-form :model="taskForm" label-width="120px">
            <el-form-item label="任务名称">
              <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
            </el-form-item>
            <el-form-item label="Prompt模板">
              <el-select v-model="taskForm.promptTemplateId" placeholder="请选择模板">
                <el-option label="代码评审-安全漏洞扫描" value="1" />
              </el-select>
            </el-form-item>
            <el-form-item label="知识库">
              <el-select v-model="taskForm.knowledgeBaseId" placeholder="可选择知识库" clearable>
                <el-option label="项目设计文档" value="1" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤4: 执行评审 -->
        <div v-if="currentStep === 3" class="step-panel">
          <h3>执行评审</h3>
          <div class="execution-status">
            <el-result
              :icon="executionStatus.icon"
              :title="executionStatus.title"
              :sub-title="executionStatus.subtitle"
            >
              <template #extra>
                <el-button v-if="executionStatus.showRetry" type="primary" @click="executeReview">
                  重试
                </el-button>
                <el-button v-if="executionStatus.showViewReport" type="success" @click="viewReport">
                  查看报告
                </el-button>
              </template>
            </el-result>
          </div>
        </div>
      </div>

      <div class="step-actions">
        <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
        <el-button v-if="currentStep < 3" type="primary" @click="nextStep">下一步</el-button>
        <el-button v-if="currentStep === 2" type="success" @click="createAndExecute">
          创建并执行
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 需求输入方式
const requirementTab = ref('manual')

// 表单数据
const diffForm = reactive({
  repositoryId: '',
  compareType: 'branch',
  sourceRef: '',
  targetRef: ''
})

const requirementForm = reactive({
  content: '',
  source: 'manual',
  file: null as File | null
})

const taskForm = reactive({
  name: '',
  promptTemplateId: '',
  knowledgeBaseId: ''
})

// 执行状态
const executionStatus = reactive({
  icon: 'info',
  title: '准备执行',
  subtitle: '点击"创建并执行"开始评审',
  showRetry: false,
  showViewReport: false
})

// 下一步
const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

// 上一步
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 处理需求文件变化
const handleRequirementFileChange = (file: any) => {
  requirementForm.file = file.raw
  requirementForm.source = 'upload'
}

// 创建并执行
const createAndExecute = async () => {
  try {
    // 验证表单
    if (!taskForm.name || !taskForm.promptTemplateId) {
      ElMessage.error('请填写完整的任务信息')
      return
    }

    currentStep.value = 3
    
    // 更新执行状态
    executionStatus.icon = 'loading'
    executionStatus.title = '正在执行评审'
    executionStatus.subtitle = '请稍候，AI正在分析代码...'
    executionStatus.showRetry = false
    executionStatus.showViewReport = false

    // 模拟执行过程
    await new Promise(resolve => setTimeout(resolve, 3000))

    // 执行成功
    executionStatus.icon = 'success'
    executionStatus.title = '评审完成'
    executionStatus.subtitle = '代码评审已完成，可以查看详细报告'
    executionStatus.showRetry = false
    executionStatus.showViewReport = true

    ElMessage.success('评审任务执行成功')
  } catch (error) {
    // 执行失败
    executionStatus.icon = 'error'
    executionStatus.title = '评审失败'
    executionStatus.subtitle = '评审过程中出现错误，请重试'
    executionStatus.showRetry = true
    executionStatus.showViewReport = false

    ElMessage.error('评审任务执行失败')
  }
}

// 执行评审
const executeReview = () => {
  createAndExecute()
}

// 查看报告
const viewReport = () => {
  router.push('/code-review/report/1')
}
</script>

<style scoped lang="scss">
.step-content {
  margin: 40px 0;
  min-height: 300px;
}

.step-panel {
  h3 {
    margin-bottom: 20px;
    color: #333;
  }
}

.step-actions {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
  
  .el-button + .el-button {
    margin-left: 16px;
  }
}

.execution-status {
  text-align: center;
  padding: 40px 0;
}
</style>
