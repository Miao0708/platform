# 登录页面原型

## 页面概述
登录页面提供用户身份认证功能，支持多种登录方式、安全验证、记住登录状态等功能，采用现代化的UI设计和完善的安全机制。

## 页面布局

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌─────────────────────────────────┐  ┌───────────────────────────────────┐ │
│  │           左侧背景区域           │  │          右侧登录区域              │ │
│  │                                 │  │                                   │ │
│  │  🎨 动态渐变背景                │  │  ┌─────────────────────────────┐  │ │
│  │                                 │  │  │      AI研发辅助平台          │  │ │
│  │  ┌─────────────────────────┐    │  │  │                             │  │ │
│  │  │   🚀 平台特性展示        │    │  │  │  👋 欢迎回来                │  │ │
│  │  │                         │    │  │  │                             │  │ │
│  │  │  ✨ 智能代码分析         │    │  │  │  🔐 登录方式选择：           │  │ │
│  │  │  🤖 AI辅助开发          │    │  │  │  ○ 用户名密码               │  │ │
│  │  │  📊 可视化报告          │    │  │  │  ○ 企业SSO                 │  │ │
│  │  │  🔄 自动化流水线        │    │  │  │  ○ 第三方登录               │  │ │
│  │  │  🛡️ 安全审计           │    │  │  │                             │  │ │
│  │  │                         │    │  │  │  ┌─────────────────────────┐  │  │ │
│  │  │  [了解更多 →]           │    │  │  │  │📧 用户名/邮箱            │  │  │ │
│  │  └─────────────────────────┘    │  │  │  │ user@example.com        │  │  │ │
│  │                                 │  │  │  └─────────────────────────┘  │  │ │
│  │  ┌─────────────────────────┐    │  │  │                             │  │ │
│  │  │    💡 今日提示           │    │  │  │  ┌─────────────────────────┐  │  │ │
│  │  │                         │    │  │  │  │🔒 密码                  │  │  │ │
│  │  │  使用AI助手提升代码质量， │    │  │  │  │ ••••••••••••••••        │  │  │ │
│  │  │  让开发效率翻倍！        │    │  │  │  │               [👁]      │  │  │ │
│  │  │                         │    │  │  │  └─────────────────────────┘  │  │ │
│  │  │  "今天已有128位开发者     │    │  │  │                             │  │ │
│  │  │   使用平台完成代码审查"   │    │  │  │  ☐ 记住登录状态              │  │ │
│  │  └─────────────────────────┘    │  │  │                             │  │ │
│  │                                 │  │  │  ┌─────────────────────────┐  │  │ │
│  │  版本: v2.1.0                   │  │  │  │   🔑 登录              │  │  │ │
│  │  最后更新: 2024-01-15           │  │  │  └─────────────────────────┘  │  │ │
│  │                                 │  │  │                             │  │ │
│  └─────────────────────────────────┘  │  │  或者使用：                  │  │ │
│                                       │  │  [GitHub] [Google] [微信]    │  │ │
│                                       │  │                             │  │ │
│                                       │  │  ──────────────────────────  │  │ │
│                                       │  │                             │  │ │
│                                       │  │  🔗 忘记密码？               │  │ │
│                                       │  │  🆕 还没有账号？立即注册      │  │ │
│                                       │  │                             │  │ │
│                                       │  │  ──────────────────────────  │  │ │
│                                       │  │                             │  │ │
│                                       │  │  🌐 语言: 中文 ▼             │  │ │
│                                       │  │  🌙 主题: 自动 ▼             │  │ │
│                                       │  │                             │  │ │
│                                       │  │  ┌─────────────────────────┐  │  │ │
│                                       │  │  │    🔐 验证码验证         │  │ │ │
│                                       │  │  │                         │  │ │ │
│                                       │  │  │  请输入验证码：           │  │ │ │
│                                       │  │  │  ┌─────┐ ┌─────────────┐ │  │ │ │
│                                       │  │  │  │KXPQ │ │ [输入验证码] │ │  │ │ │
│                                       │  │  │  └─────┘ └─────────────┘ │  │ │ │
│                                       │  │  │           [刷新验证码]   │  │ │ │
│                                       │  │  └─────────────────────────┘  │  │ │
│                                       │  └─────────────────────────────┘  │ │
│                                       └───────────────────────────────────┘ │
│                                                                             │
│  页脚: © 2024 AI研发辅助平台. 保留所有权利. | 隐私政策 | 服务条款 | 帮助中心  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 数据模型

