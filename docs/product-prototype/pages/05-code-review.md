# 代码评审页面原型设计

## 页面概述

代码评审页面提供全面的代码审查功能，支持多人协作评审、AI辅助分析、评审流程管理和代码质量检查。

## 页面布局

```
┌─────────────────────────────────────────────────────────────────┐
│ 头部导航栏                                                        │
├─────────────────────────────────────────────────────────────────┤
│ 面包屑导航: 首页 > 代码评审                                        │
├─────────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│ │  新建评审  │ │  我的评审  │ │  待审核   │ │  已完成   │ │   设置   │ │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ 评审列表区域                    │  评审详情区域                   │
│ ┌─────────────────────────────┐ │ ┌─────────────────────────────┐ │
│ │ 📝 PR-001 用户认证功能改进   │ │ │ 评审详情: PR-001            │ │
│ │    张三 → main             │ │ │ ─────────────────────────────│ │
│ │    ⏰ 2小时前              │ │ │ 标题: 用户认证功能改进        │ │
│ │    👥 3人参与              │ │ │ 分支: feature/auth → main    │ │
│ │    ✅ 2个批准              │ │ │ 作者: 张三                   │ │
│ │    ⚠️ 1个问题              │ │ │ 创建时间: 2024-01-15         │ │
│ │                            │ │ │                             │ │
│ │ 📝 PR-002 API接口优化       │ │ │ 描述: 优化用户认证流程，      │ │
│ │    李四 → main             │ │ │ 增强安全性和用户体验...       │ │
│ │    ⏰ 5小时前              │ │ │                             │ │
│ │    👥 2人参与              │ │ │ 📊 AI分析报告               │ │
│ │    🔄 等待评审             │ │ │ • 代码质量: 良好 ✅          │ │
│ │                            │ │ │ • 安全性: 已通过 ✅          │ │
│ │ 📝 PR-003 前端组件重构      │ │ │ • 性能影响: 无影响 ⚪       │ │
│ │    王五 → develop          │ │ │ • 测试覆盖: 85% ⚠️          │ │
│ │    ⏰ 1天前               │ │ │                             │ │
│ │    👥 1人参与              │ │ │ 🗂️  文件变更 (5个文件)        │ │
│ │    ❌ 1个拒绝              │ │ │ 📄 src/auth/LoginForm.vue   │ │
│ │                            │ │ │ 📄 src/services/AuthService │ │
│ │ ┌────────────────────────┐ │ │ │ 📄 src/utils/validators.ts │ │
│ │ │ 筛选器                  │ │ │ 📄 tests/auth.spec.ts      │ │
│ │ │ ☑️ 待我评审             │ │ │ 📄 docs/api.md             │ │
│ │ │ ☐ 我创建的              │ │ │                             │ │
│ │ │ ☐ 已批准                │ │ │ 📝 评审意见 (3条)            │ │
│ │ │ ☐ 需要修改              │ │ │ ─────────────────────────────│ │
│ │ └────────────────────────┘ │ │ │ [查看代码] [添加评论]        │ │
│ └─────────────────────────────┘ │ └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ 代码审查区域（全屏显示时）                                         │
│ ┌───────────────────────────────────────────────────────────────┐ │
│ │ 文件: src/auth/LoginForm.vue    [并排视图] [统一视图] [AI建议]   │ │
│ │ ───────────────────────────────────────────────────────────── │ │
│ │ 原始代码                    │     修改后代码                   │ │
│ │ ─────────────────────────── │ ─────────────────────────────── │ │
│ │  1  <template>             │  1  <template>                  │ │
│ │  2    <form @submit="      │  2    <form @submit.prevent="   │ │
│ │  3      handleLogin">      │  3      handleLogin">           │ │
│ │  4      <input             │  4      <input                  │ │
│ │  5        v-model="form.   │  5        v-model="form.       │ │
│ │ 💬 李四: 建议添加防抖处理     │ 💬 李四: 已改进,添加了prevent │ │
│ │     ⏰ 2小时前             │     ⏰ 1小时前                  │ │
│ │     [回复] [已解决]         │     [回复] [已解决]             │ │
│ └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 功能组件

### 1. 评审概览区域

#### 状态标签
- 待评审：新提交的评审请求
- 进行中：正在评审过程中
- 需要修改：发现问题，需要修改
- 已批准：评审通过
- 已合并：代码已合并到目标分支

#### 筛选功能
- 按状态筛选
- 按评审者筛选
- 按创建者筛选
- 按时间范围筛选
- 按优先级筛选

### 2. 评审列表

#### 列表信息
- 评审标题和描述
- 源分支 → 目标分支
- 创建者和时间
- 参与评审人数
- 评审状态和进度
- AI分析摘要

#### 快速操作
- 快速批准/拒绝
- 添加评审者
- 设置优先级
- 标记重要

### 3. 评审详情面板

#### 基本信息
- 完整的PR描述
- 分支信息和提交历史
- 文件变更统计
- 评审者列表和状态

#### AI分析摘要
- 代码质量评分
- 安全性检查结果
- 性能影响分析
- 测试覆盖率报告

### 4. 代码审查视图

#### 文件差异显示
- 并排对比模式
- 统一差异模式
- 语法高亮
- 折叠/展开代码块

#### 评论系统
- 行级评论
- 文件级评论
- 评论回复和讨论
- 评论状态管理

#### AI辅助建议
- 代码改进建议
- 潜在问题识别
- 最佳实践提醒
- 安全漏洞检测

## 数据模型

### 代码评审实体

```typescript
interface CodeReview {
  id: string;                       // 评审ID
  title: string;                    // 评审标题
  description: string;              // 详细描述
  status: ReviewStatus;             // 评审状态
  priority: Priority;               // 优先级
  sourceBranch: string;             // 源分支
  targetBranch: string;             // 目标分支
  author: string;                   // 创建者ID
  reviewers: ReviewerAssignment[];  // 评审者列表
  files: ReviewFile[];              // 文件变更列表
  comments: ReviewComment[];        // 评论列表
  commits: CommitInfo[];            // 提交信息
  aiAnalysis?: AIReviewAnalysis;    // AI分析结果
  createdAt: Date;                  // 创建时间
  updatedAt: Date;                  // 更新时间
  deadline?: Date;                  // 截止时间
  mergedAt?: Date;                  // 合并时间
  mergedBy?: string;                // 合并者
  labels: string[];                 // 标签
  linkedIssues: string[];           // 关联问题
}

