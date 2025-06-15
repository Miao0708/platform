# 流水线管理页面原型设计

## 页面概述

流水线管理页面用于管理CI/CD流水线，包括流水线配置、执行监控、日志查看、部署管理和自动化构建流程。

## 页面布局

```
┌─────────────────────────────────────────────────────────────────┐
│ 头部导航栏                                                        │
├─────────────────────────────────────────────────────────────────┤
│ 面包屑导航: 首页 > 流水线管理                                      │
├─────────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │ 新建流水线 │ │ 执行记录  │ │ 模板管理  │ │ 环境配置  │ │  统计报告 │ │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ 流水线列表区域                  │  流水线详情/监控区域               │
│ ┌─────────────────────────────┐ │ ┌─────────────────────────────┐ │
│ │ 🔄 user-auth-pipeline       │ │ │ 流水线: user-auth-pipeline   │ │
│ │    ✅ 构建成功 #128          │ │ │ ─────────────────────────────│ │
│ │    ⏰ 2分钟前              │ │ │ 状态: 执行中 🔄              │ │
│ │    📊 main 分支            │ │ │ 分支: main                  │ │
│ │    👤 张三提交              │ │ │ 触发者: 张三                 │ │
│ │    [▶️ 运行] [⚙️ 配置]      │ │ │ 开始时间: 2024-01-15 14:30   │ │
│ │                            │ │ │ 预计耗时: 5分钟              │ │
│ │ 🔄 api-service-pipeline     │ │ │                             │ │
│ │    🔥 构建失败 #89          │ │ │ 📈 阶段进度                  │ │
│ │    ⏰ 10分钟前             │ │ │ ┌───────────────────────────┐ │ │
│ │    📊 develop 分支         │ │ │ │ ✅ 1. 代码检出            │ │ │
│ │    👤 李四提交              │ │ │ │ ✅ 2. 依赖安装            │ │ │
│ │    [▶️ 重试] [📋 日志]      │ │ │ │ 🔄 3. 单元测试  (50%)     │ │ │
│ │                            │ │ │ │ ⏸️ 4. 代码质检            │ │ │
│ │ ┌────────────────────────┐ │ │ │ │ ⏸️ 5. 构建镜像            │ │ │
│ │ │ 筛选器                  │ │ │ │ ⏸️ 6. 部署到测试环境       │ │ │
│ │ │ ☑️ 执行中               │ │ │ └───────────────────────────┘ │ │
│ │ │ ☑️ 成功                 │ │ │                             │ │
│ │ │ ☐ 失败                  │ │ │ 📊 实时日志                  │ │ │
│ │ │ ☐ 等待批准              │ │ │ ┌───────────────────────────┐ │ │
│ │ └────────────────────────┘ │ │ │ │ [14:32:15] 开始单元测试   │ │ │
│ └─────────────────────────────┘ │ │ │ [14:32:20] 运行测试套件1  │ │ │
│                                 │ │ │ [14:32:25] ✅ 用户认证测试 │ │ │
│                                 │ │ │ [14:32:30] ✅ API测试     │ │ │
│                                 │ │ │ [14:32:35] 🔄 前端测试... │ │ │
│                                 │ │ └───────────────────────────┘ │ │
│                                 │ │                             │ │
│                                 │ │ [⏸️ 暂停] [❌ 取消] [📊 详情] │ │
│                                 │ └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 功能组件

### 1. 流水线概览区域
- 状态指示：执行中、成功、失败、等待批准、已取消
- 快速操作：立即运行、重试失败、查看日志、编辑配置、复制流水线

### 2. 流水线列表  
- 流水线名称和状态、最新执行结果和编号
- 执行时间和触发者、关联分支信息、执行统计数据
- 批量操作：批量运行、批量停止、批量删除、导出配置

### 3. 执行监控面板
- 实时状态：当前执行阶段、各阶段执行进度、实时日志输出、资源使用情况
- 阶段管理：阶段依赖关系、阶段执行时间、阶段成功率统计、失败原因分析

## 数据模型

### 流水线实体

```typescript
interface Pipeline {
  id: string;                       // 流水线ID
  name: string;                     // 流水线名称
  description: string;              // 描述
  status: PipelineStatus;           // 状态
  type: PipelineType;               // 类型
  repository: RepositoryInfo;       // 代码仓库信息
  branches: string[];               // 监听的分支
  triggers: PipelineTrigger[];      // 触发条件
  stages: PipelineStage[];          // 执行阶段
  variables: PipelineVariable[];    // 环境变量
  notifications: NotificationRule[]; // 通知规则
  schedule?: ScheduleConfig;        // 定时配置
  permissions: PipelinePermission[]; // 权限配置
  createdBy: string;                // 创建者
  createdAt: Date;                  // 创建时间
  updatedAt: Date;                  // 更新时间
  lastExecution?: PipelineExecution; // 最后执行记录
}

enum PipelineStatus {
  ACTIVE = 'active',                // 活跃
  INACTIVE = 'inactive',            // 非活跃
  DISABLED = 'disabled',            // 已禁用
  ARCHIVED = 'archived'             // 已归档
}

enum PipelineType {
  BUILD = 'build',                  // 构建
  DEPLOY = 'deploy',                // 部署
  TEST = 'test',                    // 测试
  RELEASE = 'release',              // 发布
  CUSTOM = 'custom'                 // 自定义
}

interface PipelineExecution {
  id: string;                       // 执行ID
  pipelineId: string;               // 流水线ID
  number: number;                   // 执行编号
  status: ExecutionStatus;          // 执行状态
  trigger: ExecutionTrigger;        // 触发信息
  branch: string;                   // 执行分支
  commit: CommitInfo;               // 提交信息
  startedAt: Date;                  // 开始时间
  finishedAt?: Date;                // 结束时间
  duration?: number;                // 执行时长(秒)
  stages: StageExecution[];         // 阶段执行记录
  variables: Record<string, string>; // 执行变量
  artifacts: ExecutionArtifact[];   // 执行产物
  logs: ExecutionLog[];             // 执行日志
  createdBy: string;                // 执行者
}

enum ExecutionStatus {
  PENDING = 'pending',              // 等待中
  RUNNING = 'running',              // 执行中
  SUCCESS = 'success',              // 成功
  FAILURE = 'failure',              // 失败
  CANCELLED = 'cancelled',          // 已取消
  SKIPPED = 'skipped',              // 已跳过
  MANUAL = 'manual'                 // 等待手动确认
}
```

## 状态管理

```typescript
interface PipelineState {
  // 流水线列表
  pipelines: Pipeline[];
  total: number;
  loading: boolean;
  
  // 当前流水线
  currentPipeline: Pipeline | null;
  currentExecution: PipelineExecution | null;
  
  // 执行记录
  executions: PipelineExecution[];
  executionHistory: PipelineExecution[];
  
  // 实时监控
  liveExecution: PipelineExecution | null;
  liveLogs: ExecutionLog[];
  logsStreaming: boolean;
  
  // 筛选和排序
  filter: PipelineFilter;
  sort: PipelineSort;
  pagination: PaginationState;
  
  // 操作状态
  creating: boolean;
  running: boolean;
  stopping: boolean;
  deleting: boolean;
}

interface PipelineActions {
  // 查询操作
  fetchPipelines: (filter: PipelineFilter) => Promise<void>;
  fetchPipelineDetail: (id: string) => Promise<void>;
  fetchExecutions: (pipelineId: string) => Promise<void>;
  
  // CRUD操作
  createPipeline: (data: CreatePipelineRequest) => Promise<void>;
  updatePipeline: (id: string, data: UpdatePipelineRequest) => Promise<void>;
  deletePipeline: (id: string) => Promise<void>;
  
  // 执行控制
  runPipeline: (id: string, branch?: string, variables?: Record<string, string>) => Promise<void>;
  stopExecution: (executionId: string) => Promise<void>;
  retryExecution: (executionId: string) => Promise<void>;
  approveExecution: (executionId: string) => Promise<void>;
  
