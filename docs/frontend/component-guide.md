# 前端组件开发指南

## 📋 组件架构概述

基于 Vue 3 Composition API + Element Plus 的组件开发指南，包含通用组件、业务组件和布局组件的开发规范。

## 🏗️ 组件分类

### 通用组件 (src/components/common/)
基础可复用组件，不包含业务逻辑

### 图标组件 (src/components/icons/)
项目自定义图标和 Element Plus 图标的封装

### 布局组件 (src/components/layout/)
页面布局相关组件，如头部、侧边栏、内容区域等

### 业务组件 (src/views/)
特定业务功能的页面组件

## 🎨 组件开发规范

### 1. 组件命名规范
- **文件名**: 使用 kebab-case (如: `user-profile.vue`)
- **组件名**: 使用 PascalCase (如: `UserProfile`)
- **Props**: 使用 camelCase (如: `userName`)
- **事件**: 使用 kebab-case (如: `@update-user`)

### 2. 组件模板结构
```vue
<template>
  <div class="component-wrapper">
    <!-- 组件内容 -->
  </div>
</template>

<script setup lang="ts">
// 导入
import { ref, computed, onMounted } from 'vue'
import type { ComponentProps } from '@/types/component'

// 接口定义
interface Props {
  title: string
  data?: any[]
  loading?: boolean
}

interface Emits {
  (e: 'update', value: any): void
  (e: 'submit'): void
}

// Props 和 Emits
const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  loading: false
})

const emit = defineEmits<Emits>()

// 响应式状态
const localData = ref([])
const isVisible = ref(false)

// 计算属性
const displayData = computed(() => {
  return props.data.filter(item => item.visible)
})

// 方法
const handleUpdate = (value: any) => {
  emit('update', value)
}

// 生命周期
onMounted(() => {
  console.log('组件已挂载')
})

// 暴露给父组件的方法/属性
defineExpose({
  refresh: handleUpdate
})
</script>

<style lang="scss" scoped>
.component-wrapper {
  // 样式定义
}
</style>
```

## 📦 常用组件库

### 1. 表格组件 (DataTable)
```vue
<template>
  <div class="data-table">
    <el-table
      :data="tableData"
      :loading="loading"
      stripe
      @selection-change="handleSelectionChange"
    >
      <el-table-column
        v-for="column in columns"
        :key="column.prop"
        :prop="column.prop"
        :label="column.label"
        :width="column.width"
        :formatter="column.formatter"
      />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button
            size="small"
            @click="$emit('edit', row)"
          >
            编辑
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="$emit('delete', row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <el-pagination
      v-if="showPagination"
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
    />
  </div>
</template>

<script setup lang="ts">
interface Column {
  prop: string
  label: string
  width?: string
  formatter?: (row: any, column: any, cellValue: any) => string
}

interface Props {
  data: any[]
  columns: Column[]
  loading?: boolean
  showPagination?: boolean
  total?: number
}

interface Emits {
  (e: 'edit', row: any): void
  (e: 'delete', row: any): void
  (e: 'page-change', page: number): void
  (e: 'size-change', size: number): void
  (e: 'selection-change', selection: any[]): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  showPagination: true,
  total: 0
})

const emit = defineEmits<Emits>()

const currentPage = ref(1)
const pageSize = ref(10)

const tableData = computed(() => props.data)

const handlePageChange = (page: number) => {
  emit('page-change', page)
}

const handleSizeChange = (size: number) => {
  emit('size-change', size)
}

const handleSelectionChange = (selection: any[]) => {
  emit('selection-change', selection)
}
</script>
```

### 2. 表单组件 (FormBuilder)
```vue
<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    :label-width="labelWidth"
    @submit.prevent="handleSubmit"
  >
    <el-form-item
      v-for="field in fields"
      :key="field.prop"
      :label="field.label"
      :prop="field.prop"
      :required="field.required"
    >
      <!-- 输入框 -->
      <el-input
        v-if="field.type === 'input'"
        v-model="formData[field.prop]"
        :placeholder="field.placeholder"
        :disabled="field.disabled"
      />
      
      <!-- 选择器 -->
      <el-select
        v-else-if="field.type === 'select'"
        v-model="formData[field.prop]"
        :placeholder="field.placeholder"
        :disabled="field.disabled"
      >
        <el-option
          v-for="option in field.options"
          :key="option.value"
          :label="option.label"
          :value="option.value"
        />
      </el-select>
      
      <!-- 日期选择器 -->
      <el-date-picker
        v-else-if="field.type === 'date'"
        v-model="formData[field.prop]"
        type="date"
        :placeholder="field.placeholder"
        :disabled="field.disabled"
      />
      
      <!-- 文本域 -->
      <el-input
        v-else-if="field.type === 'textarea'"
        v-model="formData[field.prop]"
        type="textarea"
        :rows="field.rows || 3"
        :placeholder="field.placeholder"
        :disabled="field.disabled"
      />
    </el-form-item>
    
    <el-form-item>
      <el-button type="primary" @click="handleSubmit">
        {{ submitText }}
      </el-button>
      <el-button @click="handleReset">
        重置
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import type { FormInstance, FormValidateCallback } from 'element-plus'

interface FormField {
  prop: string
  label: string
  type: 'input' | 'select' | 'date' | 'textarea'
  required?: boolean
  placeholder?: string
  disabled?: boolean
  options?: { label: string; value: any }[]
  rows?: number
}

interface Props {
  fields: FormField[]
  modelValue: Record<string, any>
  rules?: Record<string, any>
  labelWidth?: string
  submitText?: string
}

interface Emits {
  (e: 'update:modelValue', value: Record<string, any>): void
  (e: 'submit', value: Record<string, any>): void
  (e: 'reset'): void
}

const props = withDefaults(defineProps<Props>(), {
  labelWidth: '120px',
  submitText: '提交'
})

const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const formData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const handleSubmit = () => {
  formRef.value?.validate((valid: boolean) => {
    if (valid) {
      emit('submit', formData.value)
    }
  })
}

const handleReset = () => {
  formRef.value?.resetFields()
  emit('reset')
}

defineExpose({
  validate: (callback?: FormValidateCallback) => {
    return formRef.value?.validate(callback)
  },
  resetFields: () => {
    formRef.value?.resetFields()
  }
})
</script>
```

