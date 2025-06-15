# 用户资料页面原型

## 页面概述
用户资料页面提供完整的个人信息管理功能，包括基本信息编辑、安全设置、偏好配置、账户管理等，支持多维度的个性化设置。

## 页面布局

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            个人资料                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌───────────────────────┐ ┌───────────────────────────────────────────────┐ │
│ │      个人信息卡片      │ │                设置内容区域                    │ │
│ │                       │ │                                               │ │
│ │  ┌─────────────────┐  │ │ ┌───────────────────────────────────────────┐ │ │
│ │  │   👤 头像区域    │  │ │ │            基本信息                        │ │ │
│ │  │                 │  │ │ │                                           │ │ │
│ │  │    🖼️ 大头像     │  │ │ │ 📝 个人信息:                              │ │ │
│ │  │                 │  │ │ │ • 姓名: [张三                        ]   │ │ │
│ │  │  [上传头像]     │  │ │ │ • 邮箱: [zhang.san@company.com       ]   │ │ │
│ │  └─────────────────┘  │ │ │ • 电话: [+86 138-0013-8000           ]   │ │ │
│ │                       │ │ │ • 部门: [技术部 ▼]                       │ │ │
│ │  📋 基本信息           │ │ │ • 职位: [高级开发工程师                ]   │ │ │
│ │  • 用户名: zhangsan    │ │ │ • 工号: [EMP001                      ]   │ │ │
│ │  • 用户ID: 10001      │ │ │                                           │ │ │
│ │  • 角色: 开发工程师    │ │ │ 🏢 公司信息:                              │ │ │
│ │  • 状态: 🟢 活跃      │ │ │ • 公司: [科技有限公司                 ]   │ │ │
│ │                       │ │ │ • 地址: [北京市朝阳区xxx路xxx号        ]   │ │ │
│ │  📊 统计信息           │ │ │ • 入职时间: [2022-03-15]                 │ │ │
│ │  • 注册时间: 2022-03-15│ │ │                                           │ │ │
│ │  • 最后登录: 2分钟前   │ │ │ 🔗 社交链接:                              │ │ │
│ │  • 登录次数: 1,234次  │ │ │ • GitHub: [https://github.com/zhangsan  ] │ │ │
│ │  • 项目参与: 12个     │ │ │ • LinkedIn: [可选                    ]   │ │ │
│ │  • 代码提交: 2,567次  │ │ │ • 个人网站: [可选                     ]   │ │ │
│ │                       │ │ │                                           │ │ │
│ │  🏆 成就徽章           │ │ │ [保存更改] [重置]                         │ │ │
│ │  🥇 代码贡献者         │ │ └───────────────────────────────────────────┘ │ │
│ │  🔥 活跃开发者         │ │                                               │ │
│ │  📊 质量专家           │ │ ┌───────────────────────────────────────────┐ │ │
│ │  🚀 创新先锋           │ │ │            安全设置                        │ │ │
│ │                       │ │ │                                           │ │ │
│ │  [编辑资料]           │ │ │ 🔐 密码管理:                              │ │ │
│ └───────────────────────┘ │ │ • 当前密码强度: 🟢 强                     │ │ │
│                           │ │ • 上次更改: 30天前                         │ │ │
│ ┌───────────────────────┐ │ │ • [更改密码] [密码历史]                   │ │ │
│ │      设置导航菜单      │ │ │                                           │ │ │
│ │                       │ │ │ 🛡️ 双因子认证:                            │ │ │
│ │ 🔧 基本信息           │ │ │ • 状态: 🟢 已启用 (TOTP)                  │ │ │
│ │ 🔐 安全设置           │ │ │ • 备用方式: 📱 短信验证                   │ │ │
│ │ 🎨 偏好设置           │ │ │ • [管理2FA] [生成备用码]                  │ │ │
│ │ 🔔 通知设置           │ │ │                                           │ │ │
│ │ 🔑 API密钥           │ │ │ 📱 设备管理:                              │ │ │
│ │ 📊 使用分析           │ │ │ ┌─────────────────────────────────────────┐ │ │ │
│ │ ⚡ 高级设置           │ │ │ │设备类型│最后活动    │位置    │状态│操作│ │ │ │
│ │ 📝 活动日志           │ │ │ ├─────────────────────────────────────────┤ │ │ │
│ │ 🚫 账户注销           │ │ │ │💻 Chrome │2分钟前     │北京   │✅  │[信任]│ │ │ │
│ └───────────────────────┘ │ │ │📱 Mobile │1小时前     │北京   │✅  │[撤销]│ │ │ │
│                           │ │ │🖥️ Firefox│昨天       │上海   │⚠️  │[移除]│ │ │ │
│                           │ │ └─────────────────────────────────────────┘ │ │ │
│                           │ │                                           │ │ │
│                           │ │ 🔍 会话管理:                              │ │ │
│                           │ │ • 当前活跃会话: 3个                       │ │ │
│                           │ │ • [查看所有会话] [注销其他设备]           │ │ │
│                           │ │                                           │ │ │
│                           │ │ ⚠️ 安全建议:                              │ │ │
│                           │ │ • 定期更换密码                           │ │ │
│                           │ │ • 注意异常登录位置                       │ │ │
│                           │ │ • 保持应用程序更新                       │ │ │
│                           │ └───────────────────────────────────────────┘ │ │
│                           └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 数据模型

### 用户资料接口
```typescript
interface UserProfile {
  // 基本信息
  id: string
  username: string
  email: string
  displayName: string
  firstName?: string
  lastName?: string
  avatar: string
  
  // 联系信息
  phone?: string
  alternateEmail?: string
  
  // 职业信息
  company?: string
  department?: string
  position?: string
  employeeId?: string
  hireDate?: string
  
  // 地址信息
  address: Address
  
  // 社交链接
  socialLinks: SocialLink[]
  
  // 偏好设置
  preferences: UserPreferences
  
  // 安全设置
  security: SecuritySettings
  
  // 账户状态
  accountStatus: AccountStatus
  emailVerified: boolean
  phoneVerified: boolean
  
  // 统计信息
  statistics: UserStatistics
  
  // 成就系统
  achievements: Achievement[]
  level: number
  experience: number
  
  // 元数据
  createdAt: string
  updatedAt: string
  lastLoginAt: string
  lastActiveAt: string
  loginCount: number
  
  // 隐私设置
  privacy: PrivacySettings
  
  // 角色和权限
  roles: Role[]
  permissions: Permission[]
  
  // 团队信息
  teams: TeamMembership[]
  reportingTo?: string
  directReports: string[]
}

interface Address {
  country: string
  state?: string
  city: string
  street?: string
  postalCode?: string
  timezone: string
}

interface SocialLink {
  platform: 'github' | 'linkedin' | 'twitter' | 'website' | 'blog'
  url: string
  verified: boolean
}

interface UserPreferences {
  // 界面设置
  theme: 'light' | 'dark' | 'auto'
  language: string
  fontSize: 'small' | 'medium' | 'large'
  density: 'compact' | 'default' | 'comfortable'
  
  // 功能偏好
  defaultView: string
  dateFormat: string
  timeFormat: '12h' | '24h'
  weekStart: 'sunday' | 'monday'
  
  // 编辑器设置
  editor: EditorPreferences
  
  // 通知偏好
  notifications: NotificationPreferences
  
  // 仪表盘配置
  dashboardLayout: DashboardWidget[]
  
  // 快捷键
  shortcuts: Record<string, string>
  
  // 工作习惯
  workingHours: WorkingHours
  availability: AvailabilityStatus
}

interface EditorPreferences {
  theme: string
  fontSize: number
  tabSize: number
  wordWrap: boolean
  showLineNumbers: boolean
  autoSave: boolean
  formatOnSave: boolean
  minimap: boolean
}

interface SecuritySettings {
  // 密码设置
  passwordLastChanged: string
  passwordHistory: string[]
  passwordStrength: PasswordStrength
  requirePasswordChange: boolean
  
  // 多因子认证
  mfaEnabled: boolean
  mfaMethods: MFAMethod[]
  backupCodes: string[]
  
  // 会话管理
  activeSessions: Session[]
  maxSessions: number
  sessionTimeout: number
  
  // 设备管理
  trustedDevices: TrustedDevice[]
  deviceTrackingEnabled: boolean
  
  // 登录安全
  loginNotifications: boolean
  suspiciousActivityAlerts: boolean
  ipWhitelist: string[]
  
  // API访问
  apiKeys: APIKey[]
  
  // 隐私设置
  profileVisibility: 'public' | 'team' | 'private'
  activityVisibility: 'public' | 'team' | 'private'
  allowDataExport: boolean
  allowDataDeletion: boolean
}

interface UserStatistics {
  // 使用统计
  totalLoginTime: number
  averageSessionDuration: number
  mostActiveHours: number[]
  mostActiveDays: string[]
  
  // 工作统计
  projectsParticipated: number
  tasksCompleted: number
  codeCommits: number
  codeReviews: number
  
  // 质量指标
  bugReported: number
  bugFixed: number
  testCasesCreated: number
  documentationContributions: number
  
  // 协作统计
  mentorshipSessions: number
  knowledgeSharing: number
  teamCollaborations: number
  
  // 学习成长
  skillsAcquired: string[]
  certificationsEarned: Certification[]
  trainingCompleted: Training[]
}

interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  category: 'productivity' | 'quality' | 'collaboration' | 'innovation' | 'leadership'
  level: 'bronze' | 'silver' | 'gold' | 'platinum'
  earnedAt: string
  progress?: number
  requirements: AchievementRequirement[]
}

interface NotificationPreferences {
  // 通知渠道
  email: boolean
  push: boolean
  inApp: boolean
  sms: boolean
  
  // 通知类型
  security: boolean
  system: boolean
  project: boolean
  social: boolean
  marketing: boolean
  
  // 通知时间
  quietHours: TimeRange
  weekendNotifications: boolean
  
  // 频率控制
  digest: 'immediate' | 'hourly' | 'daily' | 'weekly'
  maxPerDay: number
}

interface PrivacySettings {
  // 数据共享
  allowAnalytics: boolean
  allowPersonalization: boolean
  allowThirdPartyIntegration: boolean
  
  // 可见性控制
  profileSearchable: boolean
  showOnlineStatus: boolean
  showLastSeen: boolean
  showActivity: boolean
  
  // 数据保留
  dataRetentionPeriod: number
  autoDeleteInactive: boolean
  
  // Cookie设置
  cookiePreferences: CookieSettings
}
```

### 状态管理
```typescript
interface ProfileState {
  // 用户数据
  profile: UserProfile | null
  originalProfile: UserProfile | null
  hasUnsavedChanges: boolean
  
  // 编辑状态
  editMode: boolean
  editingSection: ProfileSection | null
  
  // 安全相关
  securityInfo: SecurityInfo
  activeSessions: Session[]
  trustedDevices: TrustedDevice[]
  
  // 统计数据
  statistics: UserStatistics
  activityLog: ActivityLogEntry[]
  
  // 成就系统
  achievements: Achievement[]
  availableAchievements: Achievement[]
  recentAchievements: Achievement[]
  
  // UI状态
  loading: boolean
  saving: boolean
  error: string | null
  
  // 设置状态
  currentTab: ProfileTab
  
  // 对话框状态
  dialogs: {
    changePassword: boolean
    setupMFA: boolean
    manageDevices: boolean
    uploadAvatar: boolean
    exportData: boolean
    deleteAccount: boolean
    editField: boolean
  }
  
  // 表单状态
  forms: {
    basicInfo: BasicInfoForm
    security: SecurityForm
    preferences: PreferencesForm
    privacy: PrivacyForm
  }
  
  // 验证状态
  validation: {
    email: ValidationStatus
    phone: ValidationStatus
  }
}

interface ProfileActions {
  // 资料管理
  loadProfile(): Promise<void>
  updateProfile(updates: Partial<UserProfile>): Promise<void>
  uploadAvatar(file: File): Promise<void>
  deleteAvatar(): Promise<void>
  
  // 基本信息
  updateBasicInfo(info: Partial<UserProfile>): Promise<void>
  updateContactInfo(contact: ContactInfo): Promise<void>
  updateSocialLinks(links: SocialLink[]): Promise<void>
  
  // 安全设置
  changePassword(oldPassword: string, newPassword: string): Promise<void>
  setupMFA(method: MFAMethod): Promise<void>
  disableMFA(): Promise<void>
  generateBackupCodes(): Promise<string[]>
  
  // 会话管理
  loadActiveSessions(): Promise<void>
  revokeSession(sessionId: string): Promise<void>
  revokeAllOtherSessions(): Promise<void>
  
  // 设备管理
  loadTrustedDevices(): Promise<void>
  trustCurrentDevice(): Promise<void>
  revokeTrustedDevice(deviceId: string): Promise<void>
  
  // API密钥管理
  loadAPIKeys(): Promise<void>
  createAPIKey(name: string, permissions: string[]): Promise<APIKey>
  revokeAPIKey(keyId: string): Promise<void>
  
  // 偏好设置
  updatePreferences(preferences: Partial<UserPreferences>): Promise<void>
  resetPreferences(): Promise<void>
  
  // 通知设置
  updateNotificationPreferences(prefs: NotificationPreferences): Promise<void>
  testNotification(type: string): Promise<void>
  
  // 隐私设置
  updatePrivacySettings(settings: PrivacySettings): Promise<void>
  exportUserData(): Promise<void>
  
  // 账户管理
  verifyEmail(): Promise<void>
  verifyPhone(): Promise<void>
  deactivateAccount(): Promise<void>
  deleteAccount(confirmation: string): Promise<void>
  
  // 统计和分析
  loadStatistics(): Promise<void>
  loadActivityLog(): Promise<void>
  
  // 成就系统
  loadAchievements(): Promise<void>
  claimAchievement(achievementId: string): Promise<void>
  
  // UI操作
  setEditMode(enabled: boolean): void
  setCurrentTab(tab: ProfileTab): void
  toggleDialog(dialog: keyof ProfileState['dialogs']): void
  saveChanges(): Promise<void>
  discardChanges(): void
}

type ProfileSection = 'basic' | 'contact' | 'social' | 'company' | 'preferences'
type ProfileTab = 'basic' | 'security' | 'preferences' | 'notifications' | 'api' | 'analytics' | 'advanced'
```

## 页面交互逻辑

### 基本信息管理
```typescript
// 更新基本信息
async function updateBasicInfo() {
  const validation = validateBasicInfo()
  if (!validation.valid) {
    setFieldErrors(validation.errors)
    return
  }
  
  saving.value = true
  
  try {
    const updates = {
      displayName: basicInfoForm.displayName,
      email: basicInfoForm.email,
      phone: basicInfoForm.phone,
      company: basicInfoForm.company,
      department: basicInfoForm.department,
      position: basicInfoForm.position
    }
    
    await profileStore.updateBasicInfo(updates)
    showSuccessMessage('基本信息更新成功')
    editMode.value = false
    
    // 如果邮箱变更，需要重新验证
    if (updates.email !== profile.value.email) {
      showEmailVerificationDialog()
    }
    
  } catch (error) {
    showErrorMessage('更新失败：' + error.message)
  } finally {
    saving.value = false
  }
}

// 头像上传
async function handleAvatarUpload(file: File) {
  // 验证文件类型和大小
  if (!isValidImageFile(file)) {
    showErrorMessage('请选择有效的图片文件（JPG、PNG、GIF）')
    return
  }
  
  if (file.size > 5 * 1024 * 1024) { // 5MB
    showErrorMessage('头像文件大小不能超过5MB')
    return
  }
  
  try {
    // 压缩图片
    const compressedFile = await compressImage(file, {
      maxWidth: 300,
      maxHeight: 300,
      quality: 0.8
    })
    
    await profileStore.uploadAvatar(compressedFile)
    showSuccessMessage('头像更新成功')
    
  } catch (error) {
    showErrorMessage('头像上传失败：' + error.message)
  }
}

// 社交链接管理
function addSocialLink() {
  socialLinksForm.value.push({
    platform: 'github',
    url: '',
    verified: false
  })
}

function removeSocialLink(index: number) {
  socialLinksForm.value.splice(index, 1)
}

async function verifySocialLink(link: SocialLink, index: number) {
  try {
    const verification = await profileService.verifySocialLink(link)
    
    if (verification.success) {
      socialLinksForm.value[index].verified = true
      showSuccessMessage(`${link.platform} 链接验证成功`)
    } else {
      showErrorMessage(`${link.platform} 链接验证失败：${verification.error}`)
    }
  } catch (error) {
    showErrorMessage('验证失败：' + error.message)
  }
}
```

### 安全设置管理
```typescript
// 密码更改
async function changePassword() {
  const validation = validatePasswordForm()
  if (!validation.valid) {
    setFieldErrors(validation.errors)
    return
  }
  
  try {
    await profileStore.changePassword(
      passwordForm.currentPassword,
      passwordForm.newPassword
    )
    
    showSuccessMessage('密码更改成功，请重新登录')
    
    // 清空表单
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    
    dialogs.changePassword = false
    
    // 可选：自动登出
    const autoLogout = await showConfirmDialog({
      title: '密码已更改',
      message: '为了安全考虑，是否立即注销当前会话？',
      confirmText: '立即注销',
      cancelText: '稍后手动注销'
    })
    
    if (autoLogout) {
      await authStore.logout()
    }
    
  } catch (error) {
    showErrorMessage('密码更改失败：' + error.message)
  }
}

// 设置多因子认证
async function setupMFA() {
  const method = mfaSetupForm.method
  
  try {
    if (method === 'totp') {
      // 生成TOTP密钥和二维码
      const setup = await profileService.initiateTOTPSetup()
      
      showTOTPSetupDialog({
        secret: setup.secret,
        qrCode: setup.qrCode,
        backupCodes: setup.backupCodes
      })
      
    } else if (method === 'sms') {
      // 发送短信验证码
      await profileService.sendSMSSetup(mfaSetupForm.phoneNumber)
      showSMSSetupDialog()
    }
    
  } catch (error) {
    showErrorMessage('MFA设置失败：' + error.message)
  }
}

// 完成MFA设置
async function completeMFASetup() {
  try {
    const result = await profileStore.setupMFA({
      method: mfaSetupForm.method,
      code: mfaSetupForm.verificationCode,
      phoneNumber: mfaSetupForm.phoneNumber
    })
    
    if (result.success) {
      showSuccessMessage('双因子认证设置成功')
      
      // 显示备用码
      if (result.backupCodes) {
        showBackupCodesModal(result.backupCodes)
      }
      
      dialogs.setupMFA = false
      await loadProfile()
    }
    
  } catch (error) {
    showErrorMessage('MFA设置完成失败：' + error.message)
  }
}

// 会话管理
async function revokeSession(session: Session) {
  const confirmed = await showConfirmDialog({
    title: '注销会话',
    message: `确定要注销来自 ${session.location} 的会话吗？`,
    type: 'warning'
  })
  
  if (!confirmed) return
  
  try {
    await profileStore.revokeSession(session.id)
    showSuccessMessage('会话已注销')
    await loadActiveSessions()
  } catch (error) {
    showErrorMessage('注销失败：' + error.message)
  }
}

// 批量注销其他会话
async function revokeAllOtherSessions() {
  const confirmed = await showConfirmDialog({
    title: '注销所有其他会话',
    message: '这将注销除当前会话外的所有活跃会话，确定继续吗？',
    type: 'warning'
  })
  
  if (!confirmed) return
  
  try {
    await profileStore.revokeAllOtherSessions()
    showSuccessMessage('已注销所有其他会话')
    await loadActiveSessions()
  } catch (error) {
    showErrorMessage('批量注销失败：' + error.message)
  }
}

// 设备信任管理
async function trustCurrentDevice() {
  try {
    await profileStore.trustCurrentDevice()
    showSuccessMessage('当前设备已添加到信任列表')
    await loadTrustedDevices()
  } catch (error) {
    showErrorMessage('设备信任失败：' + error.message)
  }
}

async function revokeTrustedDevice(device: TrustedDevice) {
  const confirmed = await showConfirmDialog({
    title: '移除信任设备',
    message: `确定要移除设备 "${device.name}" 的信任状态吗？`,
    type: 'warning'
  })
  
  if (!confirmed) return
  
  try {
    await profileStore.revokeTrustedDevice(device.id)
    showSuccessMessage('设备信任已移除')
    await loadTrustedDevices()
  } catch (error) {
    showErrorMessage('移除失败：' + error.message)
  }
}
```

### API密钥管理
```typescript
// 创建API密钥
async function createAPIKey() {
  const validation = validateAPIKeyForm()
  if (!validation.valid) {
    setFieldErrors(validation.errors)
    return
  }
  
  try {
    const apiKey = await profileStore.createAPIKey(
      apiKeyForm.name,
      apiKeyForm.permissions
    )
    
    showAPIKeyCreatedModal({
      key: apiKey.key,
      name: apiKey.name,
      permissions: apiKey.permissions,
      expiresAt: apiKey.expiresAt
    })
    
    // 清空表单
    apiKeyForm.name = ''
    apiKeyForm.permissions = []
    
    await loadAPIKeys()
    
  } catch (error) {
    showErrorMessage('API密钥创建失败：' + error.message)
  }
}

// 撤销API密钥
async function revokeAPIKey(apiKey: APIKey) {
  const confirmed = await showConfirmDialog({
    title: '撤销API密钥',
    message: `确定要撤销API密钥 "${apiKey.name}" 吗？使用此密钥的应用将无法访问API。`,
    type: 'warning'
  })
  
  if (!confirmed) return
  
  try {
    await profileStore.revokeAPIKey(apiKey.id)
    showSuccessMessage('API密钥已撤销')
    await loadAPIKeys()
  } catch (error) {
    showErrorMessage('撤销失败：' + error.message)
  }
}

// API密钥使用统计
function viewAPIKeyUsage(apiKey: APIKey) {
  showAPIKeyUsageModal({
    key: apiKey,
    usage: apiKey.usage,
    recentRequests: apiKey.recentRequests
  })
}
```

### 偏好设置管理
```typescript
// 主题切换
function changeTheme(theme: 'light' | 'dark' | 'auto') {
  preferencesForm.theme = theme
  
  // 立即应用主题
  applyTheme(theme)
  
  // 保存偏好
  debouncedSavePreferences()
}

// 语言切换
function changeLanguage(language: string) {
  preferencesForm.language = language
  
  // 立即应用语言
  i18n.global.locale = language
  
  // 保存偏好
  debouncedSavePreferences()
}

// 仪表盘布局自定义
function customizeDashboard() {
  showDashboardCustomizationModal({
    currentLayout: preferencesForm.dashboardLayout,
    availableWidgets: getAvailableWidgets(),
    onSave: (newLayout) => {
      preferencesForm.dashboardLayout = newLayout
      savePreferences()
    }
  })
}

// 编辑器设置
function updateEditorPreferences() {
  const editorPrefs = {
    theme: editorForm.theme,
    fontSize: editorForm.fontSize,
    tabSize: editorForm.tabSize,
    wordWrap: editorForm.wordWrap,
    showLineNumbers: editorForm.showLineNumbers,
    autoSave: editorForm.autoSave,
    formatOnSave: editorForm.formatOnSave
  }
  
  preferencesForm.editor = editorPrefs
  
  // 立即应用到编辑器
  applyEditorSettings(editorPrefs)
  
  savePreferences()
}

// 防抖保存偏好设置
const debouncedSavePreferences = debounce(async () => {
  try {
    await profileStore.updatePreferences(preferencesForm.value)
    showSuccessMessage('偏好设置已保存')
  } catch (error) {
    showErrorMessage('保存失败：' + error.message)
  }
}, 1000)
```

### 数据导出和账户管理
```typescript
// 导出用户数据
async function exportUserData() {
  const options = {
    includeProfile: exportForm.includeProfile,
    includeActivity: exportForm.includeActivity,
    includeProjects: exportForm.includeProjects,
    includeFiles: exportForm.includeFiles,
    format: exportForm.format, // 'json' | 'csv' | 'pdf'
    dateRange: exportForm.dateRange
  }
  
  try {
    const exportResult = await profileStore.exportUserData(options)
    
    if (exportResult.immediate) {
      // 立即下载
      downloadFile(exportResult.url, exportResult.filename)
      showSuccessMessage('数据导出完成')
    } else {
      // 异步处理
      showInfoMessage('数据导出正在处理中，完成后将通过邮件通知您')
    }
    
    dialogs.exportData = false
    
  } catch (error) {
    showErrorMessage('数据导出失败：' + error.message)
  }
}

// 账户停用
async function deactivateAccount() {
  const reasons = [
    '暂时不需要使用',
    '功能不满足需求',
    '有安全顾虑',
    '其他原因'
  ]
  
  const deactivationData = await showAccountDeactivationDialog({
    reasons,
    requireReason: true,
    confirmationText: '我确定要停用账户'
  })
  
  if (!deactivationData.confirmed) return
  
  try {
    await profileStore.deactivateAccount(deactivationData.reason)
    
    showSuccessMessage('账户已停用，您可以随时重新激活')
    
    // 可选：立即登出
    setTimeout(() => {
      authStore.logout()
    }, 2000)
    
  } catch (error) {
    showErrorMessage('账户停用失败：' + error.message)
  }
}

// 账户删除
async function deleteAccount() {
  const confirmationSteps = [
    '确认身份验证',
    '确认删除原因',
    '最终确认删除'
  ]
  
  try {
    // 第一步：身份验证
    const authResult = await showPasswordConfirmationDialog()
    if (!authResult.success) return
    
    // 第二步：删除原因
    const reasonResult = await showAccountDeletionReasonDialog()
    if (!reasonResult.confirmed) return
    
    // 第三步：最终确认
    const finalConfirmation = await showFinalConfirmationDialog({
      accountName: profile.value.displayName,
      confirmationText: 'DELETE_MY_ACCOUNT'
    })
    
    if (!finalConfirmation.confirmed) return
    
    await profileStore.deleteAccount(finalConfirmation.confirmationInput)
    
    showSuccessMessage('账户删除请求已提交，我们将在24小时内处理')
    
    // 立即登出
    await authStore.logout()
    
  } catch (error) {
    showErrorMessage('账户删除失败：' + error.message)
  }
}
```

### 成就系统
```typescript
// 加载成就数据
async function loadAchievements() {
  try {
    await profileStore.loadAchievements()
    
    // 检查新获得的成就
    checkNewAchievements()
    
  } catch (error) {
    console.error('Failed to load achievements:', error)
  }
}

// 检查新成就
function checkNewAchievements() {
  const newAchievements = achievements.value.filter(achievement => 
    !localStorage.getItem(`achievement_${achievement.id}_shown`)
  )
  
  if (newAchievements.length > 0) {
    showAchievementNotification(newAchievements)
    
    // 标记为已显示
    newAchievements.forEach(achievement => {
      localStorage.setItem(`achievement_${achievement.id}_shown`, 'true')
    })
  }
}

// 成就进度计算
function calculateAchievementProgress(achievement: Achievement): number {
  const stats = statistics.value
  
  switch (achievement.id) {
    case 'code_contributor':
      return Math.min((stats.codeCommits / 100) * 100, 100)
    case 'bug_hunter':
      return Math.min((stats.bugFixed / 50) * 100, 100)
    case 'collaborator':
      return Math.min((stats.teamCollaborations / 20) * 100, 100)
    default:
      return achievement.progress || 0
  }
}

// 成就分享
function shareAchievement(achievement: Achievement) {
  const shareData = {
    title: `我获得了 ${achievement.name} 成就！`,
    text: achievement.description,
    url: `${location.origin}/profile/${profile.value.id}#achievements`
  }
  
  if (navigator.share) {
    navigator.share(shareData)
  } else {
    // 复制到剪贴板
    copyToClipboard(shareData.url)
    showSuccessMessage('成就链接已复制到剪贴板')
  }
}
```

## 响应式设计适配

### 桌面端布局 (≥1200px)
- 左侧个人信息卡片，右侧设置内容区域
- 底部设置导航菜单
- 完整的统计信息和成就展示

### 平板端布局 (768px-1199px)
- 顶部个人信息卡片
- 底部设置内容区域
- 简化的导航菜单

### 移动端布局 (<768px)
- 垂直布局，全屏显示
- 底部标签栏导航
- 简化的设置选项
- 手势滑动支持

```typescript
// 响应式适配
const isMobile = computed(() => screenWidth.value < 768)
const isTablet = computed(() => screenWidth.value >= 768 && screenWidth.value < 1200)

