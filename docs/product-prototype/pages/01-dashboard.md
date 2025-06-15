# 仪表盘页面 (Dashboard)

## 页面概述
仪表盘是用户登录后的主要入口页面，提供系统整体状况的概览信息，包括任务统计、性能指标、最近活动等关键信息。

## 页面布局

### 页面结构
```
┌─────────────────────────────────────────────────────────────┐
│                      顶部导航栏                               │
├─────────────────────────────────────────────────────────────┤
│ 侧边栏 │                  主内容区域                        │
│       │ ┌─────────────────────────────────────────────────┐ │
│       │ │               概览统计卡片区                     │ │
│       │ │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                │ │
│       │ │ │总任务│ │完成率│ │Token│ │活跃 │                │ │
│       │ │ └─────┘ └─────┘ └─────┘ └─────┘                │ │
│       │ └─────────────────────────────────────────────────┘ │
│       │ ┌─────────────────┐ ┌─────────────────────────────┐ │
│       │ │   任务趋势图     │ │     任务状态分布饼图        │ │
│       │ │                │ │                            │ │
│       │ └─────────────────┘ └─────────────────────────────┘ │
│       │ ┌─────────────────────────────────────────────────┐ │
│       │ │               最近任务列表                       │ │
│       │ │                                                │ │
│       │ └─────────────────────────────────────────────────┘ │
│       │ ┌─────────────────┐ ┌─────────────────────────────┐ │
│       │ │   AI模型使用统计 │ │         系统资源监控         │ │
│       │ │                │ │                            │ │
│       │ └─────────────────┘ └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 功能组件详述

### 1. 概览统计卡片
**位置**: 页面顶部
**布局**: 4个并排的统计卡片

#### 1.1 总任务数卡片
```typescript
interface TaskOverviewCard {
  title: "总任务数"
  value: number          // 当前总任务数
  change: number         // 相比昨天的变化
  changeType: 'increase' | 'decrease' | 'stable'
  icon: "task"
  color: "primary"
}
```

#### 1.2 完成率卡片
```typescript
interface CompletionRateCard {
  title: "完成率"
  value: number         // 百分比
  target: number        // 目标完成率
  trend: 'up' | 'down' | 'stable'
  icon: "check-circle"
  color: "success"
}
```

#### 1.3 Token使用统计卡片
```typescript
interface TokenUsageCard {
  title: "Token使用"
  value: number         // 今日已使用Token数
  total: number         // 今日总配额
  percentage: number    // 使用百分比
  icon: "cpu"
  color: "warning"
}
```

#### 1.4 活跃用户卡片
```typescript
interface ActiveUsersCard {
  title: "活跃用户"
  value: number         // 今日活跃用户数
  comparison: number    // 相比昨天
  icon: "users"
  color: "info"
}
```

### 2. 任务趋势图
**位置**: 左侧，统计卡片下方
**类型**: 折线图

```typescript
interface TaskTrendChart {
  title: "最近7天任务趋势"
  xAxis: string[]       // 日期数组
  series: {
    name: "创建任务"
    data: number[]      // 每日创建任务数
    color: "#409EFF"
  } & {
    name: "完成任务"
    data: number[]      // 每日完成任务数
    color: "#67C23A"
  } & {
    name: "失败任务"
    data: number[]      // 每日失败任务数
    color: "#F56C6C"
  }
}
```

### 3. 任务状态分布图
**位置**: 右侧，与趋势图并排
**类型**: 饼图

```typescript
interface TaskStatusDistribution {
  title: "任务状态分布"
  data: Array<{
    name: 'pending' | 'running' | 'completed' | 'failed'
    value: number
    percentage: number
    color: string
  }>
}
```

### 4. 最近任务列表
**位置**: 中部，占据较大区域
**类型**: 表格

```typescript
interface RecentTasksTable {
  title: "最近任务"
  columns: Array<{
    prop: string
    label: string
    width?: string
    formatter?: Function
  }>
  data: RecentTask[]
  pagination: {
    current: number
    pageSize: number
    total: number
  }
  actions: {
    view: Function      // 查看详情
    retry: Function     // 重试任务
    delete: Function    // 删除任务
  }
}
```

### 5. AI模型使用统计
**位置**: 左下角
**类型**: 柱状图

```typescript
interface AIModelUsageChart {
  title: "AI模型使用统计"
  data: Array<{
    modelName: string
    provider: string
    usageCount: number
    successRate: number
    avgResponseTime: number
  }>
}
```

### 6. 系统资源监控
**位置**: 右下角
**类型**: 仪表盘图表

```typescript
interface SystemResourceMonitor {
  title: "系统资源"
  metrics: {
    cpu: {
      usage: number     // CPU使用率
      status: 'normal' | 'warning' | 'danger'
    }
    memory: {
      usage: number     // 内存使用率
      total: string     // 总内存
      used: string      // 已使用内存
    }
    storage: {
      usage: number     // 存储使用率
      available: string // 可用空间
    }
    apiCalls: {
      count: number     // 今日API调用次数
      limit: number     // 调用限制
    }
  }
}
```

## 页面状态管理

### State 定义
```typescript
interface DashboardState {
  // 加载状态
  loading: {
    overview: boolean
    charts: boolean
    tasks: boolean
    resources: boolean
  }
  
