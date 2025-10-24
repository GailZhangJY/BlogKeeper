<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-white shadow">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <!-- Logo和标题 -->
          <div class="flex items-center">
            <img 
              src="/logo.svg" 
              alt="文捕" 
              class="h-8 w-auto" 
              width="32" 
              height="32"
              loading="eager"
              fetchpriority="high"
            />
            <span class="ml-2 text-xl font-semibold text-gray-900">文捕</span>
            <span class="hidden sm:inline-block ml-2 text-sm text-gray-500">博客内容一键解析下载工具</span>
          </div>
          
          <!-- 导航链接 -->
          <nav class="flex space-x-4">
            <router-link 
              to="/" 
              class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              active-class="text-green-600 font-bold"
            >
              首页
            </router-link>
            <a
              href="https://github.com/GailZhangJY/BlogKeeper"
              target="_blank"
              rel="noopener noreferrer"
              class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium flex items-center"
              aria-label="GitHub 仓库"
              title="GitHub"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-5 w-5">
                <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.009-.868-.014-1.703-2.782.605-3.369-1.342-3.369-1.342-.454-1.155-1.11-1.463-1.11-1.463-.908-.62.069-.607.069-.607 1.004.07 1.532 1.032 1.532 1.032.892 1.53 2.341 1.088 2.91.833.091-.647.35-1.088.636-1.339-2.221-.253-4.555-1.113-4.555-4.953 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.269 2.75 1.026A9.564 9.564 0 0 1 12 6.844c.85.004 1.705.115 2.504.337 1.909-1.295 2.748-1.026 2.748-1.026.546 1.378.203 2.397.1 2.65.64.7 1.028 1.595 1.028 2.688 0 3.849-2.337 4.697-4.566 4.945.359.309.679.919.679 1.852 0 1.336-.012 2.415-.012 2.743 0 .268.18.58.688.481A10.019 10.019 0 0 0 22 12.017C22 6.484 17.523 2 12 2z" clip-rule="evenodd"/>
              </svg>
              <span class="ml-2 hidden sm:inline">GitHub</span>
            </a>

            <router-link 
              to="/guide" 
              class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              active-class="text-green-600 font-bold"
            >
              使用说明
            </router-link>
            <router-link 
              to="/changelog" 
              class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              active-class="text-green-600 font-bold"
            >
              更新日志
            </router-link>
            <router-link 
              to="/contact" 
              class="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              active-class="text-green-600 font-bold"
            >
              联系我们
            </router-link>
          </nav>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="flex-1 container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
// 不再需要直接导入 BlogParser，因为它会通过路由加载
</script>
