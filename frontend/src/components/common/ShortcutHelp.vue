<template>
  <el-dialog
    v-model="visible"
    title="快捷键帮助"
    width="600px"
    class="shortcut-help-dialog"
  >
    <div class="shortcut-help">
      <div class="help-section">
        <h3>全局快捷键</h3>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>K</kbd>
            </div>
            <div class="shortcut-desc">全局搜索</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>H</kbd>
            </div>
            <div class="shortcut-desc">返回首页</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>A</kbd>
            </div>
            <div class="shortcut-desc">打开AI助手</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>R</kbd>
            </div>
            <div class="shortcut-desc">需求管理</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>D</kbd>
            </div>
            <div class="shortcut-desc">代码Diff</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd>
            </div>
            <div class="shortcut-desc">流水线</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>C</kbd>
            </div>
            <div class="shortcut-desc">基础配置</div>
          </div>

          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>T</kbd>
            </div>
            <div class="shortcut-desc">测试点管理</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>/</kbd>
            </div>
            <div class="shortcut-desc">显示快捷键帮助</div>
          </div>
        </div>
      </div>
      
      <div class="help-section">
        <h3>AI助手快捷键</h3>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>Enter</kbd>
            </div>
            <div class="shortcut-desc">发送消息</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>N</kbd>
            </div>
            <div class="shortcut-desc">新建对话</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>L</kbd>
            </div>
            <div class="shortcut-desc">清空对话</div>
          </div>
        </div>
      </div>
      
      <div class="help-section">
        <h3>编辑器快捷键</h3>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>S</kbd>
            </div>
            <div class="shortcut-desc">保存文档</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>O</kbd>
            </div>
            <div class="shortcut-desc">AI优化</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>B</kbd>
            </div>
            <div class="shortcut-desc">加粗文本</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>I</kbd>
            </div>
            <div class="shortcut-desc">斜体文本</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>K</kbd>
            </div>
            <div class="shortcut-desc">插入链接</div>
          </div>
        </div>
      </div>
      
      <div class="help-section">
        <h3>表格操作快捷键</h3>
        <div class="shortcut-list">
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>A</kbd>
            </div>
            <div class="shortcut-desc">全选</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Ctrl</kbd> + <kbd>F</kbd>
            </div>
            <div class="shortcut-desc">页面内搜索</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>F5</kbd>
            </div>
            <div class="shortcut-desc">刷新页面</div>
          </div>
          
          <div class="shortcut-item">
            <div class="shortcut-keys">
              <kbd>Esc</kbd>
            </div>
            <div class="shortcut-desc">关闭对话框</div>
          </div>
        </div>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">关闭</el-button>
        <el-button type="primary" @click="printShortcuts">打印快捷键</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 打印快捷键
const printShortcuts = () => {
  window.print()
}
</script>

<style scoped lang="scss">
.shortcut-help-dialog {
  :deep(.el-dialog__body) {
    padding: 20px;
    max-height: 70vh;
    overflow-y: auto;
  }
}

.shortcut-help {
  .help-section {
    margin-bottom: 24px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    h3 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      border-bottom: 1px solid #e4e7ed;
      padding-bottom: 8px;
    }
  }
  
  .shortcut-list {
    display: grid;
    gap: 12px;
  }
  
  .shortcut-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    background: #f8f9fa;
    border-radius: 6px;
    transition: background-color 0.3s;
    
    &:hover {
      background: #e9ecef;
    }
  }
  
  .shortcut-keys {
    display: flex;
    align-items: center;
    gap: 4px;
    font-family: 'Courier New', monospace;
    
    kbd {
      display: inline-block;
      padding: 2px 6px;
      font-size: 12px;
      line-height: 1.4;
      color: #495057;
      background-color: #ffffff;
      border: 1px solid #ced4da;
      border-radius: 3px;
      box-shadow: 0 1px 0 rgba(0, 0, 0, 0.1);
      font-family: 'Courier New', monospace;
      font-weight: 600;
    }
  }
  
  .shortcut-desc {
    color: #606266;
    font-size: 14px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

// 打印样式
@media print {
  .shortcut-help {
    .help-section {
      break-inside: avoid;
      margin-bottom: 20px;
      
      h3 {
        color: #000;
        border-bottom: 1px solid #000;
      }
    }
    
    .shortcut-item {
      background: transparent !important;
      border: 1px solid #ddd;
      margin-bottom: 4px;
      
      .shortcut-keys kbd {
        background: #f5f5f5;
        border: 1px solid #ccc;
      }
    }
  }
}
</style>
