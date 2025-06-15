# 代码差异分析页面原型设计

## 页面概述

代码差异分析页面用于显示和分析代码文件的变更差异，提供可视化的代码对比、AI智能分析和变更影响评估功能。

## 页面布局

```
┌─────────────────────────────────────────────────────────────────┐
│ 头部导航栏                                                        │
├─────────────────────────────────────────────────────────────────┤
│ 面包屑导航: 首页 > 代码差异分析                                     │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐    │
│ │ 导入Git │ │ 上传文件 │ │ 在线编辑 │ │   设置   │ │  AI分析  │    │
│ └─────────┘ └─────────┘ └─────────┘ └──────────┘ └──────────┘    │
├─────────────────────────────────────────────────────────────────┤
│ 文件树列表区域                    │  差异对比区域                   │
│ ┌─────────────────────────────┐   │ ┌─────────────────────────────┐ │
│ │ 📁 src/                     │   │ │ 文件：UserService.ts        │ │
│ │   📁 components/            │   │ │ ─────────────────────────────│ │
│ │     📄 Header.vue      [M]  │   │ │ 原始版本    │    修改版本     │ │
│ │     📄 Footer.vue      [A]  │   │ │ ─────────── │ ─────────────  │ │
│ │   📁 services/              │   │ │ 1  import { │ 1  import {    │ │
│ │     📄 UserService.ts  [M]  │   │ │ 2    User   │ 2    User,     │ │
│ │     📄 ApiClient.ts    [D]  │   │ │ 3  } from   │ 3    Profile   │ │
│ │   📁 utils/                 │   │ │ 4  './types'│ 4  } from      │ │
│ │     📄 helpers.ts      [M]  │   │ │ 5           │ 5  './types'   │ │
│ │                             │   │ │ 6  export   │ 6             │ │
│ │ 图例:                        │   │ │ 7  class    │ 7  export     │ │
│ │ [M] 修改  [A] 新增  [D] 删除 │   │ │ 8  UserSer- │ 8  class      │ │
│ │                             │   │ │ 9  vice {   │ 9  UserSer-   │ │
│ │ └─────────────────────────────┘   │ │ 10          │ 10 vice {     │ │
│                                   │ └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ AI分析结果面板（可折叠）                                           │
│ ┌───────────────────────────────────────────────────────────────┐ │
│ │ 📊 变更影响分析                  🔍 代码质量检查                │ │
│ │ • 修改文件: 3个                  • 代码复杂度: 增加12%         │ │
│ │ • 新增文件: 1个                  • 测试覆盖率: 需要新增测试     │ │
│ │ • 删除文件: 1个                  • 潜在问题: 2个              │ │
│ │ • 影响模块: UserManagement       • 建议重构: 1处              │ │
│ │                                                               │ │
│ │ ⚠️  风险评估                     💡 优化建议                   │ │
│ │ • 高风险变更: 1个                • 使用TypeScript严格模式     │ │
│ │ • API兼容性: 无影响              • 添加单元测试               │ │
│ │ • 性能影响: 轻微提升              • 考虑代码分割               │ │
│ └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 功能组件

### 1. 差异导入区域

#### Git仓库导入
- 支持Git URL导入
- 分支选择和提交记录比较
- 支持私有仓库认证

#### 文件上传
- 支持拖拽上传
- 批量文件上传
- 压缩包解压

#### 在线编辑
- 内置代码编辑器
- 语法高亮
- 实时预览

### 2. 文件树导航

#### 文件状态标识
- [M] 修改文件
- [A] 新增文件
- [D] 删除文件
- [R] 重命名文件

#### 筛选功能
- 按文件类型筛选
- 按变更状态筛选
- 搜索文件名

### 3. 差异对比视图

#### 并排对比模式
- 左右分屏显示
- 行号对齐
- 变更高亮显示

#### 统一差异模式
- 上下文显示
- 折叠未变更区域
- 差异统计信息

#### 交互功能
- 滚动同步
- 跳转到下一个差异
- 展开/折叠代码块

### 4. AI分析面板

#### 变更影响分析
- 修改文件统计
- 影响模块识别
- 依赖关系分析

#### 代码质量检查
- 复杂度分析
- 代码规范检查
- 安全漏洞扫描

#### 风险评估
- 变更风险等级
- 兼容性检查
- 性能影响评估

## 数据模型

### 代码差异实体

```typescript
interface CodeDiff {
  id: string;                    // 差异分析ID
  name: string;                  // 分析名称
  type: DiffType;               // 差异类型
  source: DiffSource;           // 数据源信息
  files: FileDiff[];            // 文件差异列表
  statistics: DiffStatistics;   // 差异统计
  aiAnalysis?: AIDiffAnalysis;  // AI分析结果
  createdAt: Date;              // 创建时间
  updatedAt: Date;              // 更新时间
  createdBy: string;            // 创建者
}

