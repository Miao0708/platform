
### **AI 研发辅助平台 - 前端项目架构设计 (Vue 3)**

#### **一、 技术选型 (Technology Stack)**

1.  **构建工具**: **Vite**
    *   **优势**: 极速的冷启动和热模块更新 (HMR)，基于 ESBuild 和 Rollup，提供了一流的开发体验和优化的生产构建。

2.  **核心框架**: **Vue 3**
    *   **优势**: 采用 Composition API (`<script setup>`)，代码逻辑组织更清晰、复用性更强。性能比 Vue 2 更优。

3.  **UI 组件库**: **Element Plus**
    *   **优势**: 专为 Vue 3 设计，提供丰富、高质量的组件（表单、表格、弹窗、下拉框等），与 PRD 中的 UI 需求高度契合，能极大加速开发。

4.  **路由管理**: **Vue Router 4.x**
    *   **优势**: Vue 官方路由，与 Vue 3 完美集成，支持动态路由、嵌套路由和精细的导航守卫。

5.  **状态管理**: **Pinia**
    *   **优势**: Vue 官方推荐的新一代状态管理库。类型安全、代码简洁、支持模块化 Store，完美契合 Composition API，且没有 Vuex 中繁琐的 Mutations。

6.  **HTTP 请求库**: **Axios**
    *   **优势**: 成熟稳定，支持 Promise，提供请求和响应拦截器（用于统一处理 Token 和错误），易于封装。

7.  **编程语言**: **TypeScript**
    *   **优势**: 提供静态类型检查，增强代码健壮性，提升大型项目的可维护性，并提供更好的编辑器支持（自动补全、类型提示）。

8.  **CSS 方案**: **Tailwind CSS** (可选但推荐) + **Sass/SCSS**
    *   **优势**:
        *   **Tailwind CSS**: 原子化/功能类优先的 CSS 框架，用于快速构建自定义 UI，避免编写大量重复的 CSS。
        *   **Sass/SCSS**: 用于编写全局样式、覆盖组件库样式和定义可复用的 CSS 变量与混合 (mixin)。

#### **二、 项目结构 (Project Structure)**

我们将采用模块化和功能驱动的目录结构，确保代码清晰、易于查找。

```
vue3-ai-dev-platform/
├── public/
├── src/
│   ├── api/                  # API 服务层
│   │   ├── index.ts          # Axios 实例封装与拦截器配置
│   │   ├── git.ts            # Git 配置相关 API
│   │   ├── prompt.ts         # Prompt 模板相关 API
│   │   ├── knowledgeBase.ts  # 知识库相关 API
│   │   └── pipeline.ts       # 流水线 (评审、用例) 相关 API
│   │
│   ├── assets/               # 静态资源 (images, fonts, global styles)
│   │   └── styles/
│   │       └── main.scss     # 全局 SCSS 入口
│   │
│   ├── components/           # 全局可复用组件
│   │   ├── common/           # 基础组件 (如自定义按钮、状态标签)
│   │   ├── layout/           # 页面布局组件 (Header, Sidebar, Main)
│   │   └── pipelines/        # 流水线相关的复用组件 (如任务状态 Badge)
│   │
│   ├── composables/          # 可复用的 Composition API 函数
│   │   ├── usePolling.ts     # 用于轮询任务状态的 Hook
│   │   └── useDebounce.ts    # 防抖 Hook
│   │
│   ├── router/               # 路由配置
│   │   └── index.ts
│   │
│   ├── stores/               # Pinia 状态管理
│   │   ├── user.ts           # 用户认证 Store
│   │   ├── git.ts            # Git 配置 Store
│   │   ├── prompt.ts         # Prompt 模板 Store
│   │   └── task.ts           # 所有任务 (评审、用例) 的通用 Store
│   │
│   ├── types/                # TypeScript 类型定义
│   │   ├── api.ts            # API 请求/响应的类型
│   │   ├── models.ts         # 与后端模型对应的实体类型 (Repo, Prompt, Task)
│   │   └── index.ts          # 类型导出入口
│   │
│   ├── utils/                # 通用工具函数
│   │   ├── crypto.ts         # (如果需要在前端处理加解密，尽管不推荐存敏感信息)
│   │   └── formatter.ts      # 日期、文本格式化函数
│   │
│   ├── views/                # 页面级组件 (路由映射的组件)
│   │   ├── Login.vue
│   │   ├── Dashboard.vue
│   │   ├── configuration/
│   │   │   ├── GitConfig.vue
│   │   │   ├── PromptTemplates.vue
│   │   │   └── KnowledgeBase.vue
│   │   ├── code-review/
│   │   │   ├── CreateReviewTask.vue
│   │   │   ├── ReviewTaskList.vue
│   │   │   └── ReviewReport.vue
│   │   └── test-case/
│   │       ├── CreateCaseTask.vue
│   │       ├── CaseList.vue
│   │       └── CaseManagement.vue
│   │
│   ├── App.vue               # 根组件
│   └── main.ts               # 应用入口文件
│
├── .env.development        # 开发环境变量
├── .env.production         # 生产环境变量
├── package.json
├── tsconfig.json
└── vite.config.ts
```

#### **三、 核心模块设计思路**