  // 统计数据
  overview: {
    totalTasks: number
    completionRate: number
    tokenUsage: number
    activeUsers: number
  }
  
  // 图表数据
  charts: {
    taskTrend: TaskTrendChart
    statusDistribution: TaskStatusDistribution
    modelUsage: AIModelUsageChart
  }
  
  // 任务列表
  recentTasks: {
    list: RecentTask[]
    total: number
    currentPage: number
    pageSize: number
  }
  
  // 系统资源
  systemResources: SystemResourceMonitor
  
  // 刷新控制
  autoRefresh: boolean
  refreshInterval: number
  lastRefreshTime: string
}
```

### Actions 定义
```typescript
interface DashboardActions {
  // 数据获取
  fetchOverviewStats(): Promise<void>
  fetchTaskTrend(days?: number): Promise<void>
  fetchStatusDistribution(): Promise<void>
  fetchRecentTasks(page?: number): Promise<void>
  fetchModelUsage(): Promise<void>
  fetchSystemResources(): Promise<void>
  
  // 刷新控制
  startAutoRefresh(): void
  stopAutoRefresh(): void
  manualRefresh(): Promise<void>
  
  // 任务操作
  retryTask(taskId: string): Promise<void>
  deleteTask(taskId: string): Promise<void>
  viewTaskDetail(taskId: string): void
  
  // 导出功能
  exportReport(type: 'daily' | 'weekly' | 'monthly'): Promise<void>
}
```

## 交互逻辑

### 1. 页面初始化
```typescript
onMounted(() => {
  // 1. 加载概览统计
  fetchOverviewStats()
  
  // 2. 并行加载图表数据
  Promise.all([
    fetchTaskTrend(),
    fetchStatusDistribution(),
    fetchModelUsage(),
    fetchSystemResources()
  ])
  
  // 3. 加载最近任务
  fetchRecentTasks()
  
  // 4. 启动自动刷新
  if (userPreferences.autoRefresh) {
    startAutoRefresh()
  }
})
```

### 2. 自动刷新机制
```typescript
const autoRefreshTimer = ref<NodeJS.Timeout>()

const startAutoRefresh = () => {
  autoRefreshTimer.value = setInterval(() => {
    manualRefresh()
  }, refreshInterval.value)
}

const stopAutoRefresh = () => {
  if (autoRefreshTimer.value) {
    clearInterval(autoRefreshTimer.value)
  }
}
```

### 3. 数据筛选与时间范围选择
```typescript
interface TimeRangeFilter {
  range: '7d' | '30d' | '90d' | 'custom'
  startDate?: string
  endDate?: string
}