enum DiffType {
  GIT_COMMIT = 'git_commit',     // Git提交对比
  FILE_UPLOAD = 'file_upload',   // 文件上传对比
  MANUAL_EDIT = 'manual_edit'    // 手动编辑对比
}

interface DiffSource {
  type: DiffType;
  gitRepo?: {
    url: string;
    branch: string;
    fromCommit: string;
    toCommit: string;
  };
  files?: {
    originalFiles: FileInfo[];
    modifiedFiles: FileInfo[];
  };
}

interface FileDiff {
  path: string;                  // 文件路径
  status: FileStatus;            // 文件状态
  language: string;              // 编程语言
  originalContent?: string;      // 原始内容
  modifiedContent?: string;      // 修改后内容
  chunks: DiffChunk[];           // 差异块
  statistics: FileStatistics;   // 文件统计
}

enum FileStatus {
  ADDED = 'added',               // 新增
  MODIFIED = 'modified',         // 修改
  DELETED = 'deleted',           // 删除
  RENAMED = 'renamed'            // 重命名
}

interface DiffChunk {
  originalStart: number;         // 原始文件起始行
  originalLines: number;         // 原始文件行数
  modifiedStart: number;         // 修改文件起始行
  modifiedLines: number;         // 修改文件行数
  content: string;               // 差异内容
  type: 'context' | 'add' | 'delete'; // 行类型
}

interface DiffStatistics {
  totalFiles: number;            // 总文件数
  addedFiles: number;            // 新增文件数
  modifiedFiles: number;         // 修改文件数
  deletedFiles: number;          // 删除文件数
  addedLines: number;            // 新增行数
  deletedLines: number;          // 删除行数
  languages: LanguageStats[];    // 语言统计
}

interface FileStatistics {
  addedLines: number;
  deletedLines: number;
  complexity: number;            // 复杂度变化
}

interface LanguageStats {
  language: string;
  files: number;
  addedLines: number;
  deletedLines: number;
}

interface AIDiffAnalysis {
  impactAnalysis: ImpactAnalysis;
  qualityAnalysis: QualityAnalysis;
  riskAssessment: RiskAssessment;
  suggestions: Suggestion[];
  complexity: ComplexityAnalysis;
}

interface ImpactAnalysis {
  affectedModules: string[];     // 影响的模块
  dependencyChanges: DependencyChange[]; // 依赖变更
  apiChanges: APIChange[];       // API变更
  performanceImpact: 'positive' | 'negative' | 'neutral'; // 性能影响
}

interface QualityAnalysis {
  codeComplexity: {
    before: number;
    after: number;
    change: number;
  };
  testCoverage: {
    current: number;
    required: number;
    missing: string[];
  };
  codeIssues: CodeIssue[];
  refactoringSuggestions: RefactoringSuggestion[];
}

interface RiskAssessment {
  overallRisk: 'low' | 'medium' | 'high' | 'critical';
  riskFactors: RiskFactor[];
  breakingChanges: BreakingChange[];
  compatibilityIssues: CompatibilityIssue[];
}

interface CodeIssue {
  severity: 'error' | 'warning' | 'info';
  message: string;
  file: string;
  line: number;
  rule: string;
}

interface Suggestion {
  type: 'performance' | 'security' | 'maintainability' | 'testing';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  effort: 'small' | 'medium' | 'large';
}
```

### 分析配置

```typescript
interface DiffAnalysisConfig {
  ignorePatterns: string[];      // 忽略模式
  languageSettings: LanguageSetting[];
  aiAnalysisEnabled: boolean;
  qualityRules: QualityRule[];
  riskThresholds: RiskThreshold[];
}