enum ReviewStatus {
  DRAFT = 'draft',                  // 草稿
  PENDING = 'pending',              // 待评审
  IN_PROGRESS = 'in_progress',      // 评审中
  CHANGES_REQUESTED = 'changes_requested', // 需要修改
  APPROVED = 'approved',            // 已批准
  MERGED = 'merged',                // 已合并
  CLOSED = 'closed'                 // 已关闭
}

enum Priority {
  LOW = 'low',                      // 低
  MEDIUM = 'medium',                // 中
  HIGH = 'high',                    // 高
  URGENT = 'urgent'                 // 紧急
}

interface ReviewerAssignment {
  userId: string;                   // 评审者ID
  role: ReviewerRole;               // 评审角色
  status: ReviewerStatus;           // 评审状态
  assignedAt: Date;                 // 分配时间
  reviewedAt?: Date;                // 评审时间
  decision?: ReviewDecision;        // 评审决定
  comments: string;                 // 评审意见
}

enum ReviewerRole {
  REQUIRED = 'required',            // 必须评审
  OPTIONAL = 'optional',            // 可选评审
  APPROVER = 'approver'             // 最终批准者
}

enum ReviewerStatus {
  PENDING = 'pending',              // 待评审
  IN_PROGRESS = 'in_progress',      // 评审中
  COMPLETED = 'completed'           // 已完成
}

enum ReviewDecision {
  APPROVE = 'approve',              // 批准
  REQUEST_CHANGES = 'request_changes', // 请求修改
  COMMENT = 'comment'               // 仅评论
}

