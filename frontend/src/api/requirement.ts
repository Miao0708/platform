/**
 * 需求管理API接口
 */
import { api } from './index'
import type {
  RequirementDocument,
  CreateRequirementDocumentRequest,
  UpdateRequirementDocumentRequest,
  RequirementAnalysisTask,
  CreateRequirementAnalysisTaskRequest,
  RequirementTestTask,
  CreateRequirementTestTaskRequest,
  RequirementDocumentListParams,
  RequirementTestTaskListParams,
  SupportedFileTypesResponse
} from '@/types/requirement'

const BASE_URL = '/requirement-management'

// ===== 需求文档管理 =====

/**
 * 获取需求文档列表
 */
export function getRequirementDocuments(params?: RequirementDocumentListParams) {
  return api.get<RequirementDocument[]>(`${BASE_URL}/documents`, { params })
}

/**
 * 创建需求文档（手动输入）
 */
export function createRequirementDocument(data: CreateRequirementDocumentRequest) {
  return api.post<RequirementDocument>(`${BASE_URL}/documents`, data)
}

/**
 * 上传需求文件
 */
export function uploadRequirementFile(formData: FormData) {
  return api.post<RequirementDocument>(`${BASE_URL}/documents/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取需求文档详情
 */
export function getRequirementDocument(id: number) {
  return api.get<RequirementDocument>(`${BASE_URL}/documents/${id}`)
}

/**
 * 更新需求文档
 */
export function updateRequirementDocument(id: number, data: UpdateRequirementDocumentRequest) {
  return api.put<RequirementDocument>(`${BASE_URL}/documents/${id}`, data)
}

/**
 * 删除需求文档
 */
export function deleteRequirementDocument(id: number) {
  return api.delete(`${BASE_URL}/documents/${id}`)
}

/**
 * 跳过解析，直接优化需求
 */
export function skipToOptimizeRequirement(id: number, promptTemplateId: number, modelConfigId: number) {
  const formData = new FormData()
  formData.append('prompt_template_id', promptTemplateId.toString())
  formData.append('model_config_id', modelConfigId.toString())
  
  return api.post<RequirementDocument>(`${BASE_URL}/documents/${id}/skip-to-optimize`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// ===== 需求分析任务管理 =====

/**
 * 创建需求分析任务
 */
export function createRequirementAnalysisTask(documentId: number, data: CreateRequirementAnalysisTaskRequest) {
  return api.post<RequirementAnalysisTask>(`${BASE_URL}/documents/${documentId}/analyze`, data)
}

/**
 * 获取需求文档的分析任务
 */
export function getRequirementAnalysisTask(documentId: number) {
  return api.get<RequirementAnalysisTask>(`${BASE_URL}/documents/${documentId}/analysis`)
}

// ===== 需求测试分析管理 =====

/**
 * 获取需求测试分析任务列表
 */
export function getRequirementTestTasks(params?: RequirementTestTaskListParams) {
  return api.get<RequirementTestTask[]>(`${BASE_URL}/test-tasks`, { params })
}

/**
 * 创建需求测试分析任务
 */
export function createRequirementTestTask(data: CreateRequirementTestTaskRequest) {
  return api.post<RequirementTestTask>(`${BASE_URL}/test-tasks`, data)
}

/**
 * 获取需求测试分析任务详情
 */
export function getRequirementTestTask(id: number) {
  return api.get<RequirementTestTask>(`${BASE_URL}/test-tasks/${id}`)
}

/**
 * 删除需求测试分析任务
 */
export function deleteRequirementTestTask(id: number) {
  return api.delete(`${BASE_URL}/test-tasks/${id}`)
}

// ===== 工具接口 =====

/**
 * 获取支持的文件类型
 */
export function getSupportedFileTypes() {
  return api.get<SupportedFileTypesResponse>(`${BASE_URL}/supported-file-types`)
}

// ===== 便捷方法 =====

/**
 * 轮询检查任务状态（用于实时更新）
 */
export async function pollTaskStatus<T extends { status: string }>(
  getTaskFn: () => Promise<T>,
  onUpdate: (task: T) => void,
  onComplete: (task: T) => void,
  maxAttempts: number = 60,
  interval: number = 2000
): Promise<void> {
  let attempts = 0
  
  const poll = async (): Promise<void> => {
    try {
      const task = await getTaskFn()
      onUpdate(task)
      
      if (task.status === 'completed' || task.status === 'failed') {
        onComplete(task)
        return
      }
      
      attempts++
      if (attempts < maxAttempts) {
        setTimeout(poll, interval)
      } else {
        console.warn('任务状态轮询超时')
        onComplete(task)
      }
    } catch (error) {
      console.error('轮询任务状态失败:', error)
      attempts++
      if (attempts < maxAttempts) {
        setTimeout(poll, interval)
      }
    }
  }
  
  poll()
}

/**
 * 批量操作需求文档
 */
export function batchDeleteRequirementDocuments(ids: number[]) {
  return Promise.all(ids.map(id => deleteRequirementDocument(id)))
}

/**
 * 批量操作测试任务
 */
export function batchDeleteRequirementTestTasks(ids: number[]) {
  return Promise.all(ids.map(id => deleteRequirementTestTask(id)))
} 