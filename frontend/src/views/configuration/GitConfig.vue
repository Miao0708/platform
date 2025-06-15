<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Git配置</h1>
      <p class="page-description">管理Git仓库连接凭证和仓库配置</p>
    </div>

    <!-- 全局凭证配置 -->
    <el-card class="mb-3">
      <template #header>
        <div class="card-header">
          <span>全局凭证管理</span>
        </div>
      </template>
      
      <el-form
        ref="credentialFormRef"
        :model="credentialForm"
        :rules="credentialRules"
        label-width="120px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="credentialForm.username"
            placeholder="请输入Git用户名"
          />
        </el-form-item>
        
        <el-form-item label="访问令牌" prop="token">
          <el-input
            v-model="credentialForm.token"
            type="password"
            placeholder="请输入Personal Access Token"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveCredential" :loading="saving">
            保存凭证
          </el-button>
          <el-button @click="testConnection" :loading="testing">
            测试连接
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 仓库配置列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>仓库配置</span>
          <el-button type="primary" @click="showAddDialog">
            添加仓库
          </el-button>
        </div>
      </template>
      
      <el-table :data="repositories" style="width: 100%">
        <el-table-column prop="alias" label="仓库别名" />
        <el-table-column prop="url" label="仓库地址" />
        <el-table-column prop="defaultBaseBranch" label="默认分支" />
        <el-table-column prop="createdAt" label="创建时间" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="text" @click="editRepository(scope.row)">
              编辑
            </el-button>
            <el-button type="text" @click="deleteRepository(scope.row)" style="color: #f56c6c">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑仓库对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑仓库' : '添加仓库'"
      width="500px"
    >
      <el-form
        ref="repositoryFormRef"
        :model="repositoryForm"
        :rules="repositoryRules"
        label-width="120px"
      >
        <el-form-item label="仓库别名" prop="alias">
          <el-input
            v-model="repositoryForm.alias"
            placeholder="请输入易记的仓库名称"
          />
        </el-form-item>
        
        <el-form-item label="仓库地址" prop="url">
          <el-input
            v-model="repositoryForm.url"
            placeholder="请输入Git仓库URL"
          />
        </el-form-item>
        
        <el-form-item label="默认分支" prop="defaultBaseBranch">
          <el-input
            v-model="repositoryForm.defaultBaseBranch"
            placeholder="如：main, master, develop"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRepository" :loading="saving">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { gitApi } from '@/api/git'
import type { GitCredential, GitRepository } from '@/types'

// 表单引用
const credentialFormRef = ref<FormInstance>()
const repositoryFormRef = ref<FormInstance>()

// 加载状态
const saving = ref(false)
const testing = ref(false)

// 凭证表单
const credentialForm = reactive<GitCredential>({
  username: '',
  token: ''
})

// 凭证验证规则
const credentialRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  token: [
    { required: true, message: '请输入访问令牌', trigger: 'blur' }
  ]
}

// 仓库列表
const repositories = ref<GitRepository[]>([])

// 对话框状态
const dialogVisible = ref(false)
const isEdit = ref(false)

// 仓库表单
const repositoryForm = reactive({
  id: '',
  alias: '',
  url: '',
  defaultBaseBranch: 'main'
})

// 仓库验证规则
const repositoryRules: FormRules = {
  alias: [
    { required: true, message: '请输入仓库别名', trigger: 'blur' }
  ],
  url: [
    { required: true, message: '请输入仓库地址', trigger: 'blur' },
    {
      pattern: /^https?:\/\/.+\.(git|com|org|net)(\/.*)?(\/.+\.git)?$/,
      message: '请输入有效的Git仓库地址',
      trigger: 'blur'
    }
  ]
}

// 保存凭证
const saveCredential = async () => {
  if (!credentialFormRef.value) return
  
  try {
    await credentialFormRef.value.validate()
    saving.value = true
    
    await gitApi.createCredential({
      username: credentialForm.username,
      token: credentialForm.token
    })
    
    ElMessage.success('凭证保存成功')
    loadCredentials()
  } catch (error) {
    console.error('Save credential failed:', error)
    ElMessage.error('凭证保存失败')
  } finally {
    saving.value = false
  }
}

// 测试连接
const testConnection = async () => {
  if (!credentialFormRef.value) return
  
  try {
    await credentialFormRef.value.validate()
    testing.value = true
    
    const result = await gitApi.testConnection()
    
    if (result.success) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error(`连接测试失败: ${result.message}`)
    }
  } catch (error) {
    console.error('Test connection failed:', error)
    ElMessage.error('连接测试失败')
  } finally {
    testing.value = false
  }
}

// 加载凭证列表
const loadCredentials = async () => {
  try {
    const credentials = await gitApi.getCredentials()
    if (credentials && credentials.length > 0) {
      const activeCredential = credentials.find((c: any) => c.isActive)
      if (activeCredential) {
        credentialForm.username = activeCredential.username
        // 不显示token内容，只显示已配置状态
      }
    }
  } catch (error) {
    console.error('Load credentials failed:', error)
  }
}

// 显示添加对话框
const showAddDialog = () => {
  isEdit.value = false
  Object.assign(repositoryForm, {
    id: '',
    alias: '',
    url: '',
    defaultBaseBranch: 'main'
  })
  dialogVisible.value = true
}

// 编辑仓库
const editRepository = (repository: GitRepository) => {
  isEdit.value = true
  Object.assign(repositoryForm, repository)
  dialogVisible.value = true
}

// 保存仓库
const saveRepository = async () => {
  if (!repositoryFormRef.value) return
  
  try {
    await repositoryFormRef.value.validate()
    saving.value = true
    
    if (isEdit.value) {
      await gitApi.updateRepository(repositoryForm.id, {
        alias: repositoryForm.alias,
        url: repositoryForm.url,
        default_base_branch: repositoryForm.defaultBaseBranch
      })
    } else {
      await gitApi.createRepository({
        alias: repositoryForm.alias,
        url: repositoryForm.url,
        default_base_branch: repositoryForm.defaultBaseBranch
      })
    }
    
    ElMessage.success(isEdit.value ? '仓库更新成功' : '仓库添加成功')
    dialogVisible.value = false
    loadRepositories()
  } catch (error) {
    console.error('Save repository failed:', error)
    ElMessage.error(isEdit.value ? '仓库更新失败' : '仓库添加失败')
  } finally {
    saving.value = false
  }
}

// 删除仓库
const deleteRepository = async (repository: GitRepository) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除仓库 "${repository.alias}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await gitApi.deleteRepository(repository.id)
    
    ElMessage.success('仓库删除成功')
    loadRepositories()
  } catch (error: any) {
    if (error?.name !== 'cancel') {
      console.error('Delete repository failed:', error)
      ElMessage.error('仓库删除失败')
    }
  }
}

// 加载仓库列表
const loadRepositories = async () => {
  try {
    const result = await gitApi.getRepositories()
    repositories.value = result || []
  } catch (error) {
    console.error('Load repositories failed:', error)
    ElMessage.error('加载仓库列表失败')
  }
}

onMounted(() => {
  loadCredentials()
  loadRepositories()
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
