import { api } from './index'

// 仪表盘统计数据接口
export interface DashboardStats {
  total_tasks: number
  completed_tasks: number
  running_tasks: number
  failed_tasks: number
  total_tokens_used: number
  recent_tasks: RecentTask[]
}

// 最近任务接口
export interface RecentTask {
  id: string
  name: string
  type: 'code_diff' | 'requirement_parse' | 'pipeline'
  status: 'pending' | 'running' | 'completed' | 'failed'
  created_at: string
}

// 图表数据接口
export interface ChartData {
  daily_task_trend: DailyTaskTrend[]
  task_status_distribution: TaskStatusDistribution[]
  model_usage_stats: ModelUsageStats[]
}

// 每日任务趋势
export interface DailyTaskTrend {
  date: string
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
}

// 任务状态分布
export interface TaskStatusDistribution {
  status: string
  count: number
  percentage: number
}

// AI模型使用统计
export interface ModelUsageStats {
  model_name: string
  provider: string
  usage_count: number
  total_tokens: number
  is_active: boolean
}

// 仪表盘API
export const dashboardApi = {
  // 获取仪表盘统计数据
  getStats: (): Promise<DashboardStats> => 
    api.get('/dashboard/stats'),

  // 获取图表数据
  getCharts: (): Promise<ChartData> => 
    api.get('/dashboard/stats/charts'),

  // 获取任务趋势（自定义时间范围）
  getTaskTrend: (params: { 
    start_date: string
    end_date: string
    granularity?: 'hour' | 'day' | 'week' | 'month'
  }) => 
    api.get('/dashboard/trends/tasks', { params }),

  // 获取Token使用趋势
  getTokenTrend: (params: { 
    start_date: string
    end_date: string
    model_id?: string
  }) => 
    api.get('/dashboard/trends/tokens', { params }),

  // 获取错误统计
  getErrorStats: (params?: { 
    start_date?: string
    end_date?: string
  }) => 
    api.get('/dashboard/errors', { params }),

  // 导出统计报告
  exportReport: (params: {
    type: 'daily' | 'weekly' | 'monthly'
    start_date: string
    end_date: string
    format: 'pdf' | 'excel' | 'csv'
  }) => 
    api.get('/dashboard/export', { 
      params,
      responseType: 'blob'
    })
}

// 仪表盘工具函数
export const dashboardUtils = {
  // 计算完成率
  calculateCompletionRate: (completed: number, total: number): number => {
    if (total === 0) return 0
    return Math.round((completed / total) * 100)
  },

  // 计算失败率
  calculateFailureRate: (failed: number, total: number): number => {
    if (total === 0) return 0
    return Math.round((failed / total) * 100)
  },

  // 格式化数字（添加千分位分隔符）
  formatNumber: (num: number): string => {
    return num.toLocaleString()
  },

  // 格式化Token数量
  formatTokens: (tokens: number): string => {
    if (tokens < 1000) {
      return tokens.toString()
    } else if (tokens < 1000000) {
      return (tokens / 1000).toFixed(1) + 'K'
    } else {
      return (tokens / 1000000).toFixed(1) + 'M'
    }
  },

  // 格式化百分比
  formatPercentage: (value: number, total: number): string => {
    if (total === 0) return '0%'
    return ((value / total) * 100).toFixed(1) + '%'
  },

  // 获取状态颜色
  getStatusColor: (status: string): string => {
    const colorMap: Record<string, string> = {
      pending: '#909399',
      running: '#409EFF',
      completed: '#67C23A',
      failed: '#F56C6C'
    }
    return colorMap[status] || '#909399'
  },

  // 获取任务类型显示名称
  getTaskTypeName: (type: string): string => {
    const typeMap: Record<string, string> = {
      code_diff: '代码差异',
      requirement_parse: '需求解析',
      pipeline: '流水线任务'
    }
    return typeMap[type] || type
  },

  // 计算增长率
  calculateGrowthRate: (current: number, previous: number): number => {
    if (previous === 0) return current > 0 ? 100 : 0
    return Math.round(((current - previous) / previous) * 100)
  },

  // 格式化增长率显示
  formatGrowthRate: (rate: number): string => {
    const sign = rate > 0 ? '+' : ''
    return `${sign}${rate}%`
  },

  // 获取增长率颜色
  getGrowthRateColor: (rate: number): string => {
    if (rate > 0) return '#67C23A'
    if (rate < 0) return '#F56C6C'
    return '#909399'
  },

  // 处理图表数据
  processChartData: (rawData: any[], type: 'trend' | 'distribution') => {
    if (type === 'trend') {
      return {
        labels: rawData.map(item => item.date),
        datasets: [
          {
            label: '总任务',
            data: rawData.map(item => item.total_tasks),
            borderColor: '#409EFF',
            backgroundColor: 'rgba(64, 158, 255, 0.1)',
          },
          {
            label: '完成任务',
            data: rawData.map(item => item.completed_tasks),
            borderColor: '#67C23A',
            backgroundColor: 'rgba(103, 194, 58, 0.1)',
          },
          {
            label: '失败任务',
            data: rawData.map(item => item.failed_tasks),
            borderColor: '#F56C6C',
            backgroundColor: 'rgba(245, 108, 108, 0.1)',
          }
        ]
      }
    } else {
      return {
        labels: rawData.map(item => item.status),
        datasets: [
          {
            data: rawData.map(item => item.count),
            backgroundColor: [
              '#409EFF',
              '#67C23A',
              '#E6A23C',
              '#F56C6C',
              '#909399'
            ],
          }
        ]
      }
    }
  }
}

export default dashboardApi
