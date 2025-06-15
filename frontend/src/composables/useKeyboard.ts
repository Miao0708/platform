import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export interface KeyboardShortcut {
  key: string
  ctrl?: boolean
  alt?: boolean
  shift?: boolean
  meta?: boolean
  action: () => void
  description: string
}

export function useKeyboard() {
  const router = useRouter()

  // 安全的路由跳转函数
  const safeNavigate = (path: string) => {
    try {
      console.log(`快捷键导航到: ${path}`)
      router.push(path)
    } catch (error) {
      console.error('快捷键导航失败:', error)
    }
  }
  
  // 预定义的快捷键
  const shortcuts: KeyboardShortcut[] = [
    {
      key: 'k',
      ctrl: true,
      action: () => {
        // 打开全局搜索
        ElMessage.info('全局搜索功能开发中...')
      },
      description: 'Ctrl + K: 全局搜索'
    },
    {
      key: 'h',
      ctrl: true,
      action: () => safeNavigate('/dashboard'),
      description: 'Ctrl + H: 返回首页'
    },
    {
      key: 'a',
      ctrl: true,
      shift: true,
      action: () => safeNavigate('/ai-chat'),
      description: 'Ctrl + Shift + A: 打开AI助手'
    },
    {
      key: 'r',
      ctrl: true,
      shift: true,
      action: () => safeNavigate('/requirements/list'),
      description: 'Ctrl + Shift + R: 需求管理'
    },
    {
      key: 'd',
      ctrl: true,
      shift: true,
      action: () => safeNavigate('/code-diff/tasks'),
      description: 'Ctrl + Shift + D: 代码Diff'
    },
    {
      key: 'p',
      ctrl: true,
      shift: true,
      action: () => safeNavigate('/pipelines/tasks'),
      description: 'Ctrl + Shift + P: 流水线'
    },
    {
      key: 'c',
      ctrl: true,
      shift: true,
      action: () => safeNavigate('/configuration'),
      description: 'Ctrl + Shift + C: 基础配置'
    },
    {
      key: 't',
      ctrl: true,
      shift: true,
      action: () => safeNavigate('/test-points/list'),
      description: 'Ctrl + Shift + T: 测试点管理'
    },
    {
      key: '/',
      ctrl: true,
      action: () => {
        showShortcutHelp()
      },
      description: 'Ctrl + /: 显示快捷键帮助'
    }
  ]
  
  // 显示快捷键帮助
  const showShortcutHelp = () => {
    const helpText = shortcuts.map(s => s.description).join('\n')
    ElMessage({
      message: `快捷键帮助:\n${helpText}`,
      type: 'info',
      duration: 5000,
      showClose: true
    })
  }
  
  // 检查快捷键是否匹配
  const isShortcutMatch = (event: KeyboardEvent, shortcut: KeyboardShortcut): boolean => {
    return event.key.toLowerCase() === shortcut.key.toLowerCase() &&
           event.ctrlKey === !!shortcut.ctrl &&
           event.altKey === !!shortcut.alt &&
           event.shiftKey === !!shortcut.shift &&
           event.metaKey === !!shortcut.meta
  }
  
  // 处理键盘事件
  const handleKeyDown = (event: KeyboardEvent) => {
    // 如果焦点在输入框中，不处理快捷键（除了特殊情况）
    const activeElement = document.activeElement
    const isInputFocused = activeElement && (
      activeElement.tagName === 'INPUT' ||
      activeElement.tagName === 'TEXTAREA' ||
      activeElement.contentEditable === 'true'
    )
    
    // 在输入框中只处理特定快捷键
    if (isInputFocused) {
      const allowedInInput = ['k', '/'] // Ctrl+K 搜索和 Ctrl+/ 帮助
      const matchedShortcut = shortcuts.find(shortcut => 
        isShortcutMatch(event, shortcut) && allowedInInput.includes(shortcut.key)
      )
      
      if (matchedShortcut) {
        event.preventDefault()
        matchedShortcut.action()
      }
      return
    }
    
    // 查找匹配的快捷键
    const matchedShortcut = shortcuts.find(shortcut => isShortcutMatch(event, shortcut))
    
    if (matchedShortcut) {
      event.preventDefault()
      matchedShortcut.action()
    }
  }
  
  // 注册快捷键
  const registerShortcuts = () => {
    document.addEventListener('keydown', handleKeyDown)
  }
  
  // 注销快捷键
  const unregisterShortcuts = () => {
    document.removeEventListener('keydown', handleKeyDown)
  }
  
  // 添加自定义快捷键
  const addShortcut = (shortcut: KeyboardShortcut) => {
    shortcuts.push(shortcut)
  }
  
  // 移除快捷键
  const removeShortcut = (key: string) => {
    const index = shortcuts.findIndex(s => s.key === key)
    if (index > -1) {
      shortcuts.splice(index, 1)
    }
  }
  
  // 生命周期钩子
  onMounted(() => {
    registerShortcuts()
  })
  
  onUnmounted(() => {
    unregisterShortcuts()
  })
  
  return {
    shortcuts,
    addShortcut,
    removeShortcut,
    showShortcutHelp,
    registerShortcuts,
    unregisterShortcuts
  }
}

