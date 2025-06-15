<template>
  <div class="markdown-editor">
    <el-input
      v-model="content"
      type="textarea"
      :rows="10"
      :readonly="readonly"
      placeholder="请输入模板内容..."

    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

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


</script>

<style scoped lang="scss">
.markdown-editor {
  width: 100%;
}
</style>
