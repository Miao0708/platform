import { ref, onUnmounted } from 'vue'

/**
 * 轮询Hook
 * @param callback 轮询执行的回调函数
 * @param interval 轮询间隔（毫秒）
 * @param immediate 是否立即执行
 */
export function usePolling(
  callback: () => Promise<boolean> | boolean,
  interval: number = 3000,
  immediate: boolean = true
) {
  const isPolling = ref(false)
  let timer: NodeJS.Timeout | null = null

  const start = async () => {
    if (isPolling.value) return
    
    isPolling.value = true
    
    if (immediate) {
      const shouldContinue = await callback()
      if (!shouldContinue) {
        stop()
        return
      }
    }
    
    timer = setInterval(async () => {
      try {
        const shouldContinue = await callback()
        if (!shouldContinue) {
          stop()
        }
      } catch (error) {
        console.error('Polling error:', error)
        stop()
      }
    }, interval)
  }

  const stop = () => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    isPolling.value = false
  }

  // 组件卸载时自动停止轮询
  onUnmounted(() => {
    stop()
  })

  return {
    isPolling,
    start,
    stop
  }
}
