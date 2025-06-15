import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, usersApi, authUtils, userUtils } from '@/api'

export interface UserInfo {
  id: string
  username: string
  email: string
  avatar?: string
  roles: string[]
  nickname?: string
  phone?: string
  department?: string
  position?: string
  lastLoginTime?: string
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)
  const isLoading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)
  const hasRole = computed(() => (role: string) => {
    return userInfo.value?.roles.includes(role) || false
  })

  // 方法
  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const setUserInfo = (info: UserInfo) => {
    userInfo.value = info
  }

  const login = async (username: string, password: string) => {
    try {
      isLoading.value = true

      // 调用真实的登录API
      const response = await authApi.login({ username, password })

      // 保存Token
      authUtils.saveToken(response.access_token)
      setToken(response.access_token)

      // 转换用户信息格式
      const userInfo: UserInfo = {
        id: response.user.id,
        username: response.user.username,
        email: response.user.email,
        nickname: response.user.nickname,
        avatar: response.user.avatar,
        roles: [response.user.role || 'user'], // 默认角色
        department: '技术部', // 默认部门
        position: response.user.role === 'admin' ? '系统管理员' : '开发工程师'
      }

      setUserInfo(userInfo)
      userUtils.saveUserInfo(userInfo)

      return true
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      // 调用登出API
      await authApi.logout()
    } catch (error) {
      console.error('Logout API failed:', error)
      // 即使API失败也要清除本地数据
    } finally {
      // 清除本地数据
      token.value = ''
      userInfo.value = null
      authUtils.clearToken()
      userUtils.clearUserInfo()
    }
  }

  const refreshUserInfo = async () => {
    try {
      // 调用获取用户信息API
      const response = await usersApi.get()

      // 转换用户信息格式
      const userInfo: UserInfo = {
        id: response.id,
        username: response.username,
        email: response.email,
        nickname: response.nickname,
        avatar: response.avatar,
        roles: ['user'], // 默认角色
        department: '技术部',
        position: '开发工程师'
      }

      setUserInfo(userInfo)
      userUtils.saveUserInfo(userInfo)
    } catch (error) {
      console.error('Refresh user info failed:', error)
      logout()
    }
  }

  const initializeAuth = () => {
    // 从localStorage恢复token和用户信息
    const savedToken = authUtils.getToken()
    const savedUserInfo = userUtils.getUserInfo()

    if (savedToken && savedUserInfo) {
      try {
        token.value = savedToken
        userInfo.value = savedUserInfo
      } catch (error) {
        console.error('Failed to restore user info:', error)
        // 如果解析失败，清除无效数据
        authUtils.clearToken()
        userUtils.clearUserInfo()
      }
    }
  }

  return {
    // 状态
    token,
    userInfo,
    isLoading,

    // 计算属性
    isLoggedIn,
    hasRole,

    // 方法
    setToken,
    setUserInfo,
    login,
    logout,
    refreshUserInfo,
    initializeAuth
  }
})
