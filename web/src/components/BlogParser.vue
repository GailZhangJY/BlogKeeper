<template>
  <div class="responsive-container">
    <Toast ref="toastRef" />
    <!-- 链接输入区域 -->
    <div class="section-spacing">
      <div class="input-group">
        <input
          v-model="blogUrl"
          type="text"
          class="input-field"
          placeholder="请输入文章博客链接"
        />
        <button
          @click="clearUrl"
          class="input-button"
        >
          清空
        </button>
      </div>
      <div class="mt-2 flex flex-wrap gap-2">
        <a 
          v-for="platform in supportedPlatforms" 
          :key="platform.name"
          class="platform-tag"
          :href="platform.domain"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ platform.name }}
      </a>
      </div>
    </div>

    <!-- 格式选择区域 -->
    <div class="section-spacing">
      <label class="responsive-text font-medium text-gray-700 mb-2 block">导出格式</label>
      <div class="flex flex-wrap gap-2">
        <label 
          v-for="format in formats" 
          :key="format.value"
          class="relative flex items-center justify-center shrink-0"
        >
          <input
            type="checkbox"
            v-model="selectedFormats"
            :value="format.value"
            class="sr-only"
          />
          <div 
            :class="[
              'format-item whitespace-nowrap',
              selectedFormats.includes(format.value) ? 'format-item-selected' : ''
            ]"
          >
            {{ format.label }}
          </div>
        </label>
      </div>
    </div>

    <!-- 解析按钮 -->
    <button
      @click="parseContent"
      class="w-full bg-blue-500 text-white px-6 py-3 rounded-lg font-medium
             hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500
             disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
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

    <!-- 解析结果区域 -->
    <div v-if="results.length > 0" class="mt-8">
      <div class="results-header">
        <h2 class="responsive-heading">解析结果</h2>
        <button
          v-if="results.length > 1"
          @click="downloadAll"
          class="download-all-button"
        >
          <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          下载全部
        </button>
      </div>
      <div class="space-y-4">
        <div v-for="(result, index) in results" 
             :key="index"
             class="results-item">
          <div class="flex-1 min-w-0">
            <p class="results-filename">
              {{ truncateFileName(result.title) }}
            </p>
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100">
              {{ result.format }}
            </span>
            <p class="mt-1 text-sm text-gray-500">
              {{ formatFileSize(result.size) }}
            </p>
          </div>
          <button
            @click="() => downloadFile(result)"
            class="download-button"
          >
            <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            下载
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useDebounce } from '@vueuse/core'
import { getFileNameFromResponse } from '@/utils/fileUtils'
import { API_CONFIG } from '@/config'
import Toast from './Toast.vue'

const apiHost = ref(API_CONFIG.HOST)
const blogUrl = ref('')
const debouncedBlogUrl = useDebounce(blogUrl, 300)
const urlValidationCache = new Map()
const isUrlValid = ref(false)

// 异步验证 URL
const validateUrl = async (url: string) => {
  if (!url) return false
  if (urlValidationCache.has(url)) {
    return urlValidationCache.get(url)
  }
  
  try {
    // const isValid = supportedPlatforms.some(platform => 
    //   url.includes(platform.domain)
    // )
    const isValid = true
    urlValidationCache.set(url, isValid)
    return isValid
  } catch {
    urlValidationCache.set(url, false)
    return false
  }
}

// 监听 URL 变化并更新验证状态
watch(debouncedBlogUrl, async (newUrl) => {
  isUrlValid.value = await validateUrl(newUrl)
}, { immediate: true })

// 使用同步计算属性
const canParse = computed(() => {
  return blogUrl.value.trim() !== '' && selectedFormats.value.length > 0 && isUrlValid.value
})

// 测试数据
const testResults = [
  {
    title: '我去，今天被腾讯游戏装到了-游戏葡萄-微信公众号-2024-12-03',
    download_url: '#',
    size: 1024,
    format: 'html',
  },
  {
    title: '这是一个非常非常非常长的文件名用来测试移动端展示效果',
    download_url: '#',
    size: 2048,
    format: 'pdf',
  },
  {
    title: '正常长度的文件名测试',
    download_url: '#',
    size: 512,
    format: 'md',
  }
]

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
  filename: string
  originalFilename?: string
}

interface ErrorResponse {
  detail: {
    code: number;
    type: string;
    message: string;
    suggestion?: string;
  };
}

const formats: Format[] = [
  { label: 'HTML', value: 'html' },
  { label: 'Markdown', value: 'md' },
  { label: 'PDF', value: 'pdf' },
  { label: 'MHTML', value: 'mhtml' }
]

