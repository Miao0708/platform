// 导出所有类型定义
export * from './models'
export * from './api'

// 通用工具类型
export type Nullable<T> = T | null
export type Optional<T> = T | undefined
export type Arrayable<T> = T | T[]

// 组件 Props 类型
export interface BaseComponentProps {
  class?: string
  style?: string | Record<string, any>
}

// 表格列配置类型
export interface TableColumn {
  prop: string
  label: string
  width?: string | number
  minWidth?: string | number
  fixed?: boolean | 'left' | 'right'
  sortable?: boolean
  formatter?: (row: any, column: any, cellValue: any) => string
}

// 表单验证规则类型
export interface FormRule {
  required?: boolean
  message?: string
  trigger?: string | string[]
  validator?: (rule: any, value: any, callback: any) => void
}

// 路由元信息类型
export interface RouteMeta {
  title?: string
  icon?: string
  requiresAuth?: boolean
  roles?: string[]
  hidden?: boolean
}