### 用户认证接口
```typescript
interface LoginRequest {
  // 基础登录
  username?: string
  email?: string
  password?: string
  
  // 验证码
  captcha?: string
  captchaId?: string
  
  // 二次验证
  mfaCode?: string
  mfaMethod?: 'totp' | 'sms' | 'email'
  
  // 登录选项
  rememberMe: boolean
  loginType: LoginType
  
  // 设备信息
  deviceInfo: DeviceInfo
  
  // SSO登录
  ssoProvider?: SSOProvider
  ssoToken?: string
  
  // 第三方登录
  oauthProvider?: OAuthProvider
  oauthCode?: string
  oauthState?: string
}

interface LoginResponse {
  success: boolean
  token?: string
  refreshToken?: string
  user?: UserProfile
  sessionId?: string
  expiresAt?: string
  
  // 安全检查结果
  securityCheck: SecurityCheckResult
  
  // 需要额外验证
  requiresMFA?: boolean
  mfaMethods?: MFAMethod[]
  
  // 登录失败信息
  error?: string
  errorCode?: string
  remainingAttempts?: number
  lockoutTime?: string
  
  // 首次登录
  isFirstLogin?: boolean
  mustChangePassword?: boolean
  
  // 设备验证
  requiresDeviceVerification?: boolean
  verificationMethods?: VerificationMethod[]
}

interface UserProfile {
  id: string
  username: string
  email: string
  displayName: string
  avatar?: string
  roles: Role[]
  permissions: Permission[]
  preferences: UserPreferences
  lastLoginAt?: string
  loginCount: number
  accountStatus: AccountStatus
}

interface DeviceInfo {
  userAgent: string
  platform: string
  browser: string
  browserVersion: string
  os: string
  osVersion: string
  screen: ScreenInfo
  timezone: string
  language: string
  fingerprint: string
}

interface SecurityCheckResult {
  deviceTrusted: boolean
  locationSuspicious: boolean
  timePatternNormal: boolean
  riskScore: number
  riskLevel: 'low' | 'medium' | 'high'
  recommendations: string[]
}

interface MFAMethod {
  type: 'totp' | 'sms' | 'email' | 'hardware_key'
  enabled: boolean
  verified: boolean
  setupRequired?: boolean
  phoneNumber?: string
  email?: string
}

type LoginType = 'username' | 'email' | 'sso' | 'oauth'
type SSOProvider = 'azure_ad' | 'okta' | 'auth0' | 'ldap'
type OAuthProvider = 'github' | 'google' | 'wechat' | 'dingtalk'
type AccountStatus = 'active' | 'inactive' | 'locked' | 'suspended' | 'pending_verification'
```

