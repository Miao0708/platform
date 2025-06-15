<template>
  <div v-if="hasError" class="error-boundary">
    <el-result
      icon="error"
      title="页面出现错误"
      sub-title="抱歉，页面遇到了一些问题"
    >
      <template #extra>
        <el-button type="primary" @click="reload">
          重新加载
        </el-button>
        <el-button @click="goHome">
          返回首页
        </el-button>
      </template>
    </el-result>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const hasError = ref(false)

onErrorCaptured((error: Error) => {
  console.error('Error captured by ErrorBoundary:', error)
  hasError.value = true
  return false // 阻止错误继续传播
})

const reload = () => {
  hasError.value = false
  window.location.reload()
}

const goHome = () => {
  hasError.value = false
  router.push('/')
}
</script>

<style scoped lang="scss">
.error-boundary {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
