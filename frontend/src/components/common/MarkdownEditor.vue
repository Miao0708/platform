<template>
  <div class="markdown-editor">
    <MdEditor
      v-model="content"
      :height="height"
      :preview="preview"
      :toolbars="toolbars"
      @save="handleSave"
      @upload-img="handleUploadImg"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'

interface Props {
  modelValue: string
  height?: string
  preview?: boolean
  readonly?: boolean
  enableAiOptimize?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'save', value: string): void
  (e: 'ai-optimize', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  height: '400px',
  preview: true,
  readonly: false,
  enableAiOptimize: false
})

const emit = defineEmits<Emits>()

// 编辑器内容
const content = ref(props.modelValue)

// 工具栏配置
const toolbars = computed(() => {
  const baseToolbars = [
    'bold',
    'underline',
    'italic',
    '-',
    'title',
    'strikeThrough',
    'sub',
    'sup',
    'quote',
    'unorderedList',
    'orderedList',
    'task',
    '-',
    'codeRow',
    'code',
    'link',
    'image',
    'table',
    'mermaid',
    'katex',
    '-',
    'revoke',
    'next',
    'save'
  ]

  // 如果启用AI优化，添加AI优化按钮
  if (props.enableAiOptimize) {
    baseToolbars.push('-', {
      title: 'AI优化',
      icon: 'icon-ai-optimize',
      action: handleAiOptimize
    })
  }

  baseToolbars.push(
    '=',
    'pageFullscreen',
    'fullscreen',
    'preview',
    'previewOnly',
    'htmlPreview',
    'catalog'
  )

  return baseToolbars
})

// 监听内容变化
watch(
  () => content.value,
  (newValue) => {
    emit('update:modelValue', newValue)
  }
)

// 监听外部值变化
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== content.value) {
      content.value = newValue
    }
  }
)

// 处理保存
const handleSave = (value: string) => {
  emit('save', value)
}

// 处理AI优化
const handleAiOptimize = () => {
  emit('ai-optimize', content.value)
}

// 处理图片上传
const handleUploadImg = async (files: File[], callback: (urls: string[]) => void) => {
  try {
    // TODO: 实现图片上传逻辑
    // 这里模拟上传过程
    const urls = await Promise.all(
      files.map(async (file) => {
        // 模拟上传延迟
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 返回模拟的图片URL
        return URL.createObjectURL(file)
      })
    )
    
    callback(urls)
  } catch (error) {
    console.error('Upload image failed:', error)
    callback([])
  }
}
</script>

<style scoped lang="scss">
.markdown-editor {
  :deep(.md-editor) {
    border-radius: 6px;
    
    .md-editor-toolbar {
      border-bottom: 1px solid #e8e8e8;
    }
    
    .md-editor-input-wrapper,
    .md-editor-preview-wrapper {
      font-size: 14px;
      line-height: 1.6;
    }
    
    .md-editor-preview {
      h1, h2, h3, h4, h5, h6 {
        margin-top: 24px;
        margin-bottom: 16px;
        font-weight: 600;
        line-height: 1.25;
      }
      
      h1 {
        font-size: 2em;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 10px;
      }
      
      h2 {
        font-size: 1.5em;
        border-bottom: 1px solid #eaecef;
        padding-bottom: 8px;
      }
      
      p {
        margin-bottom: 16px;
      }
      
      code {
        background: #f6f8fa;
        border-radius: 3px;
        font-size: 85%;
        margin: 0;
        padding: 0.2em 0.4em;
      }
      
      pre {
        background: #f6f8fa;
        border-radius: 6px;
        font-size: 85%;
        line-height: 1.45;
        overflow: auto;
        padding: 16px;
        
        code {
          background: transparent;
          border: 0;
          display: inline;
          line-height: inherit;
          margin: 0;
          max-width: none;
          overflow: visible;
          padding: 0;
          word-wrap: normal;
        }
      }
      
      blockquote {
        border-left: 4px solid #dfe2e5;
        color: #6a737d;
        margin: 0 0 16px 0;
        padding: 0 16px;
      }
      
      table {
        border-collapse: collapse;
        border-spacing: 0;
        display: block;
        margin-bottom: 16px;
        overflow: auto;
        width: 100%;
        
        th, td {
          border: 1px solid #dfe2e5;
          padding: 6px 13px;
        }
        
        th {
          background: #f6f8fa;
          font-weight: 600;
        }
        
        tr:nth-child(2n) {
          background: #f6f8fa;
        }
      }
      
      ul, ol {
        margin-bottom: 16px;
        padding-left: 2em;
        
        li {
          margin-bottom: 4px;
        }
      }
      
      img {
        max-width: 100%;
        height: auto;
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
    }
  }
}
</style>
