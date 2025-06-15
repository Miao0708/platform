# 需求管理页面原型设计

## 页面概述

需求管理页面是AI研发辅助平台的核心功能页面，用于管理项目需求的完整生命周期，包括需求录入、解析、分析、跟踪和验证。

## 页面布局

```
┌─────────────────────────────────────────────────────────────────┐
│ 头部导航栏                                                        │
├─────────────────────────────────────────────────────────────────┤
│ 面包屑导航: 首页 > 需求管理                                        │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌──────────────┐ ┌────────────────────────────┐   │
│ │  搜索框     │ │  状态筛选     │ │          操作按钮           │   │
│ └─────────────┘ └──────────────┘ └────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│ 需求列表区域                                                      │
│ ┌───────────────────────────────────────────────────────────────┐ │
│ │ [ID] [标题]              [状态] [优先级] [创建者] [创建时间]      │ │
│ │ ─────────────────────────────────────────────────────────────  │ │
│ │ R001 用户认证系统         进行中  高      张三    2024-01-01    │ │
│ │ R002 AI聊天接口开发       待开始  中      李四    2024-01-02    │ │
│ │ R003 代码审查功能         已完成  高      王五    2024-01-03    │ │
│ └───────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ 分页控件                                                          │
└─────────────────────────────────────────────────────────────────┘

需求详情侧边栏（可展开）
┌──────────────────────────────────────┐
│ 需求详情                               │
│ ─────────────────────────────────────  │
│ 需求ID: R001                          │
│ 标题: 用户认证系统                      │
│ 描述: [详细描述内容]                    │
│ 状态: 进行中                           │
│ 优先级: 高                             │
│ 创建者: 张三                           │
│ 创建时间: 2024-01-01                   │
│ 更新时间: 2024-01-15                   │
│                                        │
│ AI分析结果                             │
│ ─────────────────────────────────────  │
│ • 复杂度评估: 中等                      │
│ • 预估工时: 3-5天                       │
│ • 技术栈建议: Vue3 + FastAPI            │
│ • 依赖需求: R000 基础框架               │
│                                        │
│ 关联信息                               │
│ ─────────────────────────────────────  │
│ • 测试用例: 5个                         │
│ • 代码评审: 2个                         │
│ • 流水线任务: 1个                       │
│                                        │
│ 操作按钮                               │
│ [编辑] [删除] [AI分析] [导出]           │
└──────────────────────────────────────┘
```

## 功能组件

### 1. 搜索和筛选区域

#### 搜索功能
- 支持按需求ID、标题、描述内容搜索
- 实时搜索，支持模糊匹配
- 搜索历史记录

#### 筛选功能
- 状态筛选：全部、待开始、进行中、已完成、已取消
- 优先级筛选：高、中、低
- 创建者筛选：支持多选
- 时间范围筛选：创建时间、更新时间

### 2. 需求列表

#### 列表字段
- 需求ID：系统生成的唯一标识
- 标题：需求的简短描述
- 状态：当前需求的处理状态
- 优先级：需求的重要程度
- 创建者：需求创建人
- 创建时间：需求创建的日期时间
- 操作：查看、编辑、删除等快捷操作

#### 列表功能
- 支持按各字段排序
- 批量操作：批量状态更新、批量删除
- 拖拽排序：调整需求优先级

### 3. 需求详情侧边栏

#### 基本信息
- 完整的需求详情展示
- 支持内联编辑
- 状态变更历史记录

#### AI分析功能
- 需求复杂度分析
- 工时预估
- 技术栈建议
- 依赖关系识别
- 风险评估

#### 关联信息
- 关联的测试用例
- 相关代码评审
- 对应的流水线任务
- 相关文档和附件

## 数据模型

### 需求实体 (Requirement)

```typescript
interface Requirement {
  id: string;                    // 需求ID
  title: string;                 // 需求标题
  description: string;           // 详细描述
  status: RequirementStatus;     // 需求状态
  priority: Priority;            // 优先级
  complexity: ComplexityLevel;   // 复杂度等级
  estimatedHours: number;        // 预估工时
  actualHours?: number;          // 实际工时
  createdBy: string;            // 创建者ID
  assignedTo?: string;          // 分配给
  createdAt: Date;              // 创建时间
  updatedAt: Date;              // 更新时间
  dueDate?: Date;               // 截止时间
  tags: string[];               // 标签
  attachments: Attachment[];     // 附件
  dependencies: string[];        // 依赖需求ID
  aiAnalysis?: AIRequirementAnalysis; // AI分析结果
}

enum RequirementStatus {
  DRAFT = 'draft',               // 草稿
  PENDING = 'pending',           // 待开始
  IN_PROGRESS = 'in_progress',   // 进行中
  REVIEW = 'review',             // 评审中
  COMPLETED = 'completed',       // 已完成
  CANCELLED = 'cancelled'        // 已取消
}

enum Priority {
  LOW = 'low',                   // 低
  MEDIUM = 'medium',             // 中
  HIGH = 'high',                 // 高
  CRITICAL = 'critical'          // 紧急
}

enum ComplexityLevel {
  SIMPLE = 'simple',             // 简单
  MEDIUM = 'medium',             // 中等
  COMPLEX = 'complex',           // 复杂
  VERY_COMPLEX = 'very_complex'  // 非常复杂
}

interface AIRequirementAnalysis {
  complexity: ComplexityLevel;
  estimatedHours: number;
  suggestedTechStack: string[];
  identifiedRisks: Risk[];
  recommendedApproach: string;
  dependencies: string[];
  acceptanceCriteria: string[];
}

interface Risk {
  level: 'low' | 'medium' | 'high';
  description: string;
  mitigation: string;
}
```