### 状态管理
```typescript
interface AuthState {
  // 用户状态
  isAuthenticated: boolean
  user: UserProfile | null
  token: string | null
  refreshToken: string | null
  sessionId: string | null
  
  // 登录状态
  isLogging: boolean
  loginAttempts: number
  lastLoginAttempt: string | null
  isLocked: boolean
  lockoutTime: string | null
  
  // 验证状态
  requiresCaptcha: boolean
  captchaId: string | null
  requiresMFA: boolean
  mfaMethods: MFAMethod[]
  currentMFAStep: string | null
  
  // 安全状态
  deviceTrusted: boolean
  securityAlerts: SecurityAlert[]
  riskLevel: 'low' | 'medium' | 'high'
  
  // UI状态
  loginType: LoginType
  showPassword: boolean
  rememberMe: boolean
  
  // 第三方登录
  oauthProviders: OAuthProvider[]
  oauthLoading: Record<OAuthProvider, boolean>
  
  // SSO配置
  ssoProviders: SSOConfig[]
  ssoEnabled: boolean
  
  // 错误状态
  error: string | null
  fieldErrors: Record<string, string>
  
  // 设备和环境
  deviceInfo: DeviceInfo | null
  clientConfig: ClientConfig
  
  // 首次登录流程
  isFirstLogin: boolean
  mustChangePassword: boolean
  passwordChangeRequired: boolean
}

interface AuthActions {
  // 基础登录
  login(credentials: LoginRequest): Promise<LoginResponse>
  logout(): Promise<void>
  refreshAccessToken(): Promise<void>
  
  // 密码管理
  changePassword(oldPassword: string, newPassword: string): Promise<void>
  resetPassword(email: string): Promise<void>
  confirmPasswordReset(token: string, newPassword: string): Promise<void>
  
  // 多因子认证
  setupMFA(method: MFAMethod): Promise<void>
  verifyMFA(code: string, method: string): Promise<void>
  disableMFA(method: string): Promise<void>
  
  // 验证码
  getCaptcha(): Promise<{ id: string, image: string }>
  refreshCaptcha(): Promise<void>
  
  // 第三方登录
  loginWithOAuth(provider: OAuthProvider): Promise<void>
  handleOAuthCallback(code: string, state: string): Promise<void>
  
  // SSO登录
  loginWithSSO(provider: SSOProvider): Promise<void>
  handleSSOCallback(token: string): Promise<void>
  
  // 设备管理
  trustDevice(): Promise<void>
  revokeDeviceTrust(deviceId: string): Promise<void>
  getDeviceList(): Promise<Device[]>
  
  // 会话管理
  getCurrentSession(): Promise<Session>
  getActiveSessions(): Promise<Session[]>
  revokeSession(sessionId: string): Promise<void>
  revokeAllSessions(): Promise<void>
  
  // 安全检查
  checkSecurityStatus(): Promise<SecurityStatus>
  reportSuspiciousActivity(details: string): Promise<void>
  
  // UI操作
  setLoginType(type: LoginType): void
  togglePasswordVisibility(): void
  setRememberMe(remember: boolean): void
  clearErrors(): void
  
  // 用户偏好
  updatePreferences(preferences: Partial<UserPreferences>): Promise<void>
  
  // 账户验证
  sendEmailVerification(): Promise<void>
  verifyEmail(token: string): Promise<void>
  sendPhoneVerification(): Promise<void>
  verifyPhone(code: string): Promise<void>
}
```

## 页面交互逻辑

### 基础登录流程
```typescript
// 执行登录
async function handleLogin() {
  clearErrors()
  
  // 验证表单
  const validation = validateLoginForm()
  if (!validation.valid) {
    setFieldErrors(validation.errors)
    return
  }
  
  isLogging.value = true
  
  try {
    const loginData: LoginRequest = {
      [loginType.value === 'email' ? 'email' : 'username']: credentials.username,
      password: credentials.password,
      captcha: captchaCode.value,
      captchaId: captchaId.value,
      rememberMe: rememberMe.value,
      loginType: loginType.value,
      deviceInfo: await getDeviceInfo()
    }
    
    const response = await authStore.login(loginData)
    
    if (response.success) {
      if (response.requiresMFA) {
        // 需要多因子认证
        setupMFAVerification(response.mfaMethods)
      } else if (response.requiresDeviceVerification) {
        // 需要设备验证
        setupDeviceVerification(response.verificationMethods)
      } else {
        // 登录成功
        handleLoginSuccess(response)
      }
    } else {
      handleLoginError(response)
    }
    
  } catch (error) {
    handleLoginException(error)
  } finally {
    isLogging.value = false
  }
}

// 处理登录成功
function handleLoginSuccess(response: LoginResponse) {
  showSuccessMessage('登录成功，欢迎回来！')
  
  // 检查首次登录
  if (response.isFirstLogin) {
    showWelcomeModal()
  }
  
  // 检查密码过期
  if (response.mustChangePassword) {
    navigateToPasswordChange()
    return
  }
  
  // 保存登录状态
  if (rememberMe.value) {
    localStorage.setItem('rememberMe', 'true')
    localStorage.setItem('lastUsername', credentials.username)
  }
  
  // 跳转到目标页面
  const redirectUrl = route.query.redirect as string || '/dashboard'
  router.push(redirectUrl)
}

// 处理登录失败
function handleLoginError(response: LoginResponse) {
  loginAttempts.value++
  lastLoginAttempt.value = new Date().toISOString()
  
  if (response.errorCode === 'INVALID_CREDENTIALS') {
    setError('用户名或密码错误')
    
    if (response.remainingAttempts <= 3) {
      showWarningMessage(`剩余尝试次数: ${response.remainingAttempts}`)
    }
  } else if (response.errorCode === 'ACCOUNT_LOCKED') {
    setError('账户已被锁定，请稍后再试')
    showAccountLockedModal(response.lockoutTime)
  } else if (response.errorCode === 'CAPTCHA_REQUIRED') {
    requiresCaptcha.value = true
    await refreshCaptcha()
  } else {
    setError(response.error || '登录失败，请重试')
  }
  
  // 安全检查建议
  if (response.securityCheck?.riskLevel === 'high') {
    showSecurityWarning(response.securityCheck.recommendations)
  }
}

// 表单验证
function validateLoginForm(): ValidationResult {
  const errors: Record<string, string> = {}
  
  // 用户名/邮箱验证
  if (!credentials.username) {
    errors.username = '请输入用户名或邮箱'
  } else if (loginType.value === 'email' && !isValidEmail(credentials.username)) {
    errors.username = '请输入有效的邮箱地址'
  }
  
  // 密码验证
  if (!credentials.password) {
    errors.password = '请输入密码'
  } else if (credentials.password.length < 6) {
    errors.password = '密码长度至少6位'
  }
  
  // 验证码验证
  if (requiresCaptcha.value && !captchaCode.value) {
    errors.captcha = '请输入验证码'
  }
  
  return {
    valid: Object.keys(errors).length === 0,
    errors
  }
}
```

