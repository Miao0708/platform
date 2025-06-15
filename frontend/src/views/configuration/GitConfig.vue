<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Git配置</h1>
      <p class="page-description">管理Git托管平台凭证和仓库配置</p>
    </div>

    <!-- Git平台配置管理 -->
    <el-card class="mb-3">
      <template #header>
        <div class="card-header">
          <span>Git平台管理</span>
          <el-button type="primary" @click="showAddPlatformDialog">
            添加平台
          </el-button>
        </div>
      </template>
      
      <el-table :data="platformConfigs" style="width: 100%">
        <el-table-column prop="name" label="平台名称" />
        <el-table-column prop="platform" label="平台类型" width="120">
          <template #default="scope">
            <el-tag :color="gitUtils.getPlatformColor(scope.row.platform)" style="color: white;">
              {{ getPlatformLabel(scope.row.platform) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="updatedAt" label="更新时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.updatedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="text" @click="testPlatformConnection(scope.row)" :loading="testingPlatform === scope.row.id">
              测试连接
            </el-button>
            <el-button type="text" @click="editPlatformConfig(scope.row)">
              编辑
            </el-button>
            <el-button type="text" @click="deletePlatformConfig(scope.row)" style="color: #f56c6c">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 仓库配置列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>仓库配置</span>
          <el-button type="primary" @click="showAddRepositoryDialog" :disabled="platformConfigs.length === 0">
            添加仓库
          </el-button>
        </div>
      </template>
      
      <div v-if="platformConfigs.length === 0" class="empty-state">
        <p>请先添加Git平台配置，然后再添加仓库</p>
      </div>
      
      <el-table v-else :data="repositories" style="width: 100%">
        <el-table-column prop="alias" label="仓库别名" />
        <el-table-column prop="url" label="仓库地址" />
        <el-table-column prop="platformName" label="平台" width="150">
          <template #default="scope">
            <el-tag v-if="scope.row.platformName" size="small">
              {{ scope.row.platformName }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="defaultBaseBranch" label="默认分支" width="100" />
        <el-table-column prop="updatedAt" label="更新时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.updatedAt) }}
          </template>
        </el-table-column>
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

    <!-- 添加/编辑平台配置对话框 -->
    <el-dialog
      v-model="platformDialogVisible"
      :title="isPlatformEdit ? '编辑平台配置' : '添加平台配置'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="platformFormRef"
        :model="platformForm"
        :rules="platformRules"
        label-width="120px"
      >
        <el-form-item label="平台名称" prop="name">
          <el-input
            v-model="platformForm.name"
            placeholder="请输入平台名称，如：公司GitHub、个人GitLab"
          />
        </el-form-item>

        <el-form-item label="平台类型" prop="platform">
          <el-select v-model="platformForm.platform" placeholder="请选择平台类型" @change="onPlatformChange">
            <el-option
              v-for="option in gitUtils.platformOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item v-if="platformForm.platform === 'custom'" label="基础URL" prop="baseUrl">
          <el-input
            v-model="platformForm.baseUrl"
            placeholder="请输入自定义平台的基础URL，如：https://git.company.com"
          />
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="platformForm.username"
            placeholder="请输入Git用户名"
          />
        </el-form-item>
        
        <el-form-item label="访问令牌" prop="token">
          <el-input
            v-model="platformForm.token"
            type="password"
            placeholder="请输入Personal Access Token"
            show-password
          />
          <div class="form-tip">
            访问令牌需要有仓库读取权限。
            <a href="#" @click.prevent="showTokenHelp">如何获取？</a>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="platformDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePlatformConfig" :loading="saving">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑仓库对话框 -->
    <el-dialog
      v-model="repositoryDialogVisible"
      :title="isRepositoryEdit ? '编辑仓库' : '添加仓库'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="repositoryFormRef"
        :model="repositoryForm"
        :rules="repositoryRules"
        label-width="120px"
      >
        <el-form-item label="Git平台" prop="platformConfigId">
          <el-select v-model="repositoryForm.platformConfigId" placeholder="请选择Git平台配置">
            <el-option
              v-for="platform in platformConfigs"
              :key="platform.id"
              :label="platform.name"
              :value="platform.id"
            />
          </el-select>
        </el-form-item>

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
            @blur="onUrlChange"
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
        <el-button @click="repositoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRepository" :loading="saving">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- Token帮助对话框 -->
    <el-dialog v-model="tokenHelpVisible" title="如何获取访问令牌" width="70%">
      <div class="token-help">
        <h3>GitHub</h3>
        <ol>
          <li>登录GitHub，进入 Settings > Developer settings > Personal access tokens</li>
          <li>点击 "Generate new token"</li>
          <li>选择适当的权限范围（repo权限）</li>
          <li>复制生成的token</li>
        </ol>

        <h3>GitLab</h3>
        <ol>
          <li>登录GitLab，进入 User Settings > Access Tokens</li>
          <li>输入token名称，选择过期时间</li>
          <li>选择 api 和 read_repository 权限</li>
          <li>点击 "Create personal access token"</li>
        </ol>

        <h3>码云 Gitee</h3>
        <ol>
          <li>登录码云，进入 设置 > 私人令牌</li>
          <li>点击 "生成新令牌"</li>
          <li>选择适当的权限范围</li>
          <li>复制生成的令牌</li>
        </ol>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { gitApi, gitUtils, type GitPlatformConfig, type GitRepository, type GitPlatform } from '@/api/git'

// 表单引用
const platformFormRef = ref<FormInstance>()
const repositoryFormRef = ref<FormInstance>()

// 加载状态
const saving = ref(false)
const testingPlatform = ref('')

// 平台配置列表
const platformConfigs = ref<GitPlatformConfig[]>([])

// 仓库列表
const repositories = ref<GitRepository[]>([])

// 对话框状态
const platformDialogVisible = ref(false)
const repositoryDialogVisible = ref(false)
const tokenHelpVisible = ref(false)
const isPlatformEdit = ref(false)
const isRepositoryEdit = ref(false)

// 平台配置表单
const platformForm = reactive({
  id: '',
  name: '',
  platform: 'github' as GitPlatform,
  username: '',
  token: '',
  baseUrl: ''
})

// 仓库表单
const repositoryForm = reactive({
  id: '',
  alias: '',
  url: '',
  defaultBaseBranch: 'main',
  platformConfigId: ''
})

// 平台配置验证规则
const platformRules: FormRules = {
  name: [
    { required: true, message: '请输入平台名称', trigger: 'blur' }
  ],
  platform: [
    { required: true, message: '请选择平台类型', trigger: 'change' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  token: [
    { required: true, message: '请输入访问令牌', trigger: 'blur' }
  ],
  baseUrl: [
    { required: true, message: '请输入基础URL', trigger: 'blur' },
    { pattern: /^https?:\/\/.+/, message: '请输入有效的URL', trigger: 'blur' }
  ]
}

// 仓库验证规则
const repositoryRules: FormRules = {
  platformConfigId: [
    { required: true, message: '请选择Git平台配置', trigger: 'change' }
  ],
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

// 获取平台标签
const getPlatformLabel = (platform: GitPlatform) => {
  const option = gitUtils.platformOptions.find(opt => opt.value === platform)
  return option?.label || platform
}

// 格式化时间
const formatTime = (time: string | Date) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 显示添加平台对话框
const showAddPlatformDialog = () => {
  isPlatformEdit.value = false
  Object.assign(platformForm, {
    id: '',
    name: '',
    platform: 'github',
    username: '',
    token: '',
    baseUrl: ''
  })
  platformDialogVisible.value = true
}

// 显示添加仓库对话框
const showAddRepositoryDialog = () => {
  isRepositoryEdit.value = false
  Object.assign(repositoryForm, {
    id: '',
    alias: '',
    url: '',
    defaultBaseBranch: 'main',
    platformConfigId: ''
  })
  repositoryDialogVisible.value = true
}

// 编辑平台配置
const editPlatformConfig = (config: GitPlatformConfig) => {
  isPlatformEdit.value = true
  Object.assign(platformForm, {
    id: config.id,
    name: config.name,
    platform: config.platform,
    username: config.username,
    token: '', // 不显示已保存的token
    baseUrl: config.baseUrl || ''
  })
  platformDialogVisible.value = true
}

// 编辑仓库
const editRepository = (repository: GitRepository) => {
  isRepositoryEdit.value = true
  Object.assign(repositoryForm, {
    id: repository.id,
    alias: repository.alias,
    url: repository.url,
    defaultBaseBranch: repository.defaultBaseBranch,
    platformConfigId: repository.platformConfigId
  })
  repositoryDialogVisible.value = true
}

// 平台类型变化处理
const onPlatformChange = () => {
  if (platformForm.platform !== 'custom') {
    platformForm.baseUrl = ''
  }
}

// URL变化处理
const onUrlChange = () => {
  if (repositoryForm.url && !repositoryForm.alias) {
    const repoName = gitUtils.extractRepoName(repositoryForm.url)
    if (repoName) {
      repositoryForm.alias = repoName
    }
  }
}

// 保存平台配置
const savePlatformConfig = async () => {
  if (!platformFormRef.value) return
  
  try {
    await platformFormRef.value.validate()
    saving.value = true
    
    const requestData = {
      name: platformForm.name,
      platform: platformForm.platform,
      username: platformForm.username,
      token: platformForm.token,
      baseUrl: platformForm.baseUrl || undefined
    }
    
    if (isPlatformEdit.value) {
      await gitApi.updatePlatformConfig(platformForm.id, requestData)
    } else {
      await gitApi.createPlatformConfig(requestData)
    }
    
    ElMessage.success(isPlatformEdit.value ? '平台配置更新成功' : '平台配置创建成功')
    platformDialogVisible.value = false
    loadPlatformConfigs()
  } catch (error) {
    console.error('Save platform config failed:', error)
    ElMessage.error(isPlatformEdit.value ? '平台配置更新失败' : '平台配置创建失败')
  } finally {
    saving.value = false
  }
}

// 保存仓库
const saveRepository = async () => {
  if (!repositoryFormRef.value) return
  
  try {
    await repositoryFormRef.value.validate()
    saving.value = true
    
    const requestData = {
      alias: repositoryForm.alias,
      url: repositoryForm.url,
      defaultBaseBranch: repositoryForm.defaultBaseBranch,
      platformConfigId: repositoryForm.platformConfigId
    }
    
    if (isRepositoryEdit.value) {
      await gitApi.updateRepository(repositoryForm.id, requestData)
    } else {
      await gitApi.createRepository(requestData)
    }
    
    ElMessage.success(isRepositoryEdit.value ? '仓库更新成功' : '仓库添加成功')
    repositoryDialogVisible.value = false
    loadRepositories()
  } catch (error) {
    console.error('Save repository failed:', error)
    ElMessage.error(isRepositoryEdit.value ? '仓库更新失败' : '仓库添加失败')
  } finally {
    saving.value = false
  }
}

// 测试平台连接
const testPlatformConnection = async (config: GitPlatformConfig) => {
  try {
    testingPlatform.value = config.id
    
    const result = await gitApi.testPlatformConnection({
      platformConfigId: config.id
    })
    
    if (result && result.success) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error(`连接测试失败: ${result?.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('Test platform connection failed:', error)
    ElMessage.error('连接测试失败')
  } finally {
    testingPlatform.value = ''
  }
}

// 删除平台配置
const deletePlatformConfig = async (config: GitPlatformConfig) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除平台配置 "${config.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await gitApi.deletePlatformConfig(config.id)
    
    ElMessage.success('平台配置删除成功')
    loadPlatformConfigs()
    loadRepositories() // 重新加载仓库列表，更新平台名称显示
  } catch (error: any) {
    if (error?.name !== 'cancel') {
      console.error('Delete platform config failed:', error)
      ElMessage.error('平台配置删除失败')
    }
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

// 显示Token帮助
const showTokenHelp = () => {
  tokenHelpVisible.value = true
}

// 加载平台配置列表
const loadPlatformConfigs = async () => {
  try {
    const result = await gitApi.getPlatformConfigs()
    platformConfigs.value = result || []
  } catch (error) {
    console.error('Load platform configs failed:', error)
    ElMessage.error('加载平台配置失败')
  }
}

// 加载仓库列表
const loadRepositories = async () => {
  try {
    const result = await gitApi.getRepositories()
    
    // 关联平台配置名称
    const repos = (result || []).map((repo: any) => {
      const platform = platformConfigs.value.find(p => p.id === repo.platformConfigId)
      return {
        ...repo,
        platformName: platform?.name || '未知平台'
      }
    })
    
    repositories.value = repos
  } catch (error) {
    console.error('Load repositories failed:', error)
    ElMessage.error('加载仓库列表失败')
  }
}

onMounted(() => {
  loadPlatformConfigs().then(() => {
    loadRepositories()
  })
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  
  a {
    color: #409EFF;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.token-help {
  h3 {
    margin-top: 20px;
    margin-bottom: 10px;
    color: #333;
    
    &:first-child {
      margin-top: 0;
    }
  }
  
  ol {
    margin-bottom: 20px;
    
    li {
      margin-bottom: 8px;
      line-height: 1.6;
    }
  }
}
</style>