interface ReviewFile {
  path: string;                     // 文件路径
  status: FileChangeStatus;         // 变更状态
  additions: number;                // 新增行数
  deletions: number;                // 删除行数
  changes: DiffHunk[];              // 差异块
  language: string;                 // 编程语言
  originalContent?: string;         // 原始内容
  modifiedContent?: string;         // 修改后内容
  comments: FileComment[];          // 文件评论
}

enum FileChangeStatus {
  ADDED = 'added',                  // 新增
  MODIFIED = 'modified',            // 修改
  DELETED = 'deleted',              // 删除
  RENAMED = 'renamed'               // 重命名
}

interface ReviewComment {
  id: string;                       // 评论ID
  type: CommentType;                // 评论类型
  content: string;                  // 评论内容
  author: string;                   // 作者ID
  createdAt: Date;                  // 创建时间
  updatedAt?: Date;                 // 更新时间
  file?: string;                    // 关联文件
  line?: number;                    // 关联行号
  resolved: boolean;                // 是否已解决
  replies: ReplyComment[];          // 回复列表
  reactions: CommentReaction[];     // 反应表情
}

enum CommentType {
  GENERAL = 'general',              // 普通评论
  ISSUE = 'issue',                  // 问题
  SUGGESTION = 'suggestion',        // 建议
  NITPICK = 'nitpick',             // 小问题
  BLOCKING = 'blocking'             // 阻塞问题
}

interface ReplyComment {
  id: string;
  content: string;
  author: string;
  createdAt: Date;
  reactions: CommentReaction[];
}

interface CommentReaction {
  type: 'thumbs_up' | 'thumbs_down' | 'laugh' | 'heart' | 'confused';
  users: string[];
}

interface AIReviewAnalysis {
  codeQuality: CodeQualityScore;
  securityAnalysis: SecurityAnalysis;
  performanceAnalysis: PerformanceAnalysis;
  testCoverage: TestCoverageReport;
  suggestions: AISuggestion[];
  issues: AIIssue[];
  complexity: ComplexityAnalysis;
  maintainability: MaintainabilityScore;
}

interface CodeQualityScore {
  overall: number;                  // 总体评分 0-100
  factors: {
    readability: number;
    consistency: number;
    documentation: number;
    bestPractices: number;
  };
  improvements: string[];
}

interface SecurityAnalysis {
  score: number;                    // 安全评分
  vulnerabilities: SecurityVulnerability[];
  recommendations: string[];
}

interface SecurityVulnerability {
  severity: 'low' | 'medium' | 'high' | 'critical';
  type: string;
  description: string;
  file: string;
  line: number;
  fix: string;
}

interface PerformanceAnalysis {
  impact: 'positive' | 'negative' | 'neutral';
  issues: PerformanceIssue[];
  suggestions: string[];
}

interface PerformanceIssue {
  type: string;
  description: string;
  file: string;
  line: number;
  impact: 'low' | 'medium' | 'high';
}

interface TestCoverageReport {
  current: number;                  // 当前覆盖率
  change: number;                   // 变化值
  missingTests: string[];           // 缺失的测试
  recommendations: string[];
}

interface AISuggestion {
  type: 'improvement' | 'optimization' | 'refactoring';
  title: string;
  description: string;
  file: string;
  line?: number;
  priority: 'low' | 'medium' | 'high';
  example?: string;
}

interface AIIssue {
  severity: 'error' | 'warning' | 'info';
  category: string;
  message: string;
  file: string;
  line: number;
  rule: string;
  fix?: string;
}
```

### 评审流程配置

```typescript
interface ReviewWorkflow {
  id: string;
  name: string;
  rules: ReviewRule[];
  approvalPolicy: ApprovalPolicy;
  branchProtection: BranchProtectionRule[];
  automations: ReviewAutomation[];
}

interface ReviewRule {
  id: string;
  name: string;
  condition: RuleCondition;
  action: RuleAction;
  enabled: boolean;
}

