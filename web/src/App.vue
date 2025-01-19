<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-white shadow">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-4">
          <!-- Logo和标题 -->
          <div class="flex items-center">
            <img src="/logo.svg" alt="文捕" class="h-8 w-auto" />
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
