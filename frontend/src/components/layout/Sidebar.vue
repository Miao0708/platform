<template>
  <div class="sidebar-container">
    <!-- Logo -->
    <div class="sidebar-logo">
      <img src="@/assets/logo.svg" alt="Logo" class="logo-image" />
      <span v-show="!sidebarCollapsed" class="logo-text">AI研发助手</span>
    </div>
    
    <!-- 菜单 -->
    <el-menu
      :default-active="activeMenu"
      :collapse="sidebarCollapsed"
      :unique-opened="true"
      router
      background-color="#001529"
      text-color="#fff"
      active-text-color="#1890ff"
      class="sidebar-menu"
    >
      <template v-for="route in menuRoutes" :key="route.path">
        <!-- 单级菜单 -->
        <el-menu-item
          v-if="!route.children || route.children.length === 0"
          :index="route.path"
        >
          <el-icon v-if="route.meta?.icon">
            <component :is="route.meta.icon" />
          </el-icon>
          <template #title>{{ route.meta?.title }}</template>
        </el-menu-item>
        
        <!-- 多级菜单 -->
        <el-sub-menu
          v-else
          :index="route.path"
        >
          <template #title>
            <el-icon v-if="route.meta?.icon">
              <component :is="route.meta.icon" />
            </el-icon>
            <span>{{ route.meta?.title }}</span>
          </template>
          
          <el-menu-item
            v-for="child in route.children"
            :key="child.path"
            :index="child.path"
          >
            <el-icon v-if="child.meta?.icon">
              <component :is="child.meta.icon" />
            </el-icon>
            <template #title>{{ child.meta?.title }}</template>
          </el-menu-item>
        </el-sub-menu>
      </template>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const appStore = useAppStore()
const { sidebarCollapsed } = storeToRefs(appStore)

// 当前激活的菜单
const activeMenu = computed(() => {
  const { path } = route
  return path
})

// 菜单路由配置
const menuRoutes = computed(() => [
  {
    path: '/dashboard',
    meta: {
      title: '仪表盘',
      icon: 'Monitor'
    }
  },
  {
    path: '/configuration',
    meta: {
      title: '基础配置',
      icon: 'Setting'
    },
    children: [
      {
        path: '/configuration/git',
        meta: {
          title: 'Git配置',
          icon: 'Connection'
        }
      },
      {
        path: '/configuration/prompts',
        meta: {
          title: 'Prompt模板',
          icon: 'Document'
        }
      },
      {
        path: '/configuration/knowledge-base',
        meta: {
          title: '知识库',
          icon: 'Collection'
        }
      },
      {
        path: '/configuration/ai-models',
        meta: {
          title: 'AI模型配置',
          icon: 'Cpu'
        }
      }
    ]
  },
  {
    path: '/ai-chat',
    meta: {
      title: 'AI助手',
      icon: 'ChatDotRound'
    }
  },
  {
    path: '/requirements',
    meta: {
      title: '需求管理',
      icon: 'Document'
    },
    children: [
      {
        path: '/requirements/documents',
        meta: {
          title: '需求文档管理',
          icon: 'List'
        }
      },
      {
        path: '/requirements/test-analysis',
        meta: {
          title: '需求测试分析',
          icon: 'ChatDotRound'
        }
      }
    ]
  },
  {
    path: '/code-diff',
    meta: {
      title: '代码Diff',
      icon: 'View'
    },
    children: [
      {
        path: '/code-diff/tasks',
        meta: {
          title: 'Diff任务',
          icon: 'List'
        }
      }
    ]
  },
  {
    path: '/pipelines',
    meta: {
      title: '流水线',
      icon: 'Connection'
    },
    children: [
      {
        path: '/pipelines/tasks',
        meta: {
          title: '流水线任务',
          icon: 'List'
        }
      }
    ]
  },
  {
    path: '/test-points',
    meta: {
      title: '测试点管理',
      icon: 'CircleCheck'
    },
    children: [
      {
        path: '/test-points/list',
        meta: {
          title: '测试点列表',
          icon: 'List'
        }
      }
    ]
  }
])
</script>

<style scoped lang="scss">
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .sidebar-logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 16px;
    border-bottom: 1px solid #1f2937;
    
    .logo-image {
      width: 32px;
      height: 32px;
    }
    
    .logo-text {
      margin-left: 12px;
      font-size: 16px;
      font-weight: 600;
      color: #fff;
      white-space: nowrap;
    }
  }
  
  .sidebar-menu {
    flex: 1;
    border: none;

    :deep(.el-menu-item) {
      color: #d1d5db !important;

      &.is-active {
        background-color: #1890ff !important;
        color: #ffffff !important;

        .el-icon {
          color: #ffffff !important;
        }
      }

      &:hover:not(.is-active) {
        background-color: #1f2937 !important;
        color: #ffffff !important;

        .el-icon {
          color: #ffffff !important;
        }
      }

      .el-icon {
        color: #d1d5db !important;
      }
    }

    :deep(.el-sub-menu__title) {
      color: #d1d5db !important;

      &:hover {
        background-color: #1f2937 !important;
        color: #ffffff !important;

        .el-icon {
          color: #ffffff !important;
        }
      }

      .el-icon {
        color: #d1d5db !important;
      }
    }

    :deep(.el-sub-menu .el-menu-item) {
      color: #9ca3af !important;

      &.is-active {
        background-color: #1890ff !important;
        color: #ffffff !important;
      }

      &:hover:not(.is-active) {
        background-color: #374151 !important;
        color: #ffffff !important;
      }
    }
  }
}
</style>