const layoutStyle = computed(() => ({
  flexDirection: isMobile.value ? 'column' : 'row',
  gap: isMobile.value ? '16px' : '24px'
}))

const cardWidth = computed(() => {
  if (isMobile.value) return '100%'
  if (isTablet.value) return '300px'
  return '350px'
})

const showSidebar = computed(() => !isMobile.value)
const settingsLayout = computed(() => 
  isMobile.value ? 'tabs' : 'sidebar'
)
```

## 性能优化

### 数据懒加载
```typescript
// 按需加载设置数据
const settingsLoaders = {
  async security() {
    if (!securityInfo.value) {
      securityInfo.value = await profileService.getSecurityInfo()
    }
  },
  
  async statistics() {
    if (!statistics.value) {
      statistics.value = await profileService.getUserStatistics()
    }
  },
  
  async achievements() {
    if (!achievements.value.length) {
      achievements.value = await profileService.getAchievements()
    }
  }
}

// 切换标签时加载对应数据
watch(() => currentTab.value, async (newTab) => {
  if (settingsLoaders[newTab]) {
    await settingsLoaders[newTab]()
  }
})
```

### 表单优化
```typescript
// 防抖保存
const debouncedSave = debounce(async (field: string, value: any) => {
  try {
    await profileService.updateField(field, value)
    showFieldSavedIndicator(field)
  } catch (error) {
    showFieldErrorIndicator(field, error.message)
  }
}, 2000)