// 专门用于AI助手的快捷键
export function useAIChatKeyboard() {
  const shortcuts: KeyboardShortcut[] = [
    {
      key: 'Enter',
      ctrl: true,
      action: () => {
        // 发送消息 - 这个需要在组件中具体实现
        const event = new CustomEvent('ai-send-message')
        document.dispatchEvent(event)
      },
      description: 'Ctrl + Enter: 发送消息'
    },
    {
      key: 'n',
      ctrl: true,
      action: () => {
        // 新建对话
        const event = new CustomEvent('ai-new-conversation')
        document.dispatchEvent(event)
      },
      description: 'Ctrl + N: 新建对话'
    },
    {
      key: 'l',
      ctrl: true,
      action: () => {
        // 清空当前对话
        const event = new CustomEvent('ai-clear-conversation')
        document.dispatchEvent(event)
      },
      description: 'Ctrl + L: 清空对话'
    }
  ]
  
  const handleKeyDown = (event: KeyboardEvent) => {
    const matchedShortcut = shortcuts.find(shortcut => {
      return event.key === shortcut.key &&
             event.ctrlKey === !!shortcut.ctrl &&
             event.altKey === !!shortcut.alt &&
             event.shiftKey === !!shortcut.shift &&
             event.metaKey === !!shortcut.meta
    })
    
    if (matchedShortcut) {
      event.preventDefault()
      matchedShortcut.action()
    }
  }
  
  onMounted(() => {
    document.addEventListener('keydown', handleKeyDown)
  })
  
  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeyDown)
  })
  
  return {
    shortcuts
  }
}

// 专门用于编辑器的快捷键
export function useEditorKeyboard() {
  const shortcuts: KeyboardShortcut[] = [
    {
      key: 's',
      ctrl: true,
      action: () => {
        // 保存文档
        const event = new CustomEvent('editor-save')
        document.dispatchEvent(event)
      },
      description: 'Ctrl + S: 保存文档'
    },
    {
      key: 'o',
      ctrl: true,
      shift: true,
      action: () => {
        // AI优化
        const event = new CustomEvent('editor-ai-optimize')
        document.dispatchEvent(event)
      },
      description: 'Ctrl + Shift + O: AI优化'
    }
  ]
  
  const handleKeyDown = (event: KeyboardEvent) => {
    const matchedShortcut = shortcuts.find(shortcut => {
      return event.key.toLowerCase() === shortcut.key.toLowerCase() &&
             event.ctrlKey === !!shortcut.ctrl &&
             event.altKey === !!shortcut.alt &&
             event.shiftKey === !!shortcut.shift &&
             event.metaKey === !!shortcut.meta
    })
    
    if (matchedShortcut) {
      event.preventDefault()
      matchedShortcut.action()
    }
  }
  
  onMounted(() => {
    document.addEventListener('keydown', handleKeyDown)
  })
  
  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeyDown)
  })
  
  return {
    shortcuts
  }
}
