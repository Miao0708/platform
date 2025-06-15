<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="layout-sidebar">
      <Sidebar />
    </el-aside>
    
    <!-- 主内容区域 -->
    <el-container class="layout-main">
      <!-- 顶部导航 -->
      <el-header class="layout-header">
        <Header />
      </el-header>
      
      <!-- 内容区域 -->
      <el-main class="layout-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/app'
import Header from './Header.vue'
import Sidebar from './Sidebar.vue'

const appStore = useAppStore()
const { sidebarCollapsed } = storeToRefs(appStore)

// 计算侧边栏宽度
const sidebarWidth = computed(() => {
  return sidebarCollapsed.value ? '64px' : '240px'
})
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
  
  .layout-sidebar {
    background: #001529;
    transition: width 0.3s ease;
    overflow: hidden;
  }
  
  .layout-main {
    .layout-header {
      background: #fff;
      border-bottom: 1px solid #e8e8e8;
      padding: 0;
      height: 60px;
      line-height: 60px;
    }
    
    .layout-content {
      background: #f5f5f5;
      padding: 0;
      overflow-y: auto;
    }
  }
}
</style>
