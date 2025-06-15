<template>
  <div class="requirement-test-result">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" size="small">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>需求测试结果详情</h2>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="exportResults">
          <el-icon><Download /></el-icon>
          导出结果
        </el-button>
        <el-button type="success" @click="generateTestCases">
          <el-icon><DocumentAdd /></el-icon>
          生成测试用例
        </el-button>
      </div>
    </div>

    <!-- 任务信息卡片 -->
    <el-card class="task-info-card">
      <template #header>
        <div class="card-header">
          <span>任务信息</span>
          <el-tag :type="getStatusTagType(taskInfo.status)">
            {{ getStatusText(taskInfo.status) }}
          </el-tag>
        </div>
      </template>
      
      <el-row :gutter="24">
        <el-col :span="8">
          <div class="info-item">
            <label>任务名称:</label>
            <span>{{ taskInfo.name }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <label>需求文档:</label>
            <span>{{ taskInfo.requirementName }}</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="info-item">
            <label>创建时间:</label>
            <span>{{ taskInfo.createdAt }}</span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 测试概览统计 -->
    <div class="stats-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ testResult.totalTests }}</div>
              <div class="stat-label">测试点总数</div>
            </div>
            <el-icon class="stat-icon"><Document /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card functional">
            <div class="stat-content">
              <div class="stat-number">{{ testResult.testsByType.functional || 0 }}</div>
              <div class="stat-label">功能测试</div>
            </div>
            <el-icon class="stat-icon"><Setting /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card security">
            <div class="stat-content">
              <div class="stat-number">{{ testResult.testsByType.security || 0 }}</div>
              <div class="stat-label">安全测试</div>
            </div>
            <el-icon class="stat-icon"><Lock /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card performance">
            <div class="stat-content">
              <div class="stat-number">{{ testResult.testsByType.performance || 0 }}</div>
              <div class="stat-label">性能测试</div>
            </div>
            <el-icon class="stat-icon"><Timer /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 优先级分布 -->
    <el-card class="priority-card">
      <template #header>
        <span>优先级分布</span>
      </template>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <div class="priority-item high">
            <div class="priority-label">
              <el-tag type="danger" size="small">高优先级</el-tag>
            </div>
            <div class="priority-count">{{ testResult.testsByPriority.high || 0 }}个</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="priority-item medium">
            <div class="priority-label">
              <el-tag type="warning" size="small">中优先级</el-tag>
            </div>
            <div class="priority-count">{{ testResult.testsByPriority.medium || 0 }}个</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="priority-item low">
            <div class="priority-label">
              <el-tag type="info" size="small">低优先级</el-tag>
            </div>
            <div class="priority-count">{{ testResult.testsByPriority.low || 0 }}个</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 测试点列表 -->
    <el-card class="test-results-card">
      <template #header>
        <div class="card-header">
          <span>测试点详情 ({{ filteredTestResults.length }}个)</span>
          <div class="header-filters">
            <el-select v-model="filters.type" placeholder="测试类型" size="small" style="width: 120px;">
              <el-option label="全部" value="" />
              <el-option label="功能测试" value="functional" />
              <el-option label="性能测试" value="performance" />
              <el-option label="安全测试" value="security" />
              <el-option label="易用性测试" value="usability" />
              <el-option label="兼容性测试" value="compatibility" />
            </el-select>
            <el-select v-model="filters.priority" placeholder="优先级" size="small" style="width: 100px;">
              <el-option label="全部" value="" />
              <el-option label="高" value="high" />
              <el-option label="中" value="medium" />
              <el-option label="低" value="low" />
            </el-select>
          </div>
        </div>
      </template>

      <div class="test-results-list">
        <div 
          v-for="(test, index) in filteredTestResults" 
          :key="test.id"
          class="test-result-item"
        >
          <div class="test-header">
            <div class="test-title">
              <span class="test-number">{{ index + 1 }}.</span>
              <span class="test-name">{{ test.testName }}</span>
              <el-tag :type="getTestTypeTagType(test.testType)" size="small">
                {{ getTestTypeText(test.testType) }}
              </el-tag>
              <el-tag :type="getPriorityTagType(test.priority)" size="small">
                {{ getPriorityText(test.priority) }}
              </el-tag>
            </div>
            <div class="test-actions">
              <el-button size="small" @click="toggleTestDetail(test.id)">
                {{ expandedTests.includes(test.id) ? '收起' : '展开' }}
              </el-button>
            </div>
          </div>

          <div class="test-description">
            {{ test.description }}
          </div>

          <div v-if="expandedTests.includes(test.id)" class="test-detail">
            <!-- 前置条件 -->
            <div v-if="test.preconditions.length > 0" class="detail-section">
              <h4>前置条件</h4>
              <ul>
                <li v-for="condition in test.preconditions" :key="condition">
                  {{ condition }}
                </li>
              </ul>
            </div>

            <!-- 测试步骤 -->
            <div class="detail-section">
              <h4>测试步骤</h4>
              <ol>
                <li v-for="step in test.testSteps" :key="step.stepNumber">
                  <strong>{{ step.action }}</strong>
                  <div class="expected-result">预期结果: {{ step.expectedResult }}</div>
                </li>
              </ol>
            </div>

            <!-- 预期结果 -->
            <div class="detail-section">
              <h4>总体预期结果</h4>
              <p>{{ test.expectedResult }}</p>
            </div>

            <!-- 测试数据 -->
            <div v-if="test.testData" class="detail-section">
              <h4>测试数据</h4>
              <pre>{{ test.testData }}</pre>
            </div>

            <!-- 备注 -->
            <div v-if="test.notes" class="detail-section">
              <h4>备注</h4>
              <p>{{ test.notes }}</p>
            </div>

            <!-- 标签 -->
            <div v-if="test.tags.length > 0" class="detail-section">
              <h4>标签</h4>
              <el-tag 
                v-for="tag in test.tags" 
                :key="tag" 
                size="small" 
                class="tag-item"
              >
                {{ tag }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 测试建议和总结 -->
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card class="summary-card">
          <template #header>
            <span>测试总结</span>
          </template>
          <div class="summary-content">
            {{ testResult.summary }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="recommendations-card">
          <template #header>
            <span>测试建议</span>
          </template>
          <ul class="recommendations-list">
            <li v-for="recommendation in testResult.recommendations" :key="recommendation">
              {{ recommendation }}
            </li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Download,
  DocumentAdd,
  Document,
  Setting,
  Lock,
  Timer
} from '@element-plus/icons-vue'
import type { RequirementTestTaskResult, RequirementTestResult } from '@/types/models'

const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const expandedTests = ref<string[]>([])

// 筛选条件
const filters = ref({
  type: '',
  priority: ''
})

// 任务信息
const taskInfo = ref({
  id: '',
  name: '',
  requirementName: '',
  status: 'completed' as const,
  createdAt: ''
})

// 测试结果数据
const testResult = ref<RequirementTestTaskResult>({
  taskId: '',
  requirementId: '',
  requirementName: '',
  promptTemplate: '',
  totalTests: 0,
  testsByType: {},
  testsByPriority: {},
  testResults: [],
  summary: '',
  recommendations: [],
  generatedAt: ''
})

// 过滤后的测试结果
const filteredTestResults = computed(() => {
  let results = testResult.value.testResults
  
  if (filters.value.type) {
    results = results.filter(test => test.testType === filters.value.type)
  }
  
  if (filters.value.priority) {
    results = results.filter(test => test.priority === filters.value.priority)
  }
  
  return results
})

// 工具函数
const getStatusText = (status: string) => {
  const statusMap = {
    pending: '待执行',
    running: '执行中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const getStatusTagType = (status: string) => {
  const typeMap = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status as keyof typeof typeMap] || 'info'
}

const getTestTypeText = (type: string) => {
  const typeMap = {
    functional: '功能',
    performance: '性能',
    security: '安全',
    usability: '易用性',
    compatibility: '兼容性'
  }
  return typeMap[type as keyof typeof typeMap] || type
}

const getTestTypeTagType = (type: string) => {
  const typeMap = {
    functional: 'primary',
    performance: 'warning',
    security: 'danger',
    usability: 'info',
    compatibility: 'success'
  }
  return typeMap[type as keyof typeof typeMap] || 'info'
}

const getPriorityText = (priority: string) => {
  const priorityMap = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return priorityMap[priority as keyof typeof priorityMap] || priority
}

const getPriorityTagType = (priority: string) => {
  const typeMap = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return typeMap[priority as keyof typeof typeMap] || 'info'
}

// 事件处理
const goBack = () => {
  router.back()
}

const toggleTestDetail = (testId: string) => {
  const index = expandedTests.value.indexOf(testId)
  if (index > -1) {
    expandedTests.value.splice(index, 1)
  } else {
    expandedTests.value.push(testId)
  }
}

const exportResults = () => {
  // TODO: 实现导出功能
  ElMessage.success('导出功能开发中...')
}

const generateTestCases = () => {
  // TODO: 实现生成测试用例功能
  ElMessage.success('生成测试用例功能开发中...')
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    
    const taskId = route.params.id as string
    
    // TODO: 调用API加载数据
    // 模拟数据
    taskInfo.value = {
      id: taskId,
      name: '用户登录需求测试分析',
      requirementName: '用户登录功能需求',
      status: 'completed',
      createdAt: '2024-01-15 15:30:00'
    }
    
    testResult.value = {
      taskId,
      requirementId: '1',
      requirementName: '用户登录功能需求',
      promptTemplate: '需求测试分析模板',
      totalTests: 12,
      testsByType: {
        functional: 6,
        security: 3,
        performance: 2,
        usability: 1
      },
      testsByPriority: {
        high: 4,
        medium: 6,
        low: 2
      },
      testResults: [
        {
          id: '1',
          testName: '用户正常登录测试',
          testType: 'functional',
          priority: 'high',
          description: '验证用户使用正确的用户名和密码能够成功登录系统',
          preconditions: ['系统正常运行', '用户账户已创建并激活'],
          testSteps: [
            { stepNumber: 1, action: '打开登录页面', expectedResult: '显示登录表单' },
            { stepNumber: 2, action: '输入有效的用户名', expectedResult: '用户名字段显示输入内容' },
            { stepNumber: 3, action: '输入正确的密码', expectedResult: '密码字段显示掩码' },
            { stepNumber: 4, action: '点击登录按钮', expectedResult: '系统验证用户凭据' }
          ],
          expectedResult: '用户成功登录，跳转到系统首页',
          testData: 'username: testuser\npassword: Test123!',
          estimatedTime: 5,
          tags: ['登录', '核心功能', '正向测试']
        },
        {
          id: '2',
          testName: 'SQL注入攻击测试',
          testType: 'security',
          priority: 'high',
          description: '验证登录接口对SQL注入攻击的防护能力',
          preconditions: ['系统正常运行'],
          testSteps: [
            { stepNumber: 1, action: '打开登录页面', expectedResult: '显示登录表单' },
            { stepNumber: 2, action: '在用户名字段输入SQL注入代码', expectedResult: '系统接收输入' },
            { stepNumber: 3, action: '输入任意密码', expectedResult: '密码字段显示掩码' },
            { stepNumber: 4, action: '点击登录按钮', expectedResult: '系统拒绝登录请求' }
          ],
          expectedResult: '系统拒绝登录，不执行恶意SQL代码，记录安全日志',
          testData: "username: admin'; DROP TABLE users; --\npassword: anything",
          notes: '此测试用于验证系统的安全防护机制',
          estimatedTime: 10,
          tags: ['安全', 'SQL注入', '渗透测试']
        }
      ],
      summary: '本次需求测试分析共生成12个测试点，覆盖功能、安全、性能、易用性等多个维度。重点关注用户登录的核心流程和安全防护，建议优先执行高优先级测试点。',
      recommendations: [
        '优先执行高优先级测试点，确保核心功能正常',
        '安全测试应在生产环境部署前完成',
        '性能测试建议在接近生产环境的测试环境中执行',
        '建议增加边界值测试，如超长用户名、特殊字符等'
      ],
      generatedAt: '2024-01-15 15:30:00'
    }
  } catch (error) {
    console.error('Load data failed:', error)
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.requirement-test-result {
  padding: 24px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
      
      h2 {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }
    }
    
    .header-right {
      display: flex;
      gap: 12px;
    }
  }
  
  .task-info-card {
    margin-bottom: 24px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .info-item {
      margin-bottom: 12px;
      
      label {
        font-weight: 600;
        color: #606266;
        margin-right: 8px;
      }
      
      span {
        color: #303133;
      }
    }
  }
  
  .stats-section {
    margin-bottom: 24px;
    
    .stat-card {
      position: relative;
      overflow: hidden;
      
      :deep(.el-card__body) {
        padding: 20px;
      }
      
      .stat-content {
        .stat-number {
          font-size: 32px;
          font-weight: 600;
          color: #303133;
          line-height: 1;
          margin-bottom: 8px;
        }
        
        .stat-label {
          font-size: 14px;
          color: #606266;
        }
      }
      
      .stat-icon {
        position: absolute;
        right: 20px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 32px;
        color: #ddd;
      }
      
      &.functional {
        border-left: 4px solid #409eff;
        
        .stat-number {
          color: #409eff;
        }
        
        .stat-icon {
          color: #409eff;
          opacity: 0.3;
        }
      }
      
      &.security {
        border-left: 4px solid #f56c6c;
        
        .stat-number {
          color: #f56c6c;
        }
        
        .stat-icon {
          color: #f56c6c;
          opacity: 0.3;
        }
      }
      
      &.performance {
        border-left: 4px solid #e6a23c;
        
        .stat-number {
          color: #e6a23c;
        }
        
        .stat-icon {
          color: #e6a23c;
          opacity: 0.3;
        }
      }
    }
  }
  
  .priority-card {
    margin-bottom: 24px;
    
    .priority-item {
      text-align: center;
      padding: 16px;
      
      .priority-label {
        margin-bottom: 8px;
      }
      
      .priority-count {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }
    }
  }
  
  .test-results-card {
    margin-bottom: 24px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .header-filters {
        display: flex;
        gap: 8px;
      }
    }
    
    .test-results-list {
      .test-result-item {
        border: 1px solid #ebeef5;
        border-radius: 6px;
        margin-bottom: 16px;
        overflow: hidden;
        
        .test-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background: #fafafa;
          border-bottom: 1px solid #ebeef5;
          
          .test-title {
            display: flex;
            align-items: center;
            gap: 8px;
            
            .test-number {
              font-weight: 600;
              color: #409eff;
            }
            
            .test-name {
              font-weight: 600;
              color: #303133;
            }
          }
        }
        
        .test-description {
          padding: 16px;
          color: #606266;
          line-height: 1.6;
        }
        
        .test-detail {
          padding: 0 16px 16px;
          
          .detail-section {
            margin-bottom: 16px;
            
            h4 {
              margin: 0 0 8px 0;
              font-size: 14px;
              font-weight: 600;
              color: #303133;
            }
            
            ul, ol {
              margin: 0;
              padding-left: 20px;
              
              li {
                margin-bottom: 4px;
                line-height: 1.6;
                
                .expected-result {
                  font-size: 12px;
                  color: #909399;
                  margin-top: 4px;
                }
              }
            }
            
            p {
              margin: 0;
              line-height: 1.6;
              color: #606266;
            }
            
            pre {
              background: #f5f7fa;
              padding: 12px;
              border-radius: 4px;
              font-size: 12px;
              line-height: 1.4;
              margin: 0;
              overflow-x: auto;
            }
            
            .tag-item {
              margin-right: 8px;
              margin-bottom: 4px;
            }
          }
        }
      }
    }
  }
  
  .summary-card,
  .recommendations-card {
    .summary-content {
      line-height: 1.6;
      color: #606266;
    }
    
    .recommendations-list {
      margin: 0;
      padding-left: 20px;
      
      li {
        margin-bottom: 8px;
        line-height: 1.6;
        color: #606266;
      }
    }
  }
}
</style>
