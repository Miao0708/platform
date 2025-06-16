<template>
  <div class="json-viewer">
    <pre class="json-content">{{ formattedData }}</pre>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  data: any
  indent?: number
}

const props = withDefaults(defineProps<Props>(), {
  indent: 2
})

const formattedData = computed(() => {
  if (props.data === null || props.data === undefined) {
    return 'null'
  }
  
  try {
    return JSON.stringify(props.data, null, props.indent)
  } catch (error) {
    return String(props.data)
  }
})
</script>

<style scoped lang="scss">
.json-viewer {
  .json-content {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    padding: 12px;
    margin: 0;
    font-family: 'Courier New', Consolas, monospace;
    font-size: 13px;
    line-height: 1.5;
    color: #333;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-all;
  }
}
</style> 