interface LanguageSetting {
  language: string;
  enabled: boolean;
  syntaxHighlight: boolean;
  qualityRules: string[];
}

interface QualityRule {
  id: string;
  name: string;
  enabled: boolean;
  severity: 'error' | 'warning' | 'info';
  pattern?: string;
}

interface RiskThreshold {
  metric: string;
  warningThreshold: number;
  errorThreshold: number;
}
```

## 状态管理

### Store定义

```typescript
interface CodeDiffState {
  // 当前差异分析
  currentDiff: CodeDiff | null;
  loading: boolean;
  
  // 文件树状态
  fileTree: FileTreeNode[];
  selectedFile: string | null;
  expandedFolders: Set<string>;
  
  // 视图状态
  viewMode: 'split' | 'unified';
  showLineNumbers: boolean;
  showWhitespace: boolean;
  wordWrap: boolean;
  
  // AI分析状态
  aiAnalysisVisible: boolean;
  analyzing: boolean;
  analysisResult: AIDiffAnalysis | null;
  
  // 筛选状态
  fileFilter: {
    status: FileStatus[];
    language: string[];
    search: string;
  };
  
  // 配置
  config: DiffAnalysisConfig;
}

interface CodeDiffActions {
  // 导入操作
  importFromGit: (gitInfo: GitImportInfo) => Promise<void>;
  uploadFiles: (files: File[]) => Promise<void>;
  createManualDiff: (original: string, modified: string) => Promise<void>;
  
  // 文件操作
  selectFile: (filePath: string) => void;
  toggleFolder: (folderPath: string) => void;
  navigateToNextDiff: () => void;
  navigateToPrevDiff: () => void;
  
  // 视图控制
  setViewMode: (mode: 'split' | 'unified') => void;
  toggleLineNumbers: () => void;
  toggleWhitespace: () => void;
  toggleWordWrap: () => void;
  
  // AI分析
  runAIAnalysis: () => Promise<void>;
  toggleAIAnalysisPanel: () => void;
  
  // 筛选操作
  updateFileFilter: (filter: Partial<FileFilter>) => void;
  resetFileFilter: () => void;
  
  // 配置管理
  updateConfig: (config: Partial<DiffAnalysisConfig>) => void;
  
  // 导出操作
  exportDiff: (format: 'html' | 'pdf' | 'json') => Promise<void>;
}

interface FileTreeNode {
  path: string;
  name: string;
  type: 'file' | 'folder';
  status?: FileStatus;
  children?: FileTreeNode[];
  statistics?: FileStatistics;
}
```

## 页面交互逻辑

### 1. 差异导入流程

```typescript
// Git仓库导入
const handleGitImport = async (gitInfo: GitImportInfo) => {
  try {
    loading.value = true;
    showProgress('正在克隆代码仓库...');
    
    const diff = await importFromGit(gitInfo);
    currentDiff.value = diff;
    
    // 构建文件树
    buildFileTree(diff.files);
    
    // 自动选择第一个修改的文件
    selectFirstModifiedFile();
    
    showSuccess('代码导入成功');
  } catch (error) {
    showError('导入失败：' + error.message);
  } finally {
    loading.value = false;
    hideProgress();
  }
};

// 文件上传处理
const handleFileUpload = async (files: File[]) => {
  try {
    loading.value = true;
    showProgress('正在分析文件差异...');
    
    const diff = await uploadFiles(files);
    currentDiff.value = diff;
    
    buildFileTree(diff.files);
    selectFirstModifiedFile();
    
    showSuccess('文件上传成功');
  } catch (error) {
    showError('上传失败：' + error.message);
  } finally {
    loading.value = false;
    hideProgress();
  }
};
```

### 2. 文件导航逻辑

```typescript
// 文件选择
const handleFileSelect = (filePath: string) => {
  selectFile(filePath);
  
  // 更新差异视图
  updateDiffView(filePath);
  
  // 记录访问历史
  addToHistory(filePath);
};