### 多因子认证流程
```typescript
// 设置MFA验证
function setupMFAVerification(methods: MFAMethod[]) {
  mfaMethods.value = methods
  requiresMFA.value = true
  
  // 优先选择已设置的方法
  const preferredMethod = methods.find(m => m.verified) || methods[0]
  currentMFAStep.value = preferredMethod.type
  
  if (preferredMethod.type === 'sms') {
    sendSMSCode(preferredMethod.phoneNumber)
  } else if (preferredMethod.type === 'email') {
    sendEmailCode(preferredMethod.email)
  }
  
  showMFADialog()
}

// 验证MFA代码
async function verifyMFACode() {
  if (!mfaCode.value) {
    setError('请输入验证码')
    return
  }
  
  try {
    const response = await authStore.verifyMFA(mfaCode.value, currentMFAStep.value)
    
    if (response.success) {
      requiresMFA.value = false
      showSuccessMessage('验证成功')
      handleLoginSuccess(response)
    } else {
      setError('验证码错误，请重试')
      mfaCode.value = ''
    }
  } catch (error) {
    setError('验证失败，请重试')
  }
}

// 发送短信验证码
async function sendSMSCode(phoneNumber: string) {
  try {
    await authService.sendSMSVerification(phoneNumber)
    showSuccessMessage('验证码已发送到您的手机')
    startCountdown()
  } catch (error) {
    showErrorMessage('发送验证码失败，请重试')
  }
}

// 倒计时控制
function startCountdown() {
  countdown.value = 60
  
  const timer = setInterval(() => {
    countdown.value--
    
    if (countdown.value <= 0) {
      clearInterval(timer)
      canResendCode.value = true
    }
  }, 1000)
}
```

### 第三方登录
```typescript
// OAuth登录
async function loginWithOAuth(provider: OAuthProvider) {
  oauthLoading.value[provider] = true
  
  try {
    // 获取OAuth授权URL
    const authUrl = await authService.getOAuthAuthUrl(provider, {
      redirectUri: getOAuthRedirectUri(provider),
      state: generateRandomState()
    })
    
    // 跳转到第三方授权页面
    window.location.href = authUrl
    
  } catch (error) {
    showErrorMessage(`${provider} 登录失败: ${error.message}`)
  } finally {
    oauthLoading.value[provider] = false
  }
}

// 处理OAuth回调
async function handleOAuthCallback() {
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  const state = urlParams.get('state')
  const error = urlParams.get('error')
  
  if (error) {
    showErrorMessage(`授权失败: ${error}`)
    return
  }
  
  if (!code || !state) {
    showErrorMessage('授权参数缺失')
    return
  }
  
  try {
    const response = await authStore.handleOAuthCallback(code, state)
    
    if (response.success) {
      handleLoginSuccess(response)
    } else {
      handleLoginError(response)
    }
  } catch (error) {
    showErrorMessage('处理授权回调失败')
  }
}

// SSO登录
async function loginWithSSO(provider: SSOProvider) {
  try {
    const ssoUrl = await authService.getSSOAuthUrl(provider)
    window.location.href = ssoUrl
  } catch (error) {
    showErrorMessage(`SSO登录失败: ${error.message}`)
  }
}
```