### 3. 对话框组件 (Modal)
```vue
<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    :before-close="handleClose"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
  >
    <div class="modal-content">
      <slot></slot>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">
          {{ cancelText }}
        </el-button>
        <el-button
          type="primary"
          :loading="confirmLoading"
          @click="handleConfirm"
        >
          {{ confirmText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
  title: string
  width?: string
  confirmText?: string
  cancelText?: string
  confirmLoading?: boolean
  closeOnClickModal?: boolean
  closeOnPressEscape?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
  (e: 'close'): void
}

const props = withDefaults(defineProps<Props>(), {
  width: '50%',
  confirmText: '确定',
  cancelText: '取消',
  confirmLoading: false,
  closeOnClickModal: true,
  closeOnPressEscape: true
})

const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  visible.value = false
  emit('cancel')
}

const handleClose = () => {
  visible.value = false
  emit('close')
}
</script>

<style lang="scss" scoped>
.modal-content {
  min-height: 100px;
}

.dialog-footer {
  text-align: right;
}
</style>
```

### 4. 文件上传组件 (FileUpload)
```vue
<template>
  <div class="file-upload">
    <el-upload
      ref="uploadRef"
      :action="action"
      :headers="headers"
      :data="uploadData"
      :multiple="multiple"
      :accept="accept"
      :limit="limit"
      :before-upload="beforeUpload"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-progress="handleProgress"
      :on-exceed="handleExceed"
      :on-remove="handleRemove"
      :file-list="fileList"
      :auto-upload="autoUpload"
    >
      <el-button type="primary">
        <el-icon><Upload /></el-icon>
        {{ buttonText }}
      </el-button>
      
      <template #tip>
        <div class="el-upload__tip">
          {{ tip }}
        </div>
      </template>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import { Upload } from '@element-plus/icons-vue'
import type { UploadFile, UploadFiles, UploadInstance } from 'element-plus'

interface Props {
  action: string
  headers?: Record<string, string>
  data?: Record<string, any>
  multiple?: boolean
  accept?: string
  limit?: number
  autoUpload?: boolean
  buttonText?: string
  tip?: string
  maxSize?: number // MB
}

interface Emits {
  (e: 'success', response: any, file: UploadFile): void
  (e: 'error', error: Error, file: UploadFile): void
  (e: 'progress', event: any, file: UploadFile): void
  (e: 'exceed', files: File[], fileList: UploadFiles): void
  (e: 'remove', file: UploadFile, fileList: UploadFiles): void
}

const props = withDefaults(defineProps<Props>(), {
  multiple: false,
  limit: 1,
  autoUpload: true,
  buttonText: '选择文件',
  tip: '',
  maxSize: 10
})

const emit = defineEmits<Emits>()

const uploadRef = ref<UploadInstance>()
const fileList = ref<UploadFile[]>([])

const uploadData = computed(() => props.data || {})

const beforeUpload = (file: File) => {
  // 文件大小检查
  if (file.size > props.maxSize * 1024 * 1024) {
    ElMessage.error(`文件大小不能超过 ${props.maxSize}MB`)
    return false
  }
  
  return true
}

const handleSuccess = (response: any, file: UploadFile) => {
  emit('success', response, file)
}

const handleError = (error: Error, file: UploadFile) => {
  emit('error', error, file)
}

const handleProgress = (event: any, file: UploadFile) => {
  emit('progress', event, file)
}

const handleExceed = (files: File[], fileList: UploadFiles) => {
  emit('exceed', files, fileList)
}

const handleRemove = (file: UploadFile, fileList: UploadFiles) => {
  emit('remove', file, fileList)
}

defineExpose({
  submit: () => uploadRef.value?.submit(),
  clearFiles: () => uploadRef.value?.clearFiles()
})
</script>
```

