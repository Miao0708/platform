<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">评审报告</h1>
      <p class="page-description">{{ taskInfo.name }}</p>
    </div>

    <el-card>
      <div class="report-content">
        <h3>AI评审结果</h3>
        <div class="report-text">
          {{ reportContent }}
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const taskInfo = ref({
  name: '用户登录模块代码评审'
})

const reportContent = ref(`
## 代码评审报告

### 总体评价
本次代码变更主要涉及用户登录模块的安全性改进，整体代码质量良好。

### 发现的问题

#### 1. 安全问题
- **密码明文传输**: 在登录接口中发现密码以明文形式传输，建议使用HTTPS或对密码进行加密处理
- **SQL注入风险**: 用户名参数直接拼接到SQL语句中，存在SQL注入风险

#### 2. 性能问题
- **数据库连接未释放**: 在某些异常情况下，数据库连接可能未正确释放

#### 3. 代码规范
- **变量命名**: 部分变量命名不够清晰，建议使用更有意义的名称
- **注释缺失**: 关键业务逻辑缺少必要的注释说明

### 建议改进

1. 使用参数化查询防止SQL注入
2. 实现密码加密传输机制
3. 添加数据库连接池管理
4. 完善错误处理和日志记录
5. 增加单元测试覆盖

### 风险等级
- 高风险: 2个
- 中风险: 1个
- 低风险: 2个
`)

onMounted(() => {
  // 根据路由参数加载报告内容
  const taskId = route.params.id
  console.log('Loading report for task:', taskId)
})
</script>

<style scoped lang="scss">
.report-content {
  h3 {
    margin-bottom: 20px;
    color: #333;
  }
  
  .report-text {
    white-space: pre-wrap;
    line-height: 1.6;
    color: #666;
    background: #f8f9fa;
    padding: 20px;
    border-radius: 6px;
  }
}
</style>