### 安全增强功能
```typescript
// 设备指纹识别
async function getDeviceInfo(): Promise<DeviceInfo> {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')
  ctx.textBaseline = 'top'
  ctx.font = '14px Arial'
  ctx.fillText('Device fingerprint', 2, 2)
  
  return {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    browser: getBrowserInfo(),
    browserVersion: getBrowserVersion(),
    os: getOSInfo(),
    osVersion: getOSVersion(),
    screen: {
      width: screen.width,
      height: screen.height,
      colorDepth: screen.colorDepth,
      pixelDepth: screen.pixelDepth
    },
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    language: navigator.language,
    fingerprint: canvas.toDataURL()
  }
}

// 检测可疑登录
function detectSuspiciousLogin(deviceInfo: DeviceInfo): SecurityAlert[] {
  const alerts: SecurityAlert[] = []
  
  // 检查新设备
  if (!deviceTrusted.value) {
    alerts.push({
      type: 'new_device',
      level: 'warning',
      message: '检测到新设备登录',
      recommendation: '如果这不是您的操作，请立即更改密码'
    })
  }
  
  // 检查异常时间
  const currentHour = new Date().getHours()
  if (currentHour < 6 || currentHour > 23) {
    alerts.push({
      type: 'unusual_time',
      level: 'info',
      message: '检测到异常时间登录',
      recommendation: '请确认这是您本人的操作'
    })
  }
  
  return alerts
}

// 风险评分计算
function calculateRiskScore(factors: RiskFactor[]): number {
  let score = 0
  
  factors.forEach(factor => {
    switch (factor.type) {
      case 'new_device':
        score += factor.weight * 30
        break
      case 'new_location':
        score += factor.weight * 25
        break
      case 'failed_attempts':
        score += factor.weight * 20
        break
      case 'unusual_time':
        score += factor.weight * 10
        break
    }
  })
  
  return Math.min(score, 100)
}

// 安全建议
function generateSecurityRecommendations(riskScore: number): string[] {
  const recommendations = []
  
  if (riskScore > 70) {
    recommendations.push('强烈建议启用两步验证')
    recommendations.push('建议立即更改密码')
    recommendations.push('检查最近的登录活动')
  } else if (riskScore > 40) {
    recommendations.push('建议启用两步验证')
    recommendations.push('定期更改密码')
  } else {
    recommendations.push('保持良好的安全习惯')
  }
  
  return recommendations
}
```

### 用户体验优化
```typescript
// 智能表单填充
function setupSmartFormFilling() {
  // 记住上次登录的用户名
  const rememberedUsername = localStorage.getItem('lastUsername')
  if (rememberedUsername && rememberMe.value) {
    credentials.username = rememberedUsername
  }
  
  // 自动检测登录类型
  watch(() => credentials.username, (newValue) => {
    if (newValue) {
      loginType.value = isValidEmail(newValue) ? 'email' : 'username'
    }
  })
}

// 键盘快捷键支持
function setupKeyboardShortcuts() {
  document.addEventListener('keydown', (event) => {
    // Enter键登录
    if (event.key === 'Enter' && !isLogging.value) {
      handleLogin()
    }
    
    // Escape键清除错误
    if (event.key === 'Escape') {
      clearErrors()
    }
    
    // Tab键在MFA输入框之间切换
    if (event.key === 'Tab' && requiresMFA.value) {
      event.preventDefault()
      switchMFAMethod()
    }
  })
}

// 密码强度检测
function checkPasswordStrength(password: string): PasswordStrength {
  let score = 0
  const feedback = []
  
  // 长度检查
  if (password.length >= 8) score += 20
  else feedback.push('密码长度至少8位')
  
  // 复杂度检查
  if (/[a-z]/.test(password)) score += 15
  if (/[A-Z]/.test(password)) score += 15
  if (/[0-9]/.test(password)) score += 15
  if (/[^a-zA-Z0-9]/.test(password)) score += 20
  
  // 常见密码检查
  if (commonPasswords.includes(password.toLowerCase())) {
    score = 0
    feedback.push('密码过于常见，请使用更复杂的密码')
  }
  
  let strength: 'weak' | 'medium' | 'strong'
  if (score < 40) strength = 'weak'
  else if (score < 70) strength = 'medium'
  else strength = 'strong'
  
  return { score, strength, feedback }
}

// 登录状态持久化
function setupLoginPersistence() {
  // 检查自动登录
  const autoLogin = localStorage.getItem('autoLogin')
  const savedToken = localStorage.getItem('authToken')
  
  if (autoLogin && savedToken) {
    authStore.validateToken(savedToken).then(isValid => {
      if (isValid) {
        router.push('/dashboard')
      } else {
        localStorage.removeItem('authToken')
        localStorage.removeItem('autoLogin')
      }
    })
  }
  
  // 监听页面可见性变化
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && isAuthenticated.value) {
      // 页面重新可见时检查token有效性
      authStore.validateCurrentSession()
    }
  })
}
```