const handleTimeRangeChange = (range: TimeRangeFilter) => {
  // 重新获取时间范围内的数据
  fetchTaskTrend(range)
  fetchStatusDistribution(range)
}
```

### 4. 任务操作
```typescript
const handleTaskAction = async (action: string, taskId: string) => {
  switch (action) {
    case 'view':
      router.push(`/tasks/${taskId}`)
      break
    case 'retry':
      await retryTask(taskId)
      ElMessage.success('任务重试成功')
      fetchRecentTasks() // 刷新列表
      break
    case 'delete':
      await ElMessageBox.confirm('确认删除此任务？')
      await deleteTask(taskId)
      ElMessage.success('任务删除成功')
      fetchRecentTasks() // 刷新列表
      break
  }
}
```

## 响应式设计

### 断点定义
```typescript
const breakpoints = {
  xs: '< 768px',    // 手机
  sm: '768px',      // 平板
  md: '992px',      // 小屏幕
  lg: '1200px',     // 中屏幕
  xl: '1920px'      // 大屏幕
}
```

### 响应式布局调整
```typescript
// 小屏幕下的布局调整
const isSmallScreen = computed(() => windowWidth.value < 768)

const layoutConfig = computed(() => {
  if (isSmallScreen.value) {
    return {
      cardCols: 2,        // 统计卡片每行2个
      chartCols: 1,       // 图表单列显示
      hideSystemMonitor: true  // 隐藏系统监控
    }
  }
  return {
    cardCols: 4,        // 统计卡片每行4个
    chartCols: 2,       // 图表双列显示
    hideSystemMonitor: false
  }
})
```

## 权限控制

### 数据访问权限
```typescript
interface DashboardPermissions {
  viewOverview: boolean      // 查看概览统计
  viewTasks: boolean        // 查看任务信息
  viewResources: boolean    // 查看系统资源
  exportReports: boolean    // 导出报告
  manageUsers: boolean      // 管理用户（管理员）
}
```

### 权限检查
```typescript
const checkPermission = (permission: keyof DashboardPermissions) => {
  return userStore.permissions[permission] || false
}

// 组件中使用
<el-card v-if="checkPermission('viewResources')">
  <SystemResourceMonitor />
</el-card>
```

## 性能优化

### 1. 数据缓存
```typescript
// 使用 sessionStorage 缓存数据
const cacheKey = 'dashboard_overview'
const cachedData = sessionStorage.getItem(cacheKey)

if (cachedData && !isExpired(cachedData)) {
  // 使用缓存数据
  overviewData.value = JSON.parse(cachedData)
} else {
  // 重新获取数据
  await fetchOverviewStats()
}
```

### 2. 组件懒加载
```typescript
const SystemResourceMonitor = defineAsyncComponent(() => 
  import('@/components/dashboard/SystemResourceMonitor.vue')
)

const AIModelUsageChart = defineAsyncComponent(() => 
  import('@/components/dashboard/AIModelUsageChart.vue')
)
```

### 3. 防抖处理
```typescript
import { useDebounceFn } from '@/composables/useDebounce'

const debouncedRefresh = useDebounceFn(() => {
  manualRefresh()
}, 1000)
```

## 错误处理

### 1. 加载失败处理
```typescript
const handleLoadError = (error: Error, component: string) => {
  console.error(`Dashboard ${component} load failed:`, error)
  
  // 显示错误提示
  ElNotification.error({
    title: '加载失败',
    message: `${component}数据加载失败，请稍后重试`,
    duration: 3000
  })
  
  // 记录错误日志
  errorLogger.log({
    type: 'dashboard_load_error',
    component,
    error: error.message,
    timestamp: new Date().toISOString()
  })
}
```

### 2. 网络异常处理
```typescript
const handleNetworkError = () => {
  // 停止自动刷新
  stopAutoRefresh()
  
  // 显示离线提示
  ElMessage.warning('网络连接异常，已停止自动刷新')
  
  // 提供手动重试按钮
  showRetryButton.value = true
}
``` 