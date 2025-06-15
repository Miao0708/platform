/**
 * 文件上传工具函数
 * 统一处理各种文件上传的验证和格式化
 */

// 文件类型配置
export const FILE_TYPES = {
  // 需求文档支持的类型
  REQUIREMENT: ['.txt', '.md', '.docx', '.pdf', '.doc'],
  
  // 知识库文档支持的类型
  KNOWLEDGE: ['.pdf', '.txt', '.md', '.docx', '.doc'],
  
  // 代码差异文件支持的类型
  CODE_DIFF: ['.patch', '.diff', '.txt'],
  
  // 图片类型
  IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.webp']
} as const

// 文件大小限制（字节）
export const FILE_SIZE_LIMITS = {
  REQUIREMENT: 10 * 1024 * 1024, // 10MB
  KNOWLEDGE: 50 * 1024 * 1024,   // 50MB
  CODE_DIFF: 5 * 1024 * 1024,    // 5MB
  IMAGE: 5 * 1024 * 1024          // 5MB
} as const

// 文件验证结果
export interface FileValidationResult {
  isValid: boolean
  error?: string
  warnings?: string[]
}

// 文件信息
export interface FileInfo {
  name: string
  size: number
  type: string
  extension: string
}

/**
 * 验证文件类型
 */
export function validateFileType(
  file: File,
  allowedTypes: readonly string[]
): FileValidationResult {
  const extension = '.' + file.name.split('.').pop()?.toLowerCase()
  
  if (!allowedTypes.includes(extension)) {
    return {
      isValid: false,
      error: `不支持的文件类型 ${extension}，支持的类型：${allowedTypes.join(', ')}`
    }
  }
  
  return { isValid: true }
}

/**
 * 验证文件大小
 */
export function validateFileSize(
  file: File,
  maxSize: number
): FileValidationResult {
  if (file.size > maxSize) {
    return {
      isValid: false,
      error: `文件大小超过限制，最大允许 ${formatFileSize(maxSize)}`
    }
  }
  
  return { isValid: true }
}

/**
 * 综合验证文件
 */
export function validateFile(
  file: File,
  options: {
    allowedTypes: readonly string[]
    maxSize: number
    customValidation?: (file: File) => FileValidationResult
  }
): FileValidationResult {
  // 验证文件类型
  const typeValidation = validateFileType(file, options.allowedTypes)
  if (!typeValidation.isValid) {
    return typeValidation
  }
  
  // 验证文件大小
  const sizeValidation = validateFileSize(file, options.maxSize)
  if (!sizeValidation.isValid) {
    return sizeValidation
  }
  
  // 自定义验证
  if (options.customValidation) {
    const customValidation = options.customValidation(file)
    if (!customValidation.isValid) {
      return customValidation
    }
  }
  
  return { isValid: true }
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 获取文件信息
 */
export function getFileInfo(file: File): FileInfo {
  const extension = '.' + (file.name.split('.').pop()?.toLowerCase() || '')
  
  return {
    name: file.name,
    size: file.size,
    type: file.type,
    extension
  }
}

/**
 * 创建文件上传的FormData
 */
export function createUploadFormData(
  file: File,
  additionalFields: Record<string, any> = {}
): FormData {
  const formData = new FormData()
  formData.append('file', file)
  
  // 添加额外字段
  Object.entries(additionalFields).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (typeof value === 'object') {
        formData.append(key, JSON.stringify(value))
      } else {
        formData.append(key, String(value))
      }
    }
  })
  
  return formData
}

/**
 * 需求文档上传验证
 */
export function validateRequirementFile(file: File): FileValidationResult {
  return validateFile(file, {
    allowedTypes: FILE_TYPES.REQUIREMENT,
    maxSize: FILE_SIZE_LIMITS.REQUIREMENT,
    customValidation: (file) => {
      const warnings: string[] = []
      
      // 检查文件名
      if (file.name.length > 100) {
        warnings.push('文件名过长，建议不超过100个字符')
      }
      
      // 检查特殊字符
      if (/[<>:"/\\|?*]/.test(file.name)) {
        warnings.push('文件名包含特殊字符，可能导致保存问题')
      }
      
      return {
        isValid: true,
        warnings: warnings.length > 0 ? warnings : undefined
      }
    }
  })
}

/**
 * 知识库文档上传验证
 */
export function validateKnowledgeFile(file: File): FileValidationResult {
  return validateFile(file, {
    allowedTypes: FILE_TYPES.KNOWLEDGE,
    maxSize: FILE_SIZE_LIMITS.KNOWLEDGE
  })
}

/**
 * 代码差异文件上传验证
 */
export function validateCodeDiffFile(file: File): FileValidationResult {
  return validateFile(file, {
    allowedTypes: FILE_TYPES.CODE_DIFF,
    maxSize: FILE_SIZE_LIMITS.CODE_DIFF,
    customValidation: (file) => {
      // 检查是否可能是代码差异文件
      if (!file.name.includes('diff') && !file.name.includes('patch')) {
        return {
          isValid: true,
          warnings: ['文件名不包含"diff"或"patch"，请确认这是代码差异文件']
        }
      }
      
      return { isValid: true }
    }
  })
}

/**
 * 通用文件上传错误处理
 */
export function handleUploadError(error: any): string {
  if (error.response) {
    const { status, data } = error.response
    
    switch (status) {
      case 400:
        return data?.message || '文件格式或内容有误'
      case 413:
        return '文件过大，超过服务器限制'
      case 415:
        return '不支持的文件类型'
      case 500:
        return '服务器处理文件时出错'
      default:
        return data?.message || '文件上传失败'
    }
  } else if (error.request) {
    return '网络连接失败，请检查网络状态'
  } else {
    return error.message || '文件上传过程中发生未知错误'
  }
}

/**
 * 文件上传进度处理器
 */
export function createUploadProgressHandler(
  onProgress: (progress: number) => void
) {
  return (progressEvent: ProgressEvent) => {
    if (progressEvent.lengthComputable) {
      const progress = Math.round(
        (progressEvent.loaded / progressEvent.total) * 100
      )
      onProgress(progress)
    }
  }
}

/**
 * 批量文件验证
 */
export function validateMultipleFiles(
  files: File[],
  options: {
    allowedTypes: readonly string[]
    maxSize: number
    maxCount?: number
    totalMaxSize?: number
  }
): { validFiles: File[]; errors: string[] } {
  const validFiles: File[] = []
  const errors: string[] = []
  
  // 检查文件数量
  if (options.maxCount && files.length > options.maxCount) {
    errors.push(`最多只能上传 ${options.maxCount} 个文件`)
    return { validFiles, errors }
  }
  
  // 检查总大小
  const totalSize = files.reduce((sum, file) => sum + file.size, 0)
  if (options.totalMaxSize && totalSize > options.totalMaxSize) {
    errors.push(`文件总大小超过限制 ${formatFileSize(options.totalMaxSize)}`)
    return { validFiles, errors }
  }
  
  // 逐个验证文件
  files.forEach((file, index) => {
    const validation = validateFile(file, {
      allowedTypes: options.allowedTypes,
      maxSize: options.maxSize
    })
    
    if (validation.isValid) {
      validFiles.push(file)
    } else {
      errors.push(`文件 ${index + 1} (${file.name}): ${validation.error}`)
    }
  })
  
  return { validFiles, errors }
} 