## 响应式设计适配

### 桌面端布局 (≥1200px)
- 左右分栏布局，左侧展示平台特性
- 右侧居中的登录表单
- 完整的功能展示和提示信息

### 平板端布局 (768px-1199px)
- 简化的左侧内容区域
- 登录表单适当放大
- 保留主要功能入口

### 移动端布局 (<768px)
- 全屏单栏布局
- 顶部logo和标题
- 简化的登录选项
- 底部链接菜单

```typescript
// 响应式布局适配
const isMobile = computed(() => screenWidth.value < 768)
const isTablet = computed(() => screenWidth.value >= 768 && screenWidth.value < 1200)

const loginContainerStyle = computed(() => ({
  flexDirection: isMobile.value ? 'column' : 'row',
  padding: isMobile.value ? '20px' : '0'
}))

const formWidth = computed(() => {
  if (isMobile.value) return '100%'
  if (isTablet.value) return '400px'
  return '450px'
})

const showLeftPanel = computed(() => !isMobile.value)
const showFeatureList = computed(() => !isMobile.value)
```

## 安全考虑

### 密码安全
```typescript
// 密码加密传输
function encryptPassword(password: string): string {
  // 使用RSA公钥加密密码
  const publicKey = getServerPublicKey()
  return RSA.encrypt(password, publicKey)
}

// 防止密码泄露
function clearPasswordFromMemory() {
  // 清除表单中的密码
  credentials.password = ''
  
  // 清除可能的密码缓存
  document.querySelectorAll('input[type="password"]').forEach(input => {
    input.value = ''
  })
}

// 密码复杂度验证
function validatePasswordComplexity(password: string): boolean {
  const requirements = [
    /.{8,}/, // 至少8位
    /[a-z]/, // 小写字母
    /[A-Z]/, // 大写字母  
    /[0-9]/, // 数字
    /[^a-zA-Z0-9]/ // 特殊字符
  ]
  
  return requirements.filter(req => req.test(password)).length >= 3
}
```

### 防护机制
```typescript
// CSRF防护
function setupCSRFProtection() {
  const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
  if (token) {
    axios.defaults.headers.common['X-CSRF-TOKEN'] = token
  }
}

// 暴力破解防护
function setupBruteForceProtection() {
  let attemptCount = 0
  let lastAttemptTime = 0
  
  return function rateLimit() {
    const now = Date.now()
    
    if (now - lastAttemptTime < 1000) { // 1秒内不允许重复请求
      throw new Error('请求过于频繁，请稍后再试')
    }
    
    attemptCount++
    lastAttemptTime = now
    
    if (attemptCount > 5) {
      throw new Error('尝试次数过多，请稍后再试')
    }
  }
}

// XSS防护
function sanitizeInput(input: string): string {
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
}

// 安全日志记录
async function logSecurityEvent(event: SecurityEvent) {
  await securityService.logEvent({
    type: event.type,
    severity: event.severity,
    details: event.details,
    userId: event.userId,
    ipAddress: getClientIPAddress(),
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString()
  })
}