## 🎯 业务组件示例

### AI 对话组件
```vue
<template>
  <div class="ai-chat">
    <div class="chat-header">
      <h3>AI 助手</h3>
      <el-button size="small" @click="clearChat">
        清空对话
      </el-button>
    </div>
    
    <div ref="messagesRef" class="messages">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message', message.role]"
      >
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(message.content)"></div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <div v-if="loading" class="message assistant">
        <div class="message-content">
          <el-icon class="is-loading"><Loading /></el-icon>
          AI 正在思考...
        </div>
      </div>
    </div>
    
    <div class="input-area">
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="3"
        placeholder="输入你的问题..."
        @keydown.ctrl.enter="sendMessage"
      />
      <div class="input-actions">
        <el-button
          type="primary"
          :disabled="!inputText.trim() || loading"
          @click="sendMessage"
        >
          发送 (Ctrl+Enter)
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'
import { marked } from 'marked'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

interface Props {
  messages: Message[]
  loading?: boolean
}

interface Emits {
  (e: 'send-message', content: string): void
  (e: 'clear-chat'): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<Emits>()

const inputText = ref('')
const messagesRef = ref<HTMLElement>()

const sendMessage = () => {
  if (!inputText.value.trim() || props.loading) return
  
  emit('send-message', inputText.value.trim())
  inputText.value = ''
}

const clearChat = () => {
  emit('clear-chat')
}

const formatMessage = (content: string) => {
  return marked.parse(content)
}

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString()
}

// 自动滚动到底部
watch(() => props.messages, () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
})
</script>

<style lang="scss" scoped>
.ai-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  
  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid var(--el-border-color-light);
  }
  
  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    
    .message {
      margin-bottom: 16px;
      
      &.user {
        .message-content {
          background: var(--el-color-primary);
          color: white;
          margin-left: auto;
          max-width: 70%;
        }
      }
      
      &.assistant {
        .message-content {
          background: var(--el-bg-color);
          border: 1px solid var(--el-border-color-light);
          max-width: 70%;
        }
      }
      
      .message-content {
        padding: 12px;
        border-radius: 8px;
        
        .message-text {
          margin-bottom: 4px;
        }
        
        .message-time {
          font-size: 12px;
          opacity: 0.7;
        }
      }
    }
  }
  
  .input-area {
    padding: 16px;
    border-top: 1px solid var(--el-border-color-light);
    
    .input-actions {
      margin-top: 8px;
      text-align: right;
    }
  }
}
</style>
```

## 🧪 组件测试

### 单元测试示例
```typescript
// tests/components/DataTable.spec.ts
import { mount } from '@vue/test-utils'
import DataTable from '@/components/DataTable.vue'

describe('DataTable', () => {
  const mockData = [
    { id: 1, name: '测试1', status: 'active' },
    { id: 2, name: '测试2', status: 'inactive' }
  ]
  
  const mockColumns = [
    { prop: 'name', label: '名称' },
    { prop: 'status', label: '状态' }
  ]
  
  it('渲染数据正确', () => {
    const wrapper = mount(DataTable, {
      props: {
        data: mockData,
        columns: mockColumns
      }
    })
    
    expect(wrapper.text()).toContain('测试1')
    expect(wrapper.text()).toContain('测试2')
  })
  
  it('触发编辑事件', async () => {
    const wrapper = mount(DataTable, {
      props: {
        data: mockData,
        columns: mockColumns
      }
    })
    
    await wrapper.find('.edit-btn').trigger('click')
    expect(wrapper.emitted('edit')).toBeTruthy()
  })
})
```

## 📚 最佳实践

### 1. 性能优化
- 使用 `v-memo` 优化列表渲染
- 合理使用 `computed` 缓存计算结果
- 大型组件使用异步组件加载
- 避免在模板中使用复杂表达式

### 2. 可访问性
- 为表单元素添加正确的 `label`
- 使用语义化的 HTML 标签
- 添加键盘导航支持
- 提供屏幕阅读器友好的内容

### 3. 国际化支持
```typescript
// 组件中使用 i18n
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const buttonText = computed(() => t('common.submit'))
```

### 4. 类型安全
- 为所有 Props 定义 TypeScript 接口
- 使用泛型增强组件的类型安全性
- 避免使用 `any` 类型

### 5. 文档和注释
```typescript
/**
 * 数据表格组件
 * @description 基于 Element Plus Table 的封装组件
 * @example
 * <DataTable
 *   :data="tableData"
 *   :columns="columns"
 *   @edit="handleEdit"
 * />
 */
```

## 🔗 相关资源

- [Vue 3 组合式 API](https://cn.vuejs.org/guide/extras/composition-api-faq.html)
- [Element Plus 组件库](https://element-plus.org/zh-CN/)
- [Vue 3 TypeScript 支持](https://cn.vuejs.org/guide/typescript/overview.html)
- [Vue 测试工具](https://test-utils.vuejs.org/) 