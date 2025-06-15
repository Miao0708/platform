<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h1 class="page-title">仪表盘</h1>
      <p class="page-description">欢迎使用AI研发辅助平台，这里是您的工作概览</p>
    </div>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon git-icon">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ stats.repositories }}</div>
              <div class="stats-label">Git仓库</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon prompt-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ stats.prompts }}</div>
              <div class="stats-label">Prompt模板</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon review-icon">
              <el-icon><View /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ stats.reviews }}</div>
              <div class="stats-label">代码评审</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon case-icon">
              <el-icon><Files /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-number">{{ stats.testCases }}</div>
              <div class="stats-label">测试用例</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快速操作 -->
    <el-row :gutter="20" class="quick-actions-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          
          <div class="quick-actions">
            <el-button
              type="primary"
              :icon="Plus"
              @click="$router.push('/code-review/create')"
            >
              创建代码评审
            </el-button>
            
            <el-button
              type="success"
              :icon="Plus"
              @click="$router.push('/test-case/create')"
            >
              创建用例任务
            </el-button>
            
            <el-button
              type="info"
              :icon="Setting"
              @click="$router.push('/configuration/git')"
            >
              配置Git仓库
            </el-button>
            
            <el-button
              type="warning"
              :icon="Document"
              @click="$router.push('/configuration/prompts')"
            >
              管理Prompt
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近任务</span>
              <el-button type="text" @click="$router.push('/code-review/tasks')">
                查看全部
              </el-button>
            </div>
          </template>
          
          <div class="recent-tasks">
            <div
              v-for="task in recentTasks"
              :key="task.id"
              class="task-item"
            >
              <div class="task-info">
                <div class="task-name">{{ task.name }}</div>
                <div class="task-time">{{ task.createdAt }}</div>
              </div>
              <el-tag :type="getTaskTagType(task.status)">
                {{ getTaskStatusText(task.status) }}
              </el-tag>
            </div>
            
            <div v-if="recentTasks.length === 0" class="empty-tasks">
              暂无任务
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  Connection,
  Document,
  View,
  Files,
  Plus,
  Setting
} from '@element-plus/icons-vue'
import type { TaskStatus } from '@/types'

// 统计数据
const stats = ref({
  repositories: 5,
  prompts: 12,
  reviews: 28,
  testCases: 156
})

// 最近任务
const recentTasks = ref([
  {
    id: '1',
    name: '用户登录模块代码评审',
    status: 'completed' as TaskStatus,
    createdAt: '2024-01-15 14:30'
  },
  {
    id: '2',
    name: '支付流程测试用例生成',
    status: 'running' as TaskStatus,
    createdAt: '2024-01-15 13:45'
  },
  {
    id: '3',
    name: '数据库连接模块评审',
    status: 'pending' as TaskStatus,
    createdAt: '2024-01-15 12:20'
  }
])

// 获取任务状态标签类型
const getTaskTagType = (status: TaskStatus) => {
  const typeMap = {
    pending: 'info',
    queued: 'warning',
    running: 'primary',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取任务状态文本
const getTaskStatusText = (status: TaskStatus) => {
  const textMap = {
    pending: '待执行',
    queued: '排队中',
    running: '执行中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || '未知'
}

onMounted(() => {
  // 这里可以加载实际的统计数据
  console.log('Dashboard mounted')
})
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;
  
  .page-header {
    margin-bottom: 24px;
  }
  
  .stats-row {
    margin-bottom: 24px;
    
    .stats-card {
      .stats-content {
        display: flex;
        align-items: center;
        
        .stats-icon {
          width: 48px;
          height: 48px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 16px;
          font-size: 24px;
          color: #fff;
          
          &.git-icon {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }
          
          &.prompt-icon {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          }
          
          &.review-icon {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          }
          
          &.case-icon {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
          }
        }
        
        .stats-info {
          .stats-number {
            font-size: 24px;
            font-weight: 600;
            color: #333;
            line-height: 1;
          }
          
          .stats-label {
            font-size: 14px;
            color: #666;
            margin-top: 4px;
          }
        }
      }
    }
  }
  
  .quick-actions-row {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .quick-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      
      .el-button {
        height: 48px;
      }
    }
    
    .recent-tasks {
      .task-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;
        
        &:last-child {
          border-bottom: none;
        }
        
        .task-info {
          .task-name {
            font-size: 14px;
            color: #333;
            margin-bottom: 4px;
          }
          
          .task-time {
            font-size: 12px;
            color: #999;
          }
        }
      }
      
      .empty-tasks {
        text-align: center;
        color: #999;
        padding: 40px 0;
      }
    }
  }
}
</style>
