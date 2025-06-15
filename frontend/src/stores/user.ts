import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, authUtils } from '@/api'

export interface UserInfo {
  id: number
  username: string
  isSuperuser: boolean
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)
  const isLoading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)
  const isAdmin = computed(() => userInfo.value?.isSuperuser || false)

  // 方法
  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const setUserInfo = (info: UserInfo) => {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }

  const login = async (username: string, password: string) => {
    try {
      isLoading.value = true

      console.log('正在调用登录API...', { username })
      const response = await authApi.login({ username, password })
      console.log('登录API响应:', response)

      // 保存Token和用户信息
      setToken(response.accessToken)
      setUserInfo(response.user)

      return true
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    // 清除本地数据
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  const initializeAuth = () => {
    // 从localStorage恢复用户信息
    const savedToken = localStorage.getItem('token')
    const savedUserInfo = localStorage.getItem('userInfo')

    if (savedToken && savedUserInfo) {
      try {
        token.value = savedToken
        userInfo.value = JSON.parse(savedUserInfo)
      } catch (error) {
        console.error('Failed to restore user info:', error)
        // 如果解析失败，清除无效数据
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
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
    isAdmin,

    // 方法
    setToken,
    setUserInfo,
    login,
    logout,
    initializeAuth
  }
})
