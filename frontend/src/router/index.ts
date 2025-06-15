import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 导入布局组件
const Layout = () => import('@/components/layout/Layout.vue')

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '仪表盘',
          icon: 'Dashboard'
        }
      }
    ]
  },
  {
    path: '/configuration',
    component: Layout,
    redirect: '/configuration/git',
    meta: {
      title: '基础配置',
      icon: 'Setting'
    },
    children: [
      {
        path: 'git',
        name: 'GitConfig',
        component: () => import('@/views/configuration/GitConfig.vue'),
        meta: {
          title: 'Git配置',
          icon: 'Connection'
        }
      },
      {
        path: 'prompts',
        name: 'PromptTemplates',
        component: () => import('@/views/configuration/PromptTemplates.vue'),
        meta: {
          title: 'Prompt模板',
          icon: 'Document'
        }
      },
      {
        path: 'knowledge-base',
        name: 'KnowledgeBase',
        component: () => import('@/views/configuration/KnowledgeBase.vue'),
        meta: {
          title: '知识库',
          icon: 'Collection'
        }
      },
      {
        path: 'ai-models',
        name: 'AIModelConfig',
        component: () => import('@/views/configuration/AIModelConfig.vue'),
        meta: {
          title: 'AI模型配置',
          icon: 'Cpu'
        }
      }
    ]
  },
  {
    path: '/requirements',
    component: Layout,
    redirect: '/requirements/list',
    meta: {
      title: '需求管理',
      icon: 'Document'
    },
    children: [
      {
        path: 'list',
        name: 'RequirementList',
        component: () => import('@/views/requirements/RequirementList.vue'),
        meta: {
          title: '需求列表',
          icon: 'List'
        }
      }
    ]
  },
  {
    path: '/code-diff',
    component: Layout,
    redirect: '/code-diff/tasks',
    meta: {
      title: '代码Diff',
      icon: 'View'
    },
    children: [
      {
        path: 'tasks',
        name: 'DiffTaskList',
        component: () => import('@/views/code-diff/DiffTaskList.vue'),
        meta: {
          title: 'Diff任务',
          icon: 'List'
        }
      }
    ]
  },
  {
    path: '/pipelines',
    component: Layout,
    redirect: '/pipelines/tasks',
    meta: {
      title: '流水线',
      icon: 'Connection'
    },
    children: [
      {
        path: 'tasks',
        name: 'PipelineTaskList',
        component: () => import('@/views/pipelines/PipelineTaskList.vue'),
        meta: {
          title: '流水线任务',
          icon: 'List'
        }
      },
      {
        path: 'requirement-test/:id',
        name: 'RequirementTestResult',
        component: () => import('@/views/pipelines/RequirementTestResult.vue'),
        meta: {
          title: '需求测试结果'
        }
      }
    ]
  },
  {
    path: '/ai-chat',
    component: Layout,
    children: [
      {
        path: '',
        name: 'AIChatInterface',
        component: () => import('@/views/ai-chat/AIChatInterface.vue'),
        meta: {
          title: 'AI助手',
          icon: 'ChatDotRound'
        }
      }
    ]
  },
  {
    path: '/profile',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: {
          title: '个人信息',
          icon: 'User'
        }
      }
    ]
  },
  {
    path: '/test-points',
    name: 'TestPoints',
    component: Layout,
    meta: { title: '测试点管理' },
    children: [
      {
        path: 'list',
        name: 'TestPointList',
        component: () => import('@/views/test-points/TestPointList.vue'),
        meta: { title: '测试点列表' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: {
      title: '页面不存在'
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - AI研发辅助平台`
  }

  // 公开页面列表（不需要登录）
  const publicPages = ['/login', '/register', '/forgot-password']
  const isPublicPage = publicPages.includes(to.path)

  // 检查是否需要登录
  if (!isPublicPage && !userStore.isLoggedIn) {
    console.log('用户未登录，重定向到登录页')
    next('/login')
    return
  }

  // 如果已登录且访问登录页，重定向到首页
  if (to.path === '/login' && userStore.isLoggedIn) {
    console.log('用户已登录，重定向到首页')
    next('/')
    return
  }

  console.log(`路由跳转: ${from.path} -> ${to.path}`)
  next()
})

export default router
