<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">个人信息</h1>
      <p class="page-description">管理您的个人资料和账户设置</p>
    </div>

    <el-row :gutter="20">
      <!-- 基本信息 -->
      <el-col :span="16">
        <el-card title="基本信息">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
            </div>
          </template>
          
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="120px"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" />
            </el-form-item>
            
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="profileForm.nickname" placeholder="请输入昵称" />
            </el-form-item>
            
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
            </el-form-item>
            
            <el-form-item label="部门">
              <el-input v-model="profileForm.department" placeholder="请输入部门" />
            </el-form-item>
            
            <el-form-item label="职位">
              <el-input v-model="profileForm.position" placeholder="请输入职位" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveProfile" :loading="saving">
                保存信息
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- 头像和安全设置 -->
      <el-col :span="8">
        <el-card class="mb-3">
          <template #header>
            <div class="card-header">
              <span>头像设置</span>
            </div>
          </template>
          
          <div class="avatar-section">
            <el-avatar :size="120" :src="profileForm.avatar">
              {{ profileForm.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            
            <el-upload
              class="avatar-uploader"
              :action="uploadAction"
              :headers="uploadHeaders"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
            >
              <el-button type="primary" class="mt-2">更换头像</el-button>
            </el-upload>
          </div>
        </el-card>
        
        <el-card>
          <template #header>
            <div class="card-header">
              <span>安全设置</span>
            </div>
          </template>
          
          <div class="security-section">
            <el-button type="warning" @click="showChangePasswordDialog">
              修改密码
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="400px"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="currentPassword">
          <el-input
            v-model="passwordForm.currentPassword"
            type="password"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="changePassword" :loading="changingPassword">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

const userStore = useUserStore()
const { userInfo } = storeToRefs(userStore)

// 表单引用
const profileFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

// 加载状态
const saving = ref(false)
const changingPassword = ref(false)

// 对话框状态
const passwordDialogVisible = ref(false)

// 个人信息表单
const profileForm = reactive({
  username: '',
  email: '',
  nickname: '',
  phone: '',
  department: '',
  position: '',
  avatar: ''
})

// 密码修改表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则
const profileRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const passwordRules: FormRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 上传配置
const uploadAction = computed(() => '/api/upload/avatar')
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

// 保存个人信息
const saveProfile = async () => {
  if (!profileFormRef.value) return
  
  try {
    await profileFormRef.value.validate()
    saving.value = true
    
    // TODO: 调用API保存个人信息
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 更新用户信息
    userStore.setUserInfo({
      ...userInfo.value!,
      email: profileForm.email,
      avatar: profileForm.avatar
    })
    
    ElMessage.success('个人信息保存成功')
  } catch (error) {
    console.error('Save profile failed:', error)
  } finally {
    saving.value = false
  }
}

// 显示修改密码对话框
const showChangePasswordDialog = () => {
  Object.assign(passwordForm, {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  passwordDialogVisible.value = true
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    changingPassword.value = true
    
    // TODO: 调用API修改密码
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
  } catch (error) {
    console.error('Change password failed:', error)
    ElMessage.error('密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

// 头像上传前检查
const beforeAvatarUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过2MB')
    return false
  }
  return true
}

// 头像上传成功
const handleAvatarSuccess = (response: any) => {
  profileForm.avatar = response.url
  ElMessage.success('头像上传成功')
}

// 初始化数据
onMounted(() => {
  if (userInfo.value) {
    Object.assign(profileForm, {
      username: userInfo.value.username,
      email: userInfo.value.email,
      avatar: userInfo.value.avatar || '',
      nickname: userInfo.value.username,
      phone: '',
      department: '',
      position: ''
    })
  }
})
</script>

<style scoped lang="scss">
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-section {
  text-align: center;
  
  .avatar-uploader {
    margin-top: 16px;
  }
}

.security-section {
  text-align: center;
}
</style>
