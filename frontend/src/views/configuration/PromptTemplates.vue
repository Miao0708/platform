<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Prompt模板管理</h1>
      <p class="page-description">创建和管理高质量的Prompt模板，支持链式调用</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>模板列表</span>
          <el-button type="primary" @click="showAddDialog">
            新建模板
          </el-button>
        </div>
      </template>
      
      <el-table :data="templates" style="width: 100%">
        <el-table-column prop="name" label="模板名称" />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="scope">
            <el-tag :type="getCategoryTagType(scope.row.category)">
              {{ getCategoryName(scope.row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" width="200">
          <template #default="scope">
            <el-tag
              v-for="tag in scope.row.tags"
              :key="tag"
              size="small"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usageCount" label="使用次数" width="100" />
        <el-table-column prop="isPublic" label="公开" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.isPublic ? 'success' : 'info'" size="small">
              {{ scope.row.isPublic ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="text" @click="showPreviewTemplate(scope.row)">
              预览
            </el-button>
            <el-button type="text" @click="editTemplate(scope.row)">
              编辑
            </el-button>
            <el-button type="text" @click="deleteTemplate(scope.row)" style="color: #f56c6c">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑模板对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑模板' : '新建模板'"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="templateFormRef"
        :model="templateForm"
        :rules="templateRules"
        label-width="120px"
      >
        <el-form-item label="模板名称" prop="name">
          <el-input
            v-model="templateForm.name"
            placeholder="请输入模板名称"
          />
        </el-form-item>

        <el-form-item label="唯一标识" prop="identifier">
          <el-input
            v-model="templateForm.identifier"
            placeholder="请输入英文标识，如：code_review_security"
          />
        </el-form-item>

        <el-form-item label="分类" prop="category">
          <el-select v-model="templateForm.category" placeholder="请选择分类">
            <el-option label="需求分析" value="requirement" />
            <el-option label="代码评审" value="code_review" />
            <el-option label="测试用例" value="test_case" />
            <el-option label="通用对话" value="general" />
          </el-select>
        </el-form-item>

        <el-form-item label="标签">
          <el-select
            v-model="templateForm.tags"
            multiple
            filterable
            allow-create
            placeholder="请选择或创建标签"
            style="width: 100%"
          >
            <el-option
              v-for="tag in availableTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="模板内容" prop="content">
          <MarkdownEditor
            v-model="templateForm.content"
            height="300px"
            @save="saveTemplate"
          />
          <div class="form-tip">
            支持变量占位符：{{code_diff}}、{{requirement}}、{{context}}等
          </div>
        </el-form-item>

        <el-form-item label="说明">
          <el-input
            v-model="templateForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模板说明，包括用途、适用场景和变量说明"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="templateForm.isPublic">公开模板（其他用户可见）</el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate" :loading="saving">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 模板预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="模板预览"
      width="70%"
    >
      <div v-if="currentPreviewTemplate" class="template-preview">
        <div class="preview-header">
          <h3>{{ currentPreviewTemplate.name }}</h3>
          <div class="template-meta">
            <el-tag :type="getCategoryTagType(currentPreviewTemplate.category)">
              {{ getCategoryName(currentPreviewTemplate.category) }}
            </el-tag>
            <el-tag
              v-for="tag in currentPreviewTemplate.tags"
              :key="tag"
              size="small"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <div class="preview-content">
          <MarkdownEditor
            :model-value="currentPreviewTemplate.content"
            :preview="true"
            :readonly="true"
            height="400px"
          />
        </div>

        <div v-if="currentPreviewTemplate.description" class="preview-description">
          <h4>说明</h4>
          <p>{{ currentPreviewTemplate.description }}</p>
        </div>
      </div>

      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button v-if="currentPreviewTemplate" type="primary" @click="editTemplate(currentPreviewTemplate)">
          编辑此模板
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import MarkdownEditor from '@/components/common/MarkdownEditor.vue'
import type { PromptTemplate } from '@/types'

// 表单引用
const templateFormRef = ref<FormInstance>()

// 加载状态
const saving = ref(false)

// 模板列表
const templates = ref<PromptTemplate[]>([])

// 对话框状态
const dialogVisible = ref(false)
const previewDialogVisible = ref(false)
const isEdit = ref(false)

// 当前预览的模板
const currentPreviewTemplate = ref<PromptTemplate | null>(null)

// 可用标签
const availableTags = ref(['需求分析', '代码评审', '安全检查', '性能优化', '测试用例', '文档生成'])

// 模板表单
const templateForm = reactive({
  id: '',
  name: '',
  identifier: '',
  content: '',
  description: '',
  category: 'general' as PromptTemplate['category'],
  tags: [] as string[],
  isPublic: true
})

// 表单验证规则
const templateRules: FormRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' }
  ],
  identifier: [
    { required: true, message: '请输入唯一标识', trigger: 'blur' },
    { pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/, message: '标识必须以字母开头，只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入模板内容', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ]
}

// 获取分类标签类型
const getCategoryTagType = (category: string) => {
  const typeMap: Record<string, string> = {
    requirement: 'primary',
    code_review: 'success',
    test_case: 'warning',
    general: 'info'
  }
  return typeMap[category] || 'info'
}

// 获取分类名称
const getCategoryName = (category: string) => {
  const nameMap: Record<string, string> = {
    requirement: '需求分析',
    code_review: '代码评审',
    test_case: '测试用例',
    general: '通用对话'
  }
  return nameMap[category] || category
}

// 显示添加对话框
const showAddDialog = () => {
  isEdit.value = false
  Object.assign(templateForm, {
    id: '',
    name: '',
    identifier: '',
    content: '',
    description: '',
    category: 'general',
    tags: [],
    isPublic: true
  })
  dialogVisible.value = true
}

// 预览模板
const showPreviewTemplate = (template: PromptTemplate) => {
  currentPreviewTemplate.value = template
  previewDialogVisible.value = true
}

// 编辑模板
const editTemplate = (template: PromptTemplate) => {
  isEdit.value = true
  Object.assign(templateForm, template)
  dialogVisible.value = true
}

// 保存模板
const saveTemplate = async () => {
  if (!templateFormRef.value) return
  
  try {
    await templateFormRef.value.validate()
    saving.value = true
    
    // TODO: 调用API保存模板
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success(isEdit.value ? '模板更新成功' : '模板创建成功')
    dialogVisible.value = false
    loadTemplates()
  } catch (error) {
    console.error('Save template failed:', error)
  } finally {
    saving.value = false
  }
}

// 删除模板
const deleteTemplate = async (template: PromptTemplate) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板 "${template.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // TODO: 调用API删除模板
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('模板删除成功')
    loadTemplates()
  } catch {
    // 用户取消
  }
}

// 加载模板列表
const loadTemplates = async () => {
  try {
    // TODO: 调用API加载模板列表
    // 模拟数据
    templates.value = [
      {
        id: '1',
        name: '代码评审-安全漏洞扫描',
        identifier: 'code_review_security',
        content: `你是一个代码安全专家，请仔细分析以下代码变更，识别潜在的安全漏洞：

## 代码差异
{{code_diff}}

## 分析要求
1. 检查SQL注入漏洞
2. 检查XSS攻击风险
3. 检查权限控制问题
4. 检查敏感信息泄露
5. 检查输入验证缺陷

请提供详细的安全分析报告。`,
        description: '专门用于检测代码中的安全问题，包括SQL注入、XSS、权限控制等常见安全漏洞',
        category: 'code_review' as const,
        tags: ['安全检查', '代码评审', '漏洞扫描'],
        variables: ['code_diff'],
        isPublic: true,
        usageCount: 156,
        createdAt: '2024-01-15 10:30:00',
        updatedAt: '2024-01-15 10:30:00'
      },
      {
        id: '2',
        name: '需求分析-功能拆解',
        identifier: 'requirement_analysis',
        content: `你是一个资深的产品经理，请对以下需求进行详细分析：

## 原始需求
{{requirement}}

## 分析维度
1. **功能拆解**：将需求拆解为具体的功能点
2. **用户故事**：编写用户故事和验收标准
3. **技术考量**：分析技术实现难点
4. **风险评估**：识别潜在风险和依赖
5. **优先级建议**：给出功能优先级建议

请提供结构化的需求分析报告。`,
        description: '用于分析和拆解产品需求，生成结构化的需求文档',
        category: 'requirement' as const,
        tags: ['需求分析', '功能拆解', '用户故事'],
        variables: ['requirement'],
        isPublic: true,
        usageCount: 89,
        createdAt: '2024-01-10 14:20:00',
        updatedAt: '2024-01-10 14:20:00'
      },
      {
        id: '3',
        name: '测试用例生成',
        identifier: 'test_case_generation',
        content: `你是一个测试专家，请根据以下需求生成详细的测试用例：

## 需求描述
{{requirement}}

## 代码实现
{{code_diff}}

## 测试用例要求
1. **正向测试**：正常流程的测试用例
2. **边界测试**：边界值和临界条件测试
3. **异常测试**：异常情况和错误处理测试
4. **性能测试**：性能相关的测试场景
5. **安全测试**：安全相关的测试用例

请按照标准格式生成测试用例。`,
        description: '根据需求和代码自动生成全面的测试用例',
        category: 'test_case' as const,
        tags: ['测试用例', '自动化测试', '质量保证'],
        variables: ['requirement', 'code_diff'],
        isPublic: true,
        usageCount: 234,
        createdAt: '2024-01-08 09:15:00',
        updatedAt: '2024-01-08 09:15:00'
      }
    ]
  } catch (error) {
    console.error('Load templates failed:', error)
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag-item {
  margin-right: 4px;
  margin-bottom: 4px;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.template-preview {
  .preview-header {
    margin-bottom: 20px;

    h3 {
      margin-bottom: 8px;
      color: #333;
    }

    .template-meta {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }

  .preview-content {
    margin-bottom: 20px;
  }

  .preview-description {
    h4 {
      margin-bottom: 8px;
      color: #333;
    }

    p {
      color: #666;
      line-height: 1.6;
    }
  }
}
</style>
