<template>
  <div class="bg-white shadow-lg rounded-lg p-6">
    <!-- 链接输入区域 -->
    <div class="mb-6">
      <div class="flex">
        <input
          v-model="blogUrl"
          type="text"
          class="flex-1 px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="请输入博客链接 (支持CSDN、博客园、知乎、掘金、微信公众号)"
        />
        <button
          @click="clearUrl"
          class="px-4 py-2 text-gray-500 hover:text-gray-700 border-t border-b border-r border-gray-300 rounded-r-lg"
        >
          清空
        </button>
      </div>
      <div class="mt-2 flex flex-wrap gap-2">
        <span 
          v-for="platform in supportedPlatforms" 
          :key="platform.name"
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
        >
          {{ platform.name }}
        </span>
      </div>
    </div>

    <!-- 格式选择区域 -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">导出格式</label>
      <div class="flex flex-wrap gap-4">
        <label 
          v-for="format in formats" 
          :key="format.value"
          class="relative flex items-center justify-center"
        >
          <input
            type="checkbox"
            v-model="selectedFormats"
            :value="format.value"
            class="sr-only peer"
          />
          <div class="px-4 py-2 rounded-lg border cursor-pointer 
                     peer-checked:bg-blue-500 peer-checked:text-white
                     peer-checked:border-blue-500
                     hover:bg-gray-50 peer-checked:hover:bg-blue-600">
            {{ format.label }}
          </div>
        </label>
      </div>
    </div>

    <!-- 解析按钮 -->
    <button
      @click="parseContent"
      class="w-full bg-blue-500 text-white px-6 py-3 rounded-lg font-medium
             hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
             disabled:opacity-50 disabled:cursor-not-allowed"
      :disabled="isLoading || !canParse"
    >
      <span v-if="isLoading" class="flex items-center justify-center">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        解析中...
      </span>
      <span v-else>开始解析</span>
    </button>

    <!-- 结果显示区域 -->
    <div v-if="results.length > 0" class="mt-8">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-medium text-gray-900">解析结果</h2>
        <button
          v-if="results.length > 1"
          @click="downloadAll"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-500 hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
          打包下载全部
        </button>
      </div>
      <div class="space-y-4">
        <div
          v-for="(result, index) in results"
          :key="index"
          class="bg-gray-50 p-4 rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
        >
          <div class="flex justify-between items-center">
            <div class="flex-1">
              <p class="font-medium truncate">{{ result.title }}</p>
              <div class="flex items-center text-sm text-gray-500 mt-1 space-x-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100">
                  {{ result.format }}
                </span>
                <span>{{ formatFileSize(result.size) }}</span>
              </div>
            </div>
            <button
              @click="downloadFile(result)"
              class="ml-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-500 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              下载
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import { getFileNameFromResponse } from '@/utils/fileUtils';
import { API_CONFIG } from '@/config'

const apiHost = ref(API_CONFIG.HOST)
const blogUrl = ref('')
const isLoading = ref(false)
const selectedFormats = ref<string[]>(['html'])
const results = ref<ParseResult[]>([])

interface Format {
  label: string
  value: string
}

interface Platform {
  name: string
  domain: string
}

interface ParseResult {
  title: string
  download_url: string
  size: number
  format: string
}

const formats: Format[] = [
  { label: 'HTML', value: 'html' },
  { label: 'Markdown', value: 'md' },
  { label: 'PDF', value: 'pdf' },
  { label: 'MHTML', value: 'mhtml' }
]

const supportedPlatforms: Platform[] = [
  { name: 'CSDN', domain: 'csdn.net' },
  { name: '博客园', domain: 'cnblogs.com' },
  { name: '知乎', domain: 'zhihu.com' },
  { name: '掘金', domain: 'juejin.cn' },
  { name: '微信公众号', domain: 'weixin.qq.com' }
]

const canParse = computed(() => {
  return blogUrl.value.trim() !== '' && selectedFormats.value.length > 0
})

const clearUrl = () => {
  blogUrl.value = ''
  results.value = []  // 清除解析结果
}

const parseContent = async () => {
  if (!canParse.value) return
  
  isLoading.value = true
  try {
    const response = await fetch(`${apiHost.value}/parse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: blogUrl.value,
        formats: selectedFormats.value,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    results.value = data
  } catch (error) {
    console.error('解析失败:', error)
    alert('解析失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const downloadFile = async (result: ParseResult) => {
  try {
    console.log('开始下载文件:', result)
    const downloadUrl = `${apiHost.value}${result.download_url}`
    console.log('下载地址:', downloadUrl)
    
    const response = await fetch(downloadUrl)
    console.log('服务器响应状态:', response.status, response.statusText)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('服务器错误响应:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        errorText
      })
      throw new Error(`下载失败: ${response.status} ${response.statusText}\n${errorText}`)
    }
    
    const blob = await response.blob()
    console.log('文件下载完成，大小:', blob.size, '字节')
    
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = result.title + '.' + result.format
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    console.log('文件下载成功:', result.title + '.' + result.format)
  } catch (error: any) {
    const errorDetails = {
      message: error.message,
      stack: error.stack,
      result: result
    }
    console.error('下载出错 - 详细信息:', errorDetails)
    alert(`下载文件时出错:\n${error.message}\n\n请查看控制台了解详细信息`)
  }
}

const downloadAll = async () => {
  try {
    console.log('开始批量下载文件:', results.value)
    const downloadUrl = `${apiHost.value}/batch-download`
    console.log('批量下载地址:', downloadUrl)
    
    // 构建下载请求
    const response = await fetch(downloadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        files: results.value.map(result => ({
          url: result.download_url,
          filename: result.title + '.' + result.format
        }))
      })
    })
    
    console.log('服务器响应状态:', response.status, response.statusText)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('服务器错误响应:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        errorText
      })
      throw new Error(`批量下载失败: ${response.status} ${response.statusText}\n${errorText}`)
    }
    
    const blob = await response.blob()
    console.log('打包文件下载完成，大小:', blob.size, '字节')
    
    const fileName = getFileNameFromResponse(response);
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fileName || 'download.zip' // 使用解析的文件名，如果没有则使用默认名
    
    // 触发下载
    document.body.appendChild(a)
    a.click()
    
    // 清理
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    console.log('打包下载成功')
  } catch (error: any) {
    const errorDetails = {
      message: error.message,
      stack: error.stack,
      results: results.value
    }
    console.error('批量下载出错 - 详细信息:', errorDetails)
    alert(`批量下载文件时出错:\n${error.message}\n\n请查看控制台了解详细信息`)
  }
}
</script>
