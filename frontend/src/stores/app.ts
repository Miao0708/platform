import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 侧边栏状态
  const sidebarCollapsed = ref(false)
  
  // 全局加载状态
  const globalLoading = ref(false)
  
  // 主题设置
  const theme = ref<'light' | 'dark'>('light')
  
  // 语言设置
  const locale = ref('zh-CN')

  // 方法
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  const setSidebarCollapsed = (collapsed: boolean) => {
    sidebarCollapsed.value = collapsed
  }

  const setGlobalLoading = (loading: boolean) => {
    globalLoading.value = loading
  }

  const setTheme = (newTheme: 'light' | 'dark') => {
    theme.value = newTheme
    // 可以在这里添加主题切换逻辑
    document.documentElement.setAttribute('data-theme', newTheme)
  }

  const setLocale = (newLocale: string) => {
    locale.value = newLocale
  }

  const initializeApp = () => {
    // 从localStorage恢复应用设置
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark'
    if (savedTheme) {
      setTheme(savedTheme)
    }

    const savedLocale = localStorage.getItem('locale')
    if (savedLocale) {
      setLocale(savedLocale)
    }

    const savedSidebarState = localStorage.getItem('sidebarCollapsed')
    if (savedSidebarState) {
      setSidebarCollapsed(JSON.parse(savedSidebarState))
    }
  }

  return {
    // 状态
    sidebarCollapsed,
    globalLoading,
    theme,
    locale,

    // 方法
    toggleSidebar,
    setSidebarCollapsed,
    setGlobalLoading,
    setTheme,
    setLocale,
    initializeApp
  }
})
