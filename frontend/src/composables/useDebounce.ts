import { ref, watch, type Ref } from 'vue'

/**
 * 防抖Hook
 * @param value 需要防抖的值
 * @param delay 防抖延迟时间（毫秒）
 */
export function useDebounce<T>(value: Ref<T>, delay: number = 300) {
  const debouncedValue = ref<T>(value.value) as Ref<T>
  let timer: NodeJS.Timeout | null = null

  watch(
    value,
    (newValue) => {
      if (timer) {
        clearTimeout(timer)
      }
      
      timer = setTimeout(() => {
        debouncedValue.value = newValue
      }, delay)
    },
    { immediate: true }
  )

  return debouncedValue
}

/**
 * 防抖函数Hook
 * @param fn 需要防抖的函数
 * @param delay 防抖延迟时间（毫秒）
 */
export function useDebounceFn<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
) {
  let timer: NodeJS.Timeout | null = null

  const debouncedFn = (...args: Parameters<T>) => {
    if (timer) {
      clearTimeout(timer)
    }
    
    timer = setTimeout(() => {
      fn(...args)
    }, delay)
  }

  const cancel = () => {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  }

  return {
    debouncedFn,
    cancel
  }
}