const supportedPlatforms: Platform[] = [
  { name: '微信公众号', domain: 'https://mp.weixin.qq.com/s/bdqcwi0CgkoIvUiKsGBFog' },
  { name: 'CSDN', domain: 'https://blog.csdn.net' },
  { name: '博客园', domain: 'https://www.cnblogs.com' },
  { name: '简书', domain: 'https://www.jianshu.com' },
  //{ name: '知乎', domain: 'zhihu.com' },
  //{ name: '掘金', domain: 'https://juejin.cn' },
  { name: '思否', domain: 'https://segmentfault.com/blogs' },
  { name: '阮一峰的网络日志', domain: 'https://ruanyifeng.com/blog/' },
  { name: '腾讯云开发者社区', domain: 'https://cloud.tencent.com/developer' },
  //{ name: '阿里云开发者社区', domain: 'https://developer.aliyun.com' },
  //{ name: '华为云开发者社区', domain: 'https://bbs.huaweicloud.com/' },
]

const selectedFormats = ref<string[]>(['html'])
const results = ref<ParseResult[]>([])
const isTestMode = ref(false)  // 开发测试模式
const toastRef = ref<InstanceType<typeof Toast> | null>(null)
const isLoading = ref(false)

const clearUrl = () => {
  blogUrl.value = ''
  urlValidationCache.clear()
  isUrlValid.value = false
  results.value = []  // 清除解析结果
  selectedFormats.value = ['html']
}

const parseContent = async () => {
  if (!canParse.value) return
  
  isLoading.value = true
  try {
    if (isTestMode.value) {
      setTimeout(() => {
        results.value = testResults.map(result => {
          return { 
            ...result, 
            filename: `${result.title}.${result.format}`,
            originalFilename: `${result.title}.${result.format}`
          }
        })
        isLoading.value = false
      }, 500)
      return
    }

    const response = await fetch(`${apiHost.value}/parse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: blogUrl.value,
        formats: selectedFormats.value,
        fileContent: false
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      const error = data as ErrorResponse
      let errorMessage = error.detail.message
      
      // 如果有建议信息，添加到错误信息中
      if (error.detail.suggestion) {
        errorMessage += `\n${error.detail.suggestion}`
      }

      toastRef.value?.show(errorMessage, 'error', 5000)
      throw new Error(errorMessage)
    }

    results.value = data.map((result: Omit<ParseResult, 'filename'>) => ({
      ...result,
      filename: `${result.title}.${result.format}`,
      originalFilename: `${result.title}.${result.format}`
    }))

    toastRef.value?.show('解析成功', 'success', 2000)
  } catch (error: any) {
    console.error('解析失败:', error)
    toastRef.value?.show(error.message || '解析失败，请稍后重试', 'error', 3000)
  } finally {
    isLoading.value = false
  }
}

const isMobile = ref(window.innerWidth <= 768)

onMounted(() => {
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth <= 768
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    isMobile.value = window.innerWidth <= 768
  })
})

const truncateFileName = (filename: string): string => {
  const maxLength = isMobile.value ? 20 : 50
  
  // 如果文件名长度在限制内，直接返回
  if (filename.length <= maxLength) return filename
  
  // 截断文件名
  return filename.slice(0, maxLength - 3) + '...'
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
    const downloadUrl = `${apiHost.value}${result.download_url}`
    const response = await fetch(downloadUrl)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = result.originalFilename || result.filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
    toastRef.value?.show('下载成功', 'success', 1000)
  } catch (error) {
    console.error('下载失败:', error)
    toastRef.value?.show('下载失败，请稍后重试', 'error', 1000)
  }
}

const downloadAll = async () => {
  try {
    const downloadUrl = `${apiHost.value}/batch-download`
    console.log('批量下载地址:', downloadUrl)
    
    const response = await fetch(downloadUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        files: results.value.map(result => ({
          url: result.download_url,
          filename: result.originalFilename || result.filename
        }))
      }),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const blob = await response.blob()
    const fileName = getFileNameFromResponse(response) || 'blog_articles.zip'
    
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fileName
    
    document.body.appendChild(a)
    a.click()
    
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    toastRef.value?.show('批量下载成功', 'success', 1000)
  } catch (error: unknown) {
    const errorDetails = {
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      results: results.value
    }
    console.error('批量下载出错 - 详细信息:', errorDetails)
    toastRef.value?.show(`批量下载文件时出错:\n${errorDetails.message}\n\n请查看控制台了解详细信息`, 'error', 1000)
  }
}
</script>

<style>
.download-all-button {
  @apply inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500;
}
</style>
