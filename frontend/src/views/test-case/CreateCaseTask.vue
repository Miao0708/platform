<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">创建测试用例任务</h1>
      <p class="page-description">基于需求文档生成测试用例</p>
    </div>

    <el-card>
      <el-form :model="form" label-width="120px">
        <el-form-item label="任务名称">
          <el-input v-model="form.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="需求文档">
          <el-input
            v-model="form.requirement"
            type="textarea"
            :rows="8"
            placeholder="请输入需求描述..."
          />
        </el-form-item>
        
        <el-form-item label="Prompt模板">
          <el-select v-model="form.promptTemplateId" placeholder="请选择模板">
            <el-option label="测试用例生成模板" value="1" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="createTask">创建任务</el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const form = reactive({
  name: '',
  requirement: '',
  promptTemplateId: ''
})

const createTask = async () => {
  if (!form.name || !form.requirement || !form.promptTemplateId) {
    ElMessage.error('请填写完整信息')
    return
  }
  
  try {
    // TODO: 调用API创建任务
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('任务创建成功')
    router.push('/test-case/tasks')
  } catch (error) {
    ElMessage.error('任务创建失败')
  }
}
</script>