// 智能保存提示
function setupAutoSave() {
  watch(() => hasUnsavedChanges.value, (hasChanges) => {
    if (hasChanges) {
      showAutoSaveIndicator()
    } else {
      hideAutoSaveIndicator()
    }
  })
  
  // 页面离开前提醒
  window.addEventListener('beforeunload', (event) => {
    if (hasUnsavedChanges.value) {
      event.preventDefault()
      event.returnValue = '您有未保存的更改，确定要离开吗？'
    }
  })
}
```

## 安全考虑

### 敏感信息保护
```typescript
// 敏感字段脱敏显示
function maskSensitiveField(value: string, type: 'email' | 'phone' | 'api_key'): string {
  switch (type) {
    case 'email':
      const [username, domain] = value.split('@')
      return `${username.substring(0, 2)}***@${domain}`
    case 'phone':
      return value.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
    case 'api_key':
      return `${value.substring(0, 8)}...${value.substring(value.length - 4)}`
    default:
      return value
  }
}

// 操作验证
async function requirePasswordConfirmation(action: string): Promise<boolean> {
  const result = await showPasswordConfirmationDialog({
    title: '安全验证',
    message: `为了安全，请输入密码确认${action}操作`,
    action
  })
  
  return result.success
}

// 敏感操作日志
async function logSensitiveOperation(operation: string, details?: any) {
  await auditService.log({
    operation,
    resourceType: 'user_profile',
    resourceId: profile.value.id,
    details,
    timestamp: new Date().toISOString(),
    ipAddress: getClientIPAddress(),
    userAgent: navigator.userAgent
  })
}