interface RuleCondition {
  type: 'file_pattern' | 'branch_pattern' | 'author' | 'size';
  pattern: string;
  operator: 'equals' | 'contains' | 'matches' | 'greater_than';
  value: any;
}

interface RuleAction {
  type: 'require_reviewers' | 'auto_assign' | 'block_merge' | 'notify';
  parameters: Record<string, any>;
}

interface ApprovalPolicy {
  minimumApprovals: number;
  requireCodeOwnerApproval: boolean;
  dismissStaleApprovals: boolean;
  requireUpToDateBranch: boolean;
  allowSelfApproval: boolean;
}

interface BranchProtectionRule {
  branch: string;
  enforceAdmins: boolean;
  requiredStatusChecks: string[];
  requirePullRequestReviews: boolean;
  dismissalRestrictions: string[];
}

interface ReviewAutomation {
  trigger: 'pr_created' | 'pr_updated' | 'review_submitted';
  condition: AutomationCondition;
  action: AutomationAction;
}
```

## 状态管理

### Store定义

```typescript
interface CodeReviewState {
  // 评审列表
  reviews: CodeReview[];
  total: number;
  loading: boolean;
  
  // 当前评审
  currentReview: CodeReview | null;
  currentFile: string | null;
  
  // 视图状态
  viewMode: 'list' | 'detail' | 'code';
  diffViewMode: 'split' | 'unified';
  showResolved: boolean;
  
  // 筛选和排序
  filter: ReviewFilter;
  sort: ReviewSort;
  pagination: PaginationState;
  
  // 评论系统
  comments: ReviewComment[];
  newComment: string;
  commentMode: CommentMode;
  
  // AI分析
  aiAnalysisVisible: boolean;
  analyzing: boolean;
  
  // 操作状态
  submitting: boolean;
  approving: boolean;
  merging: boolean;
}

interface CodeReviewActions {
  // 查询操作
  fetchReviews: (filter: ReviewFilter) => Promise<void>;
  fetchReviewDetail: (id: string) => Promise<void>;
  searchReviews: (keyword: string) => Promise<void>;
  
  // CRUD操作
  createReview: (data: CreateReviewRequest) => Promise<void>;
  updateReview: (id: string, data: UpdateReviewRequest) => Promise<void>;
  deleteReview: (id: string) => Promise<void>;
  
  // 评审操作
  submitReview: (reviewId: string, decision: ReviewDecision, comments: string) => Promise<void>;
  approveReview: (reviewId: string, comments?: string) => Promise<void>;
  requestChanges: (reviewId: string, comments: string) => Promise<void>;
  mergeReview: (reviewId: string, mergeType: MergeType) => Promise<void>;
  
  // 评审者管理
  addReviewer: (reviewId: string, userId: string, role: ReviewerRole) => Promise<void>;
  removeReviewer: (reviewId: string, userId: string) => Promise<void>;
  updateReviewerRole: (reviewId: string, userId: string, role: ReviewerRole) => Promise<void>;
  
  // 评论操作
  addComment: (reviewId: string, comment: CreateCommentRequest) => Promise<void>;
  replyComment: (commentId: string, content: string) => Promise<void>;
  editComment: (commentId: string, content: string) => Promise<void>;
  deleteComment: (commentId: string) => Promise<void>;
  resolveComment: (commentId: string) => Promise<void>;
  addReaction: (commentId: string, reaction: string) => Promise<void>;
  
  // 文件操作
  selectFile: (filePath: string) => void;
  navigateToNextFile: () => void;
  navigateToPrevFile: () => void;
  
  // 视图控制
  setViewMode: (mode: 'list' | 'detail' | 'code') => void;
  setDiffViewMode: (mode: 'split' | 'unified') => void;
  toggleResolvedComments: () => void;
  
  // AI分析
  runAIAnalysis: (reviewId: string) => Promise<void>;
  toggleAIAnalysisPanel: () => void;
  
  // 筛选和排序
  updateFilter: (filter: Partial<ReviewFilter>) => void;
  updateSort: (sort: ReviewSort) => void;
  resetFilter: () => void;
}

