import { api } from './index'

// 用户信息接口 - 简化版本
export interface UserInfo {
  id: string
  username: string
  email: string
  nickname?: string
  avatar?: string
  created_at: string
}

// 更新用户信息请求 - 简化版本
export interface UpdateUserRequest {
  email?: string
  nickname?: string
}

// 修改密码请求
export interface ChangePasswordRequest {
  current_password: string
  new_password: string
  confirm_password: string
}

// 用户管理API - 简化接口路径
export const usersApi = {
  // 获取当前用户信息
  get: (): Promise<UserInfo> =>
    api.get('/user/get'),

  // 更新当前用户信息
  update: (data: UpdateUserRequest): Promise<UserInfo> =>
    api.post('/user/update', data),

  // 修改用户密码
  changePassword: (data: ChangePasswordRequest) =>
    api.post('/user/change-password', data),

  // 上传用户头像
  uploadAvatar: (file: File) => {
    const formData = new FormData()
    formData.append('avatar', file)
    return api.post('/user/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

// 用户工具函数
export const userUtils = {
  // 保存用户信息到localStorage
  saveUserInfo: (userInfo: UserInfo) => {
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
  },

  // 获取用户信息
  getUserInfo: (): UserInfo | null => {
    const userInfoStr = localStorage.getItem('userInfo')
    if (userInfoStr) {
      try {
        return JSON.parse(userInfoStr)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        return null
      }
    }
    return null
  },

  // 清除用户信息
  clearUserInfo: () => {
    localStorage.removeItem('userInfo')
  },

  // 获取用户显示名称
  getDisplayName: (userInfo: UserInfo): string => {
    return userInfo.full_name || userInfo.username
  },

  // 获取用户头像URL
  getAvatarUrl: (userInfo: UserInfo): string => {
    return userInfo.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${userInfo.username}`
  },

  // 格式化最后登录时间
  formatLastLoginTime: (lastLoginAt?: string): string => {
    if (!lastLoginAt) return '从未登录'
    
    const date = new Date(lastLoginAt)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) {
      return '今天'
    } else if (diffDays === 1) {
      return '昨天'
    } else if (diffDays < 7) {
      return `${diffDays}天前`
    } else {
      return date.toLocaleDateString()
    }
  },

  // 验证用户信息
  validateUserInfo: (data: UpdateUserRequest): string[] => {
    const errors: string[] = []
    
    if (data.email && !isValidEmail(data.email)) {
      errors.push('邮箱格式不正确')
    }
    
    if (data.full_name && data.full_name.length > 50) {
      errors.push('姓名长度不能超过50个字符')
    }
    
    if (data.bio && data.bio.length > 500) {
      errors.push('个人简介长度不能超过500个字符')
    }
    
    return errors
  },

  // 验证密码修改
  validatePasswordChange: (data: ChangePasswordRequest): string[] => {
    const errors: string[] = []
    
    if (!data.current_password) {
      errors.push('请输入当前密码')
    }
    
    if (!data.new_password) {
      errors.push('请输入新密码')
    } else if (data.new_password.length < 6) {
      errors.push('新密码长度不能少于6位')
    }
    
    if (data.new_password !== data.confirm_password) {
      errors.push('新密码与确认密码不匹配')
    }
    
    if (data.current_password === data.new_password) {
      errors.push('新密码不能与当前密码相同')
    }
    
    return errors
  }
}

// 辅助函数
function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export default usersApi
