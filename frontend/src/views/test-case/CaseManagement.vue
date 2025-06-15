<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">测试用例管理</h1>
      <p class="page-description">查看和管理生成的测试用例</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>测试用例列表</span>
          <el-button type="primary" @click="exportCases">导出用例</el-button>
        </div>
      </template>
      
      <el-table :data="testCases" style="width: 100%">
        <el-table-column prop="title" label="用例标题" />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityTagType(scope.row.priority)">
              {{ scope.row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="preconditions" label="前置条件" show-overflow-tooltip />
        <el-table-column prop="steps" label="测试步骤" show-overflow-tooltip />
        <el-table-column prop="expectedResult" label="预期结果" show-overflow-tooltip />
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button type="text" @click="editCase(scope.row)">编辑</el-button>
            <el-button type="text" @click="deleteCase(scope.row)" style="color: #f56c6c">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { TestCase } from '@/types'

const testCases = ref<TestCase[]>([])

const getPriorityTagType = (priority: string) => {
  const typeMap: Record<string, string> = {
    P0: 'danger',
    P1: 'warning', 
    P2: 'info'
  }
  return typeMap[priority] || 'info'
}

const editCase = (testCase: TestCase) => {
  // TODO: 实现编辑功能
  ElMessage.info('编辑功能开发中')
}

const deleteCase = (testCase: TestCase) => {
  // TODO: 实现删除功能
  ElMessage.info('删除功能开发中')
}

const exportCases = () => {
  // TODO: 实现导出功能
  ElMessage.info('导出功能开发中')
}

const loadTestCases = async () => {
  // 模拟数据
  testCases.value = [
    {
      id: '1',
      title: '用户正常注册流程',
      preconditions: '用户未注册，系统正常运行',
      steps: '1. 打开注册页面\n2. 输入有效信息\n3. 点击注册按钮',
      expectedResult: '注册成功，跳转到登录页面',
      priority: 'P0',
      createdAt: '2024-01-15 14:30:00',
      updatedAt: '2024-01-15 14:30:00'
    }
  ]
}

onMounted(() => {
  loadTestCases()
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