// 文件夹展开/折叠
const handleFolderToggle = (folderPath: string) => {
  toggleFolder(folderPath);
  
  // 保存展开状态到本地存储
  saveExpandedState();
};

// 差异导航
const handleNavigateToDiff = (direction: 'next' | 'prev') => {
  const currentLine = getCurrentLine();
  const nextDiff = findNextDiff(currentLine, direction);
  
  if (nextDiff) {
    scrollToLine(nextDiff.line);
    highlightDiff(nextDiff);
  } else {
    // 切换到下一个/上一个文件
    const nextFile = getNextFile(direction);
    if (nextFile) {
      selectFile(nextFile.path);
    }
  }
};
```

### 3. 差异视图交互

```typescript
// 视图模式切换
const handleViewModeChange = (mode: 'split' | 'unified') => {
  setViewMode(mode);
  
  // 重新渲染差异视图
  rerenderDiffView();
  
  // 保持当前滚动位置
  maintainScrollPosition();
};

// 行点击处理
const handleLineClick = (lineNumber: number, side: 'left' | 'right') => {
  // 同步滚动到对应行
  syncScrollPosition(lineNumber, side);
  
  // 显示行信息
  showLineInfo(lineNumber, side);
};

// 代码折叠/展开
const handleCodeFolding = (startLine: number, endLine: number) => {
  if (isCodeFolded(startLine, endLine)) {
    expandCode(startLine, endLine);
  } else {
    foldCode(startLine, endLine);
  }
  
  updateFoldingState();
};
```

### 4. AI分析集成

```typescript
// 触发AI分析
const handleAIAnalysis = async () => {
  if (!currentDiff.value) return;
  
  try {
    analyzing.value = true;
    showProgress('AI正在分析代码差异...');
    
    const analysis = await runAIAnalysis();
    analysisResult.value = analysis;
    
    // 显示分析结果
    aiAnalysisVisible.value = true;
    
    // 在代码中标记问题
    highlightCodeIssues(analysis.qualityAnalysis.codeIssues);
    
    showSuccess('AI分析完成');
  } catch (error) {
    showError('AI分析失败：' + error.message);
  } finally {
    analyzing.value = false;
    hideProgress();
  }
};

// 分析结果交互
const handleAnalysisResultClick = (issue: CodeIssue) => {
  // 跳转到问题所在行
  selectFile(issue.file);
  scrollToLine(issue.line);
  highlightLine(issue.line);
  
  // 显示问题详情
  showIssueDetails(issue);
};
```

### 5. 筛选和搜索

```typescript
// 文件筛选
const handleFileFilter = (filter: Partial<FileFilter>) => {
  updateFileFilter(filter);
  
  // 更新文件树显示
  updateFileTreeVisibility();
  
  // 如果当前选中文件被筛选掉，选择第一个可见文件
  if (!isCurrentFileVisible()) {
    selectFirstVisibleFile();
  }
};

// 文件搜索
const handleFileSearch = debounce((keyword: string) => {
  updateFileFilter({ search: keyword });
  updateFileTreeVisibility();
}, 300);
```

## 响应式设计

### 桌面端 (≥1200px)
- 三栏布局：文件树 + 差异视图 + AI分析面板
- 文件树可调整宽度
- 差异视图支持并排和统一模式

### 平板端 (768px-1199px)
- 两栏布局：文件树折叠 + 差异视图
- AI分析面板以抽屉形式显示
- 简化工具栏选项

### 移动端 (<768px)
- 单栏布局，分页显示
- 文件树、差异视图、分析结果分别占据全屏
- 底部标签页导航

## 性能优化

### 1. 虚拟滚动

```typescript
// 大文件差异虚拟滚动
const virtualScrollConfig = {
  itemHeight: 20,           // 每行高度
  buffer: 50,              // 缓冲区行数
  threshold: 1000          // 启用虚拟滚动的行数阈值
};

// 按需加载文件内容
const loadFileContent = async (filePath: string) => {
  if (!contentCache.has(filePath)) {
    const content = await fetchFileContent(filePath);
    contentCache.set(filePath, content);
  }
  return contentCache.get(filePath);
};
```

### 2. 差异计算优化

```typescript
// Web Worker计算差异
const calculateDiff = async (original: string, modified: string) => {
  return new Promise((resolve) => {
    const worker = new Worker('/workers/diff-worker.js');
    worker.postMessage({ original, modified });
    worker.onmessage = (e) => {
      resolve(e.data.diff);
      worker.terminate();
    };
  });
};