### 需求筛选参数

```typescript
interface RequirementFilter {
  search?: string;               // 搜索关键词
  status?: RequirementStatus[];  // 状态筛选
  priority?: Priority[];         // 优先级筛选
  createdBy?: string[];         // 创建者筛选
  assignedTo?: string[];        // 分配给筛选
  dateRange?: {                 // 时间范围
    start: Date;
    end: Date;
  };
  tags?: string[];              // 标签筛选
  complexity?: ComplexityLevel[]; // 复杂度筛选
}

interface RequirementQuery {
  filter: RequirementFilter;
  pagination: {
    page: number;
    pageSize: number;
  };
  sort: {
    field: keyof Requirement;
    order: 'asc' | 'desc';
  };
}
```

## 状态管理

### Store定义

```typescript
interface RequirementState {
  // 需求列表
  requirements: Requirement[];
  total: number;
  loading: boolean;
  
  // 当前选中的需求
  selectedRequirement: Requirement | null;
  detailVisible: boolean;
  
  // 筛选条件
  filter: RequirementFilter;
  pagination: {
    current: number;
    pageSize: number;
  };
  
  // 操作状态
  creating: boolean;
  updating: boolean;
  deleting: boolean;
  analyzing: boolean;
}

interface RequirementActions {
  // 查询操作
  fetchRequirements: (query: RequirementQuery) => Promise<void>;
  searchRequirements: (keyword: string) => Promise<void>;
  
  // CRUD操作
  createRequirement: (data: Partial<Requirement>) => Promise<void>;
  updateRequirement: (id: string, data: Partial<Requirement>) => Promise<void>;
  deleteRequirement: (id: string) => Promise<void>;
  batchUpdateStatus: (ids: string[], status: RequirementStatus) => Promise<void>;
  
  // 详情操作
  selectRequirement: (requirement: Requirement) => void;
  showDetail: (requirement: Requirement) => void;
  hideDetail: () => void;
  
  // AI分析
  analyzeRequirement: (id: string) => Promise<void>;
  
  // 筛选操作
  updateFilter: (filter: Partial<RequirementFilter>) => void;
  resetFilter: () => void;
  
  // 分页操作
  changePage: (page: number) => void;
  changePageSize: (pageSize: number) => void;
}
```

## 页面交互逻辑

### 1. 页面初始化

```typescript
const initializePage = async () => {
  // 加载需求列表
  await fetchRequirements({
    filter: {},
    pagination: { page: 1, pageSize: 20 },
    sort: { field: 'createdAt', order: 'desc' }
  });
  
  // 初始化筛选选项
  await loadFilterOptions();
};
```

### 2. 搜索和筛选

```typescript
// 实时搜索
const handleSearch = debounce(async (keyword: string) => {
  await updateFilter({ search: keyword });
  await refreshRequirements();
}, 300);

// 筛选器变更
const handleFilterChange = async (newFilter: Partial<RequirementFilter>) => {
  await updateFilter(newFilter);
  await refreshRequirements();
};

// 重置筛选
const handleResetFilter = async () => {
  await resetFilter();
  await refreshRequirements();
};
```

### 3. 需求操作

```typescript
// 查看需求详情
const handleViewDetail = (requirement: Requirement) => {
  selectRequirement(requirement);
  showDetail(requirement);
};

// 编辑需求
const handleEdit = async (requirement: Requirement) => {
  // 打开编辑对话框
  showEditDialog(requirement);
};

// 删除需求
const handleDelete = async (id: string) => {
  const confirmed = await showConfirm('确认删除此需求？');
  if (confirmed) {
    await deleteRequirement(id);
    await refreshRequirements();
    showSuccess('需求删除成功');
  }
};

// 批量操作
const handleBatchOperation = async (operation: string, ids: string[]) => {
  switch (operation) {
    case 'updateStatus':
      const status = await selectStatus();
      await batchUpdateStatus(ids, status);
      break;
    case 'delete':
      const confirmed = await showConfirm(`确认删除选中的 ${ids.length} 个需求？`);
      if (confirmed) {
        await Promise.all(ids.map(id => deleteRequirement(id)));
      }
      break;
  }
  await refreshRequirements();
};
```

### 4. AI分析