interface ReviewFilter {
  status?: ReviewStatus[];
  author?: string[];
  reviewer?: string[];
  assignee?: string[];
  priority?: Priority[];
  labels?: string[];
  dateRange?: DateRange;
  search?: string;
}

interface ReviewSort {
  field: 'createdAt' | 'updatedAt' | 'priority' | 'status' | 'title';
  order: 'asc' | 'desc';
}

enum CommentMode {
  NORMAL = 'normal',
  SUGGESTION = 'suggestion',
  ISSUE = 'issue'
}

enum MergeType {
  MERGE = 'merge',
  SQUASH = 'squash',
  REBASE = 'rebase'
}
```

## 页面交互逻辑

### 1. 评审列表管理

```typescript
// 初始化评审列表
const initializeReviews = async () => {
  loading.value = true;
  try {
    await fetchReviews({
      status: [ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS],
      assignee: [currentUser.value.id]
    });
  } catch (error) {
    showError('加载评审列表失败：' + error.message);
  } finally {
    loading.value = false;
  }
};

// 筛选器变更
const handleFilterChange = async (newFilter: Partial<ReviewFilter>) => {
  updateFilter(newFilter);
  await fetchReviews(filter.value);
};

// 评审选择
const handleReviewSelect = async (review: CodeReview) => {
  currentReview.value = review;
  setViewMode('detail');
  
  // 加载详细信息
  await fetchReviewDetail(review.id);
  
  // 选择第一个文件
  if (review.files.length > 0) {
    selectFile(review.files[0].path);
  }
};
```

### 2. 评审操作流程

```typescript
// 提交评审决定
const handleSubmitReview = async (decision: ReviewDecision, comments: string) => {
  if (!currentReview.value) return;
  
  try {
    submitting.value = true;
    await submitReview(currentReview.value.id, decision, comments);
    
    // 刷新评审状态
    await fetchReviewDetail(currentReview.value.id);
    
    showSuccess(`评审${getDecisionText(decision)}成功`);
    
    // 如果是批准，询问是否合并
    if (decision === ReviewDecision.APPROVE && canMerge.value) {
      const shouldMerge = await showConfirm('是否立即合并此代码？');
      if (shouldMerge) {
        await handleMerge();
      }
    }
  } catch (error) {
    showError('提交评审失败：' + error.message);
  } finally {
    submitting.value = false;
  }
};

// 快速批准
const handleQuickApprove = async (reviewId: string) => {
  try {
    await approveReview(reviewId, '快速批准');
    showSuccess('评审批准成功');
    await fetchReviews(filter.value);
  } catch (error) {
    showError('批准失败：' + error.message);
  }
};

// 合并代码
const handleMerge = async (mergeType: MergeType = MergeType.MERGE) => {
  if (!currentReview.value) return;
  
  const confirmed = await showConfirm(
    `确认将 ${currentReview.value.sourceBranch} 合并到 ${currentReview.value.targetBranch}？`
  );
  
  if (confirmed) {
    try {
      merging.value = true;
      await mergeReview(currentReview.value.id, mergeType);
      showSuccess('代码合并成功');
      
      // 返回列表页面
      setViewMode('list');
      await fetchReviews(filter.value);
    } catch (error) {
      showError('合并失败：' + error.message);
    } finally {
      merging.value = false;
    }
  }
};
```

### 3. 评论系统交互

```typescript
// 添加行级评论
const handleAddLineComment = async (file: string, line: number, content: string) => {
  if (!currentReview.value) return;
  
  try {
    await addComment(currentReview.value.id, {
      type: CommentType.GENERAL,
      content,
      file,
      line
    });
    
    // 清空输入框
    newComment.value = '';
    
    // 刷新评论列表
    await fetchReviewDetail(currentReview.value.id);
    
    showSuccess('评论添加成功');
  } catch (error) {
    showError('添加评论失败：' + error.message);
  }
};