// 增量更新差异
const updateDiffIncremental = (changes: Change[]) => {
  const existingDiff = currentDiff.value;
  const updatedDiff = applyChangesToDiff(existingDiff, changes);
  currentDiff.value = updatedDiff;
};
```

### 3. 内存管理

```typescript
// 文件内容缓存管理
class ContentCache {
  private cache = new Map<string, string>();
  private maxSize = 50; // 最大缓存文件数
  
  set(key: string, content: string) {
    if (this.cache.size >= this.maxSize) {
      // 删除最旧的缓存
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, content);
  }
  
  get(key: string): string | undefined {
    return this.cache.get(key);
  }
  
  clear() {
    this.cache.clear();
  }
}
```

## 安全考虑

### 1. 文件上传安全

```typescript
// 文件类型检查
const validateFileType = (file: File): boolean => {
  const allowedTypes = ['.js', '.ts', '.vue', '.py', '.java', '.cpp'];
  const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
  return allowedTypes.includes(extension);
};

// 文件大小限制
const validateFileSize = (file: File): boolean => {
  const maxSize = 10 * 1024 * 1024; // 10MB
  return file.size <= maxSize;
};

// 文件内容安全检查
const scanFileContent = async (content: string): Promise<SecurityIssue[]> => {
  const issues: SecurityIssue[] = [];
  
  // 检查敏感信息
  if (containsCredentials(content)) {
    issues.push({
      type: 'credentials',
      message: '检测到可能的凭据信息',
      severity: 'high'
    });
  }
  
  return issues;
};
```

### 2. Git仓库安全

```typescript
// Git URL验证
const validateGitUrl = (url: string): boolean => {
  const gitUrlPattern = /^(https?:\/\/|git@)[\w\.-]+[:\w\.-\/]+\.git$/;
  return gitUrlPattern.test(url);
};

// 私有仓库认证
const authenticateGitRepo = async (url: string, credentials: GitCredentials) => {
  // 使用安全的方式处理认证信息
  const encryptedCredentials = await encryptCredentials(credentials);
  return await gitClient.authenticate(url, encryptedCredentials);
};
```

## 用户体验优化

### 1. 加载状态

```typescript
// 分阶段加载反馈
const showLoadingStages = (stages: string[]) => {
  let currentStage = 0;
  
  const updateStage = () => {
    if (currentStage < stages.length) {
      showProgress(stages[currentStage]);
      currentStage++;
      setTimeout(updateStage, 1000);
    }
  };
  
  updateStage();
};

// 导入进度示例
const gitImportStages = [
  '正在连接Git仓库...',
  '正在下载代码...',
  '正在计算差异...',
  '正在生成分析报告...'
];
```

### 2. 快捷键支持

```typescript
// 键盘快捷键
const keyboardShortcuts = {
  'Ctrl+F': () => showSearchDialog(),        // 搜索
  'F3': () => navigateToNextDiff(),          // 下一个差异
  'Shift+F3': () => navigateToPrevDiff(),    // 上一个差异
  'Ctrl+G': () => showGoToLineDialog(),      // 跳转到行
  'Ctrl+D': () => toggleAIAnalysisPanel(),   // 切换AI面板
  'Escape': () => closeCurrentPanel()       // 关闭面板
};
```

### 3. 自动保存和恢复

```typescript
// 自动保存分析状态
const autoSaveState = debounce(() => {
  const state = {
    currentDiff: currentDiff.value,
    selectedFile: selectedFile.value,
    viewMode: viewMode.value,
    fileFilter: fileFilter.value
  };
  
  localStorage.setItem('codeDiffState', JSON.stringify(state));
}, 1000);

// 恢复上次状态
const restoreState = () => {
  const savedState = localStorage.getItem('codeDiffState');
  if (savedState) {
    const state = JSON.parse(savedState);
    // 恢复状态
    restoreAnalysisState(state);
  }
};
``` 