```typescript
// 触发AI分析
const handleAIAnalysis = async (requirementId: string) => {
  try {
    analyzing.value = true;
    await analyzeRequirement(requirementId);
    showSuccess('AI分析完成');
    
    // 刷新详情显示
    if (selectedRequirement.value?.id === requirementId) {
      await fetchRequirementDetail(requirementId);
    }
  } catch (error) {
    showError('AI分析失败：' + error.message);
  } finally {
    analyzing.value = false;
  }
};
```

### 5. 状态管理集成

```typescript
// 使用 Pinia store
const requirementStore = useRequirementStore();

const {
  requirements,
  total,
  loading,
  selectedRequirement,
  detailVisible,
  filter,
  pagination
} = storeToRefs(requirementStore);

const {
  fetchRequirements,
  createRequirement,
  updateRequirement,
  deleteRequirement,
  selectRequirement,
  showDetail,
  hideDetail,
  analyzeRequirement
} = requirementStore;
```

## 响应式设计

### 桌面端 (≥1200px)
- 三栏布局：筛选区 + 列表区 + 详情侧边栏
- 详情侧边栏可收起/展开
- 列表显示完整字段信息

### 平板端 (768px-1199px)
- 两栏布局：列表区 + 可折叠筛选栏
- 详情以弹窗形式显示
- 列表字段适当简化

### 移动端 (<768px)
- 单栏布局，垂直堆叠
- 筛选条件折叠在顶部
- 卡片式列表展示
- 详情全屏显示

## 性能优化

### 1. 虚拟滚动
```typescript
// 大数据量列表使用虚拟滚动
const virtualListConfig = {
  itemHeight: 60,
  buffer: 10,
  threshold: 100
};
```

### 2. 分页策略
```typescript
// 智能分页，根据屏幕大小调整
const getPageSize = () => {
  const screenHeight = window.innerHeight;
  return Math.floor((screenHeight - 300) / 60); // 每行60px高度
};
```

### 3. 缓存策略
```typescript
// 需求列表缓存
const cacheKey = computed(() => 
  `requirements_${JSON.stringify(filter.value)}_${pagination.value.current}`
);

// 使用LRU缓存最近访问的需求详情
const detailCache = new LRUCache<string, Requirement>({ max: 50 });
```

### 4. 防抖节流
```typescript
// 搜索防抖
const debouncedSearch = debounce(handleSearch, 300);

// 滚动节流
const throttledScroll = throttle(handleScroll, 100);
```

## 权限控制

### 权限定义
```typescript
enum RequirementPermission {
  VIEW = 'requirement:view',
  CREATE = 'requirement:create',
  EDIT = 'requirement:edit',
  DELETE = 'requirement:delete',
  AI_ANALYZE = 'requirement:ai_analyze',
  BATCH_OPERATE = 'requirement:batch_operate'
}
```

### 权限检查
```typescript
// 组件级权限控制
const canEdit = computed(() => 
  hasPermission(RequirementPermission.EDIT) && 
  (selectedRequirement.value?.createdBy === currentUser.value?.id || isAdmin.value)
);

const canDelete = computed(() =>
  hasPermission(RequirementPermission.DELETE) &&
  selectedRequirement.value?.status !== RequirementStatus.COMPLETED
);
```

## 错误处理

### 网络错误
```typescript
const handleNetworkError = (error: any) => {
  if (error.code === 'NETWORK_ERROR') {
    showError('网络连接失败，请检查网络设置');
  } else if (error.status === 403) {
    showError('权限不足，无法执行此操作');
  } else {
    showError('操作失败：' + (error.message || '未知错误'));
  }
};
```

### 数据验证
```typescript
const validateRequirement = (data: Partial<Requirement>): string[] => {
  const errors: string[] = [];
  
  if (!data.title?.trim()) {
    errors.push('需求标题不能为空');
  }
  
  if (data.title && data.title.length > 100) {
    errors.push('需求标题不能超过100个字符');
  }
  
  if (!data.description?.trim()) {
    errors.push('需求描述不能为空');
  }
  
  if (data.dueDate && data.dueDate < new Date()) {
    errors.push('截止时间不能早于当前时间');
  }
  
  return errors;
};
```

## 用户体验优化

### 1. 操作反馈
- 操作按钮显示加载状态
- 成功/失败消息提示
- 进度条显示长时间操作

### 2. 快捷键支持
```typescript
// 键盘快捷键
const keyboardShortcuts = {
  'Ctrl+N': () => showCreateDialog(),     // 新建需求
  'Ctrl+F': () => focusSearchInput(),     // 搜索
  'Delete': () => handleDeleteSelected(), // 删除选中
  'Escape': () => hideDetail()           // 关闭详情
};
```

### 3. 自动保存
```typescript
// 编辑表单自动保存草稿
const autoSave = debounce(async (data: Partial<Requirement>) => {
  await saveDraft(data);
  showInfo('草稿已自动保存');
}, 2000);
```

### 4. 离线支持
```typescript
// Service Worker 缓存关键数据
const offlineSupport = {
  cacheRequirements: true,
  syncOnReconnect: true,
  showOfflineIndicator: true
};
``` 