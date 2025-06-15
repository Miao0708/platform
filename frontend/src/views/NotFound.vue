<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <div class="error-message">页面不存在</div>
      <div class="error-description">
        抱歉，您访问的页面不存在或已被删除
      </div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">
          返回首页
        </el-button>
        <el-button @click="goBack">
          返回上页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped lang="scss">
.not-found-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  
  .not-found-content {
    text-align: center;
    
    .error-code {
      font-size: 120px;
      font-weight: 600;
      color: #409eff;
      line-height: 1;
      margin-bottom: 24px;
    }
    
    .error-message {
      font-size: 24px;
      color: #333;
      margin-bottom: 16px;
    }
    
    .error-description {
      font-size: 16px;
      color: #666;
      margin-bottom: 32px;
    }
    
    .error-actions {
      .el-button + .el-button {
        margin-left: 16px;
      }
    }
  }
}
</style>
