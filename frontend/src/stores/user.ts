import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, usersApi, authUtils, userUtils } from '@/api'

export interface UserInfo {
  id: string
  username: string
  roles: string[]
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
      console.log('正在调用登录API...', { username })
      const response = await authApi.login({ username, password })
      console.log('登录API响应:', response)

      // 保存Token
      authUtils.saveToken(response.access_token)
      setToken(response.access_token)

      // 确定用户角色（通过用户名判断）
      const userRole = username === 'admin' ? 'admin' : 'user'

      // 转换用户信息格式
      const userInfo: UserInfo = {
        id: response.user.id.toString(),
        username: response.user.username,
        roles: [userRole] // 根据用户名确定角色
      }

      console.log('用户信息:', userInfo)
      setUserInfo(userInfo)
      userUtils.saveUserInfo(userInfo)

      console.log('登录状态:', isLoggedIn.value)
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