  // 实时监控
  startLogStream: (executionId: string) => void;
  stopLogStream: () => void;
  updateLiveExecution: (execution: PipelineExecution) => void;
  addLiveLog: (log: ExecutionLog) => void;
}
```

## 页面交互逻辑

### 1. 流水线执行控制

```typescript
// 运行流水线
const handleRunPipeline = async (pipelineId: string, options?: RunOptions) => {
  try {
    running.value = true;
    
    const execution = await runPipeline(pipelineId, options?.branch, options?.variables);
    
    // 开始实时监控
    startLiveMonitoring(execution.id);
    
    showSuccess('流水线启动成功');
    
    // 刷新列表
    await fetchPipelines(filter.value);
  } catch (error) {
    showError('启动流水线失败：' + error.message);
  } finally {
    running.value = false;
  }
};

// 停止执行
const handleStopExecution = async (executionId: string) => {
  const confirmed = await showConfirm('确认停止此次执行？');
  
  if (confirmed) {
    try {
      stopping.value = true;
      await stopExecution(executionId);
      showSuccess('流水线已停止');
      
      // 停止日志流
      stopLogStream();
      
      // 刷新状态
      await refreshExecutionStatus();
    } catch (error) {
      showError('停止失败：' + error.message);
    } finally {
      stopping.value = false;
    }
  }
};
```

### 2. 实时监控

```typescript
// 开始实时监控
const startLiveMonitoring = (executionId: string) => {
  // 开始日志流
  startLogStream(executionId);
  
  // 定期更新执行状态
  const updateInterval = setInterval(async () => {
    try {
      const execution = await fetchExecutionDetail(executionId);
      updateLiveExecution(execution);
      
      // 如果执行完成，停止监控
      if (isExecutionFinished(execution.status)) {
        clearInterval(updateInterval);
        stopLogStream();
        showExecutionResult(execution);
      }
    } catch (error) {
      console.error('更新执行状态失败：', error);
    }
  }, 5000); // 每5秒更新一次
};

// WebSocket日志流
const startLogStream = (executionId: string) => {
  const wsUrl = `ws://api/pipelines/executions/${executionId}/logs`;
  const logSocket = new WebSocket(wsUrl);
  
  logSocket.onmessage = (event) => {
    const logEntry = JSON.parse(event.data);
    addLiveLog(logEntry);
    
    // 自动滚动到底部
    scrollLogsToBottom();
  };
  
  logSocket.onclose = () => {
    logsStreaming.value = false;
    // 尝试重连
    setTimeout(() => {
      if (liveExecution.value?.status === ExecutionStatus.RUNNING) {
        startLogStream(executionId);
      }
    }, 3000);
  };
  
  currentLogSocket.value = logSocket;
  logsStreaming.value = true;
};
```

## 响应式设计

### 桌面端 (≥1200px)
- 三栏布局：列表 + 详情 + 监控面板
- 支持拖拽调整面板大小
- 全屏配置编辑器

### 平板端 (768px-1199px)  
- 两栏布局：列表/详情切换 + 监控
- 配置编辑器全屏显示
- 简化操作按钮

### 移动端 (<768px)
- 单栏布局，页面切换
- 卡片式流水线展示
- 简化的监控界面

## 性能优化

### 1. 日志流优化
- 日志缓冲区批量更新UI
- 限制总日志数量避免内存溢出
- 虚拟滚动处理大量日志

### 2. 状态缓存
- 流水线配置缓存
- 执行记录分页缓存
- 定期清理过期缓存

## 安全考虑

### 1. 配置验证
- 检查敏感信息泄漏
- 检查特权容器使用
- 验证镜像安全性

### 2. 权限控制
- 基于角色的操作权限
- 流水线访问控制
- 环境变量保护

## 用户体验优化

### 1. 实时通知
- 执行完成通知
- 需要批准通知
- 失败重试提醒

### 2. 快捷键支持
- Ctrl+R: 运行流水线
- Ctrl+S: 保存配置
- F5: 刷新状态
- Space: 切换详情 