1.  **API 服务层 (`src/api/`)**
    *   在 `api/index.ts` 中创建并配置 Axios 实例。
    *   **请求拦截器**: 统一添加 JWT Token 到请求头 (`Authorization: Bearer ...`)。
    *   **响应拦截器**: 统一处理 API 错误（如 401 跳转登录、500 弹出全局错误提示）和数据预处理。
    *   每个业务模块（如 `git.ts`, `prompt.ts`）都基于此实例封装具体的 API 函数，函数的参数和返回值都使用 `src/types/` 中定义的类型进行强类型约束。

    ```typescript
    // src/api/pipeline.ts (示例)
    import request from './index';
    import type { CreateReviewTaskPayload, PipelineTask } from '@/types/models';

    export function createCodeReviewTask(data: CreateReviewTaskPayload): Promise<PipelineTask> {
        return request({
            url: '/code-review/tasks',
            method: 'post',
            data,
        });
    }

    export function getTaskDetails(taskId: string): Promise<PipelineTask> {
        return request.get(`/tasks/${taskId}`);
    }
    ```

2.  **状态管理 (`src/stores/`)**
    *   按功能模块划分 Store，职责清晰。
    *   `user.ts`: 管理用户 token 和用户信息，处理登录、登出逻辑。
    *   `git.ts`: 缓存 Git 仓库列表、全局凭证信息，并提供增删改查的 Action。
    *   `task.ts`: 核心 Store，管理任务列表、单个任务详情。
        *   **Action**: `fetchTasks()`, `createTask()`, `executeTask()`。
        *   **异步处理**: `executeTask` Action 会调用 API，然后启动一个轮询（使用 `usePolling` composable），定时调用 `fetchTaskDetails` Action 来更新任务状态，直到任务完成或失败。

3.  **路由与布局 (`src/router/`, `src/components/layout/`)**
    *   使用嵌套路由实现通用页面布局。
        *   一个顶层路由 `/` 包含 `Layout.vue` 组件。
        *   `Layout.vue` 内部包含 `Header`, `Sidebar` 和一个 `<router-view />`。
        *   所有业务页面（如 Dashboard, GitConfig）都作为此顶层路由的 `children`，这样它们都会共享同一个布局。
    *   在 `router/index.ts` 中配置**导航守卫 (`beforeEach`)**，检查 `userStore` 中是否存在 token，实现登录拦截。

4.  **页面与组件 (`src/views/`, `src/components/`)**
    *   **Views**: "智能"组件，负责业务逻辑、与 Pinia Store 交互、调用 API。例如，`CreateReviewTask.vue` 会从 `gitStore` 获取仓库列表，从 `promptStore` 获取 Prompt 列表，然后组合成表单，提交时调用 `taskStore` 的 Action。
    *   **Components**: "哑"组件，只负责展示和响应用户交互事件。它们通过 `props`接收数据，通过 `emits` 派发事件。例如，一个 `TaskStatusBadge.vue` 组件，接收一个 `status` prop，然后根据状态显示不同颜色和文本的徽章。

#### **四、 关键流程实现示例：执行代码评审任务**

1.  **用户操作**: 在 `ReviewTaskList.vue` 页面，用户点击某条任务的“执行”按钮。
    ```vue
    <!-- ReviewTaskList.vue -->
    <script setup lang="ts">
    import { useTaskStore } from '@/stores/task';
    const taskStore = useTaskStore();

    function handleExecute(taskId: string) {
        // 调用 Store 的 Action
        taskStore.executeTask(taskId);
    }
    </script>
    <template>
      <!-- ... 表格渲染 ... -->
      <el-button @click="handleExecute(task.id)">执行</el-button>
      <!-- ... -->
    </template>
    ```

2.  **Pinia Action**: `taskStore` 接收到调用，执行 `executeTask` Action。
    ```typescript
    // src/stores/task.ts
    import { defineStore } from 'pinia';
    import { executeTask as executeTaskApi, getTaskDetails } from '@/api/pipeline';
    import type { PipelineTask } from '@/types/models';

    export const useTaskStore = defineStore('task', {
        state: () => ({
            tasks: [] as PipelineTask[],
            activeTask: null as PipelineTask | null,
            pollingInterval: null as number | null,
        }),
        actions: {
            async executeTask(taskId: string) {
                try {
                    // 1. 调用 API，通知后端开始执行
                    await executeTaskApi(taskId);
                    
                    // 2. 立即更新本地任务状态为 'QUEUED'
                    const task = this.tasks.find(t => t.id === taskId);
                    if (task) task.status = 'QUEUED';

                    // 3. 开始轮询任务详情
                    this.startPollingTaskStatus(taskId);

                } catch (error) {
                    // 处理错误
                }
            },
            
            startPollingTaskStatus(taskId: string) {
                // 清除之前的轮询
                if (this.pollingInterval) clearInterval(this.pollingInterval);

                this.pollingInterval = setInterval(async () => {
                    const updatedTask = await getTaskDetails(taskId);
                    // 更新列表中的任务
                    const index = this.tasks.findIndex(t => t.id === taskId);
                    if (index !== -1) this.tasks[index] = updatedTask;
                    
                    // 如果任务完成或失败，停止轮询
                    if (['COMPLETED', 'FAILED'].includes(updatedTask.status)) {
                        clearInterval(this.pollingInterval!);
                        this.pollingInterval = null;
                    }
                }, 3000); // 每 3 秒轮询一次
            },
        },
    });
    ```
3.  **UI 响应式更新**:
    *   `ReviewTaskList.vue` 的表格行数据绑定到 `taskStore.tasks`。
    *   当 `executeTask` 和随后的轮询更新了 `taskStore` 中的任务状态时，由于 Pinia 的状态是响应式的，视图会自动更新。
    *   用户会先看到状态变为 `QUEUED`，然后是 `RUNNING`，最终变为 `COMPLETED` 或 `FAILED`，整个过程无需手动刷新页面。
