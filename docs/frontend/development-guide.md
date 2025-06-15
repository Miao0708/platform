# 前端开发指南

## 📋 项目概述

基于 Vue 3 + TypeScript + Element Plus 的 AI 研发辅助平台前端项目。

## 🛠️ 技术栈

- **框架**: Vue 3.5.13 (Composition API)
- **构建工具**: Vite 6.2.4
- **语言**: TypeScript
- **UI 组件库**: Element Plus 2.10.1
- **图标**: @element-plus/icons-vue 2.3.1
- **状态管理**: Pinia 3.0.3
- **路由**: Vue Router 4.5.1
- **HTTP 客户端**: Axios 1.9.0
- **样式**: Sass 1.89.2
- **Markdown 编辑器**: md-editor-v3 5.6.1

## 📁 项目结构

```
frontend/
├── public/                    # 静态资源
├── src/
│   ├── api/                  # API 接口定义
│   ├── assets/              # 资源文件
│   │   └── styles/          # 样式文件
│   ├── components/          # 组件
│   │   ├── common/          # 通用组件
│   │   ├── icons/           # 图标组件
│   │   └── layout/          # 布局组件
│   ├── composables/         # 组合式函数
│   ├── router/              # 路由配置
│   ├── stores/              # Pinia 状态管理
│   ├── types/               # TypeScript 类型定义
│   ├── utils/               # 工具函数
│   ├── views/               # 页面组件
│   │   ├── ai-chat/         # AI 对话模块
│   │   ├── code-diff/       # 代码差异模块
│   │   ├── code-review/     # 代码评审模块
│   │   ├── configuration/   # 配置管理模块
│   │   ├── pipelines/       # 流水线模块
│   │   ├── requirements/    # 需求管理模块
│   │   ├── test-case/       # 测试用例模块
│   │   └── test-points/     # 测试点模块
│   ├── App.vue              # 根组件
│   └── main.ts              # 入口文件
├── index.html               # HTML 模板
├── package.json             # 依赖配置
├── tsconfig.json            # TypeScript 配置
├── vite.config.js           # Vite 配置
└── jsconfig.json            # JS 配置
```

## 🚀 开发环境搭建

### 环境要求
- Node.js >= 18.0.0
- npm >= 8.0.0

### 安装依赖
```bash
cd frontend
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 预览生产构建
```bash
npm run preview
```

## 📝 开发规范

### 代码风格
- 使用 TypeScript 严格模式
- 组件名使用 PascalCase
- 文件名使用 kebab-case
- 变量和函数名使用 camelCase
- 常量使用 UPPER_SNAKE_CASE

### 组件开发规范
1. **组件结构**
   ```vue
   <template>
     <!-- 模板内容 -->
   </template>

   <script setup lang="ts">
   // 组合式 API 逻辑
   </script>

   <style lang="scss" scoped>
   /* 样式内容 */
   </style>
   ```

2. **Props 定义**
   ```typescript
   interface Props {
     title: string
     data?: any[]
     loading?: boolean
   }
   
   const props = withDefaults(defineProps<Props>(), {
     data: () => [],
     loading: false
   })
   ```

3. **事件定义**
   ```typescript
   interface Emits {
     (e: 'update', value: string): void
     (e: 'submit', data: any): void
   }
   
   const emit = defineEmits<Emits>()
   ```

### API 调用规范
1. **API 接口定义**
   ```typescript
   // src/api/user.ts
   import request from '@/utils/request'
   import type { User, CreateUserDto } from '@/types/user'

   export const userApi = {
     getUsers: (): Promise<User[]> => 
       request.get('/api/v1/users'),
     
     createUser: (data: CreateUserDto): Promise<User> => 
       request.post('/api/v1/users', data)
   }
   ```

2. **错误处理**
   ```typescript
   try {
     const users = await userApi.getUsers()
     // 处理成功响应
   } catch (error) {
     console.error('获取用户列表失败:', error)
     ElMessage.error('获取用户列表失败')
   }
   ```

### 状态管理 (Pinia)
```typescript
// src/stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(null)
  const token = ref<string>('')
  
  const isLoggedIn = computed(() => !!token.value)
  
  const login = async (credentials: LoginDto) => {
    // 登录逻辑
  }
  
  const logout = () => {
    currentUser.value = null
    token.value = ''
  }
  
  return {
    currentUser,
    token,
    isLoggedIn,
    login,
    logout
  }
})
```

### 路由配置
```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue')
    },
    {
      path: '/ai-chat',
      name: 'AIChat',
      component: () => import('@/views/ai-chat/index.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

## 🎨 样式开发指南

### 全局样式结构
```scss
// src/assets/styles/main.scss
@import './variables';
@import './mixins';
@import './base';
@import './components';
```

### CSS 变量定义
```scss
// src/assets/styles/_variables.scss
:root {
  --color-primary: #409eff;
  --color-success: #67c23a;
  --color-warning: #e6a23c;
  --color-danger: #f56c6c;
  --color-info: #909399;
  
  --font-size-base: 14px;
  --border-radius-base: 4px;
  --spacing-base: 16px;
}
```

### 响应式设计
```scss
// 断点定义
$breakpoints: (
  xs: 0,
  sm: 576px,
  md: 768px,
  lg: 992px,
  xl: 1200px,
  xxl: 1600px
);

// 媒体查询 mixin
@mixin respond-to($breakpoint) {
  @media (min-width: map-get($breakpoints, $breakpoint)) {
    @content;
  }
}
```

## 🧪 测试

### 单元测试
```bash
# 运行测试
npm run test

# 运行测试并生成覆盖率报告
npm run test:coverage
```

### E2E 测试
```bash
# 运行端到端测试
npm run test:e2e
```

## 📦 构建和部署

### 环境变量配置
```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=AI研发辅助平台（开发环境）

# .env.production
VITE_API_BASE_URL=https://api.example.com
VITE_APP_TITLE=AI研发辅助平台
```

### 构建优化
- 代码分割
- Tree shaking
- 资源压缩
- CDN 资源优化

## 🔧 开发工具配置

### VS Code 推荐插件
- Vue Language Features (Volar)
- TypeScript Vue Plugin (Volar)
- ESLint
- Prettier
- Auto Rename Tag
- Bracket Pair Colorizer

### 调试配置
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/src"
    }
  ]
}
```

## 📋 常见问题

### 1. 依赖安装问题
如果遇到依赖安装失败，尝试清除缓存：
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### 2. TypeScript 类型错误
确保所有组件和函数都有正确的类型定义，使用 `any` 类型时要谨慎。

### 3. 样式问题
- 使用 scoped 样式避免全局污染
- 深度选择器使用 `:deep()` 语法
- 组件库样式覆盖使用正确的选择器权重

### 4. 性能优化
- 使用 `v-memo` 指令优化列表渲染
- 合理使用 `computed` 和 `watch`
- 大型组件考虑懒加载

## 📚 学习资源

- [Vue 3 官方文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Pinia 状态管理](https://pinia.vuejs.org/)
- [Vite 构建工具](https://vitejs.dev/)
- [TypeScript 手册](https://www.typescriptlang.org/docs/) 