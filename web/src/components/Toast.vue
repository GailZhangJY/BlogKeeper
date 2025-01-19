<template>
  <Transition name="toast">
    <div v-if="visible" 
      class="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 px-4 py-2 rounded-lg shadow-lg max-w-md"
      :class="typeClass"
    >
      <div class="flex items-start space-x-2">
        <svg v-if="currentType === 'error'" class="w-5 h-5 mt-0.5 shrink-0" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
        </svg>
        <svg v-if="currentType === 'success'" class="w-5 h-5 mt-0.5 shrink-0" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <div class="text-sm font-medium whitespace-pre-line">{{ currentMessage }}</div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const visible = ref(false)
const currentMessage = ref('')
const currentType = ref<'error' | 'success'>('error')
let timer: number | null = null

const typeClass = computed(() => {
  switch (currentType.value) {
    case 'error':
      return 'bg-red-50 text-red-600'
    case 'success':
      return 'bg-green-50 text-green-600'
    default:
      return 'bg-gray-50 text-gray-600'
  }
})

// 定义显示方法
const show = (message: string, type: 'error' | 'success' = 'error', duration = 1000) => {
  // 重置状态
  visible.value = false
  if (timer) clearTimeout(timer)
  
  // 更新消息和类型
  currentMessage.value = message
  currentType.value = type
  
  // 显示新消息
  visible.value = true
  
  // 设置定时器
  timer = window.setTimeout(() => {
    visible.value = false
  }, duration)
}

// 导出方法供父组件使用
defineExpose({ show })
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -1rem);
}
</style>