// 回复评论
const handleReplyComment = async (commentId: string, content: string) => {
  try {
    await replyComment(commentId, content);
    showSuccess('回复成功');
    
    // 刷新评论
    if (currentReview.value) {
      await fetchReviewDetail(currentReview.value.id);
    }
  } catch (error) {
    showError('回复失败：' + error.message);
  }
};
```

### 4. AI分析集成

```typescript
// 触发AI分析
const handleAIAnalysis = async () => {
  if (!currentReview.value) return;
  
  try {
    analyzing.value = true;
    showProgress('AI正在分析代码评审...');
    
    await runAIAnalysis(currentReview.value.id);
    
    // 显示分析结果
    aiAnalysisVisible.value = true;
    
    // 高亮显示问题
    highlightAIIssues();
    
    showSuccess('AI分析完成');
  } catch (error) {
    showError('AI分析失败：' + error.message);
  } finally {
    analyzing.value = false;
    hideProgress();
  }
};
```

## 响应式设计

### 桌面端 (≥1200px)
- 三栏布局：评审列表 + 详情面板 + 代码视图
- 支持拖拽调整面板大小
- 评论浮层显示

### 平板端 (768px-1199px)
- 两栏布局：列表/详情切换 + 代码视图
- 评论抽屉显示
- 简化工具栏

### 移动端 (<768px)
- 单栏布局，页面切换
- 底部导航栏
- 手势操作支持

## 性能优化

### 1. 虚拟滚动和懒加载

```typescript
// 评审列表虚拟滚动
const virtualListConfig = {
  itemHeight: 120,
  buffer: 5,
  threshold: 50
};

// 代码差异懒加载
const loadFileDiff = async (filePath: string) => {
  if (!diffCache.has(filePath)) {
    const diff = await fetchFileDiff(currentReview.value.id, filePath);
    diffCache.set(filePath, diff);
  }
  return diffCache.get(filePath);
};
```

### 2. 状态缓存

```typescript
// 评审详情缓存
const reviewCache = new Map<string, CodeReview>();

// 评论缓存
const commentCache = new Map<string, ReviewComment[]>();

// 自动清理过期缓存
const cleanExpiredCache = () => {
  const now = Date.now();
  const expiry = 5 * 60 * 1000; // 5分钟
  
  for (const [key, data] of reviewCache.entries()) {
    if (now - data.lastAccess > expiry) {
      reviewCache.delete(key);
    }
  }
};
```

## 安全考虑

### 1. 权限控制

```typescript
// 评审权限检查
const checkReviewPermission = (review: CodeReview, action: string): boolean => {
  switch (action) {
    case 'approve':
      return isReviewer(review) && !isAuthor(review);
    case 'merge':
      return hasPermission('repo:merge') && isApproved(review);
    case 'edit':
      return isAuthor(review) || hasPermission('repo:admin');
    default:
      return false;
  }
};
```

## 用户体验优化

### 1. 实时协作

```typescript
// WebSocket连接评审实时更新
const setupRealtimeUpdates = (reviewId: string) => {
  const ws = new WebSocket(`ws://api/reviews/${reviewId}/updates`);
  
  ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    handleRealtimeUpdate(update);
  };
  
  ws.onclose = () => {
    // 重连逻辑
    setTimeout(() => setupRealtimeUpdates(reviewId), 3000);
  };
};
```

### 2. 快捷键支持

```typescript
// 键盘快捷键
const keyboardShortcuts = {
  'r': () => handleQuickReply(),           // 快速回复
  'a': () => handleQuickApprove(),         // 快速批准
  'c': () => showCommentDialog(),          // 添加评论
  'n': () => navigateToNextFile(),         // 下一个文件
  'p': () => navigateToPrevFile(),         // 上一个文件
  'Escape': () => closeCurrentDialog(),    // 关闭对话框
  'Ctrl+Enter': () => submitCurrentForm(), // 提交表单
  'j': () => navigateToNextDiff(),         // 下一个差异
  'k': () => navigateToPrevDiff()          // 上一个差异
};
``` 