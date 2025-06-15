<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { useKeyboard } from '@/composables/useKeyboard'

const userStore = useUserStore()
const appStore = useAppStore()

// 启用全局快捷键
useKeyboard()

onMounted(() => {
  // 初始化应用
  userStore.initializeAuth()
  appStore.initializeApp()
})
</script>

<style>
/* 全局样式已在 main.ts 中引入 */
</style>
