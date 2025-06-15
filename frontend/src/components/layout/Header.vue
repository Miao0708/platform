<template>
  <div class="header-container">
    <!-- 左侧 -->
    <div class="header-left">
      <el-button
        type="text"
        :icon="sidebarCollapsed ? Expand : Fold"
        @click="toggleSidebar"
        class="sidebar-toggle"
      />
      
      <el-breadcrumb separator="/" class="breadcrumb">
        <el-breadcrumb-item
          v-for="item in breadcrumbItems"
          :key="item.path"
          :to="item.path"
        >
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    
    <!-- 右侧 -->
    <div class="header-right">
      <!-- 全局搜索 -->
      <el-input
        v-model="searchKeyword"
        placeholder="搜索..."
        :prefix-icon="Search"
        class="search-input"
        clearable
      />
      
      <!-- AI助手快捷入口 -->
      <el-button type="primary" @click="openAiChat" class="ai-chat-btn">
        <el-icon><ChatDotRound /></el-icon>
        AI助手
      </el-button>

      <!-- 快捷键帮助 -->
      <el-button type="text" @click="showShortcutHelp" title="快捷键帮助 (Ctrl + /)">
        <el-icon><QuestionFilled /></el-icon>
      </el-button>

      <!-- 通知 -->
      <el-badge :value="notificationCount" class="notification-badge">
        <el-button type="text" :icon="Bell" />
      </el-badge>
      
      <!-- 用户菜单 -->
      <el-dropdown @command="handleUserMenuCommand">
        <div class="user-info">
          <el-avatar :size="32" :src="userInfo?.avatar">
            {{ userInfo?.username?.charAt(0).toUpperCase() }}
          </el-avatar>
          <span class="username">{{ userInfo?.username }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人资料
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 快捷键帮助对话框 -->
    <ShortcutHelp v-model="shortcutHelpVisible" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { ElMessageBox } from 'element-plus'
import {
  Expand,
  Fold,
  Search,
  Bell,
  ArrowDown,
  User,
  Setting,
  SwitchButton,
  ChatDotRound,
  QuestionFilled
} from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import ShortcutHelp from '@/components/common/ShortcutHelp.vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const { sidebarCollapsed } = storeToRefs(appStore)
const { userInfo } = storeToRefs(userStore)

// 搜索关键词
const searchKeyword = ref('')

// 通知数量（模拟）
const notificationCount = ref(3)

// 快捷键帮助对话框
const shortcutHelpVisible = ref(false)

// 面包屑导航
const breadcrumbItems = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title)
  return matched.map(item => ({
    title: item.meta?.title,
    path: item.path
  }))
})

// 切换侧边栏
const toggleSidebar = () => {
  appStore.toggleSidebar()
}

// 打开AI助手
const openAiChat = () => {
  console.log('AI助手按钮被点击')
  try {
    router.push('/ai-chat')
    console.log('路由跳转成功')
  } catch (error) {
    console.error('路由跳转失败:', error)
  }
}

// 显示快捷键帮助
const showShortcutHelp = () => {
  shortcutHelpVisible.value = true
}

// 处理用户菜单命令
const handleUserMenuCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      // 跳转到个人资料页面
      router.push('/profile')
      break
    case 'settings':
      // 跳转到设置页面
      router.push('/settings')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        userStore.logout()
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}
</script>

<style scoped lang="scss">
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
  
  .header-left {
    display: flex;
    align-items: center;
    
    .sidebar-toggle {
      margin-right: 16px;
      font-size: 18px;
    }
    
    .breadcrumb {
      font-size: 14px;
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;

    .ai-chat-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 14px;
      transition: all 0.3s;

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
      }

      .el-icon {
        font-size: 16px;
      }
    }

    .search-input {
      width: 240px;
    }

    .notification-badge {
      cursor: pointer;
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 6px;
      transition: background-color 0.3s;
      
      &:hover {
        background-color: #f5f5f5;
      }
      
      .username {
        font-size: 14px;
        color: #333;
      }
    }
  }
}
</style>
