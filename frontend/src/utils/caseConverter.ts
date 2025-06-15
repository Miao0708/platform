/**
 * camelCase 和 snake_case 转换工具
 * 用于前后端数据格式标准化
 */

/**
 * 将snake_case转换为camelCase
 */
export function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
}

/**
 * 将camelCase转换为snake_case
 */
export function toSnakeCase(str: string): string {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
}

/**
 * 递归地将对象的所有键从snake_case转换为camelCase
 */
export function convertKeysToCamelCase(obj: any): any {
  if (obj === null || obj === undefined) {
    return obj
  }

  if (Array.isArray(obj)) {
    return obj.map(convertKeysToCamelCase)
  }

  if (typeof obj === 'object' && obj.constructor === Object) {
    const result: any = {}
    for (const [key, value] of Object.entries(obj)) {
      const camelKey = toCamelCase(key)
      result[camelKey] = convertKeysToCamelCase(value)
    }
    return result
  }

  return obj
}

/**
 * 递归地将对象的所有键从camelCase转换为snake_case
 */
export function convertKeysToSnakeCase(obj: any): any {
  if (obj === null || obj === undefined) {
    return obj
  }

  if (Array.isArray(obj)) {
    return obj.map(convertKeysToSnakeCase)
  }

  if (typeof obj === 'object' && obj.constructor === Object) {
    const result: any = {}
    for (const [key, value] of Object.entries(obj)) {
      const snakeKey = toSnakeCase(key)
      result[snakeKey] = convertKeysToSnakeCase(value)
    }
    return result
  }

  return obj
}

/**
 * 检查字符串是否为camelCase格式
 */
export function isCamelCase(str: string): boolean {
  return /^[a-z][a-zA-Z0-9]*$/.test(str) && /[A-Z]/.test(str)
}

/**
 * 检查字符串是否为snake_case格式
 */
export function isSnakeCase(str: string): boolean {
  return /^[a-z][a-z0-9_]*$/.test(str) && /_/.test(str)
} 