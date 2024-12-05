<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <img src="/logo.svg" alt="文捕" class="h-8 w-auto" />
            <span class="ml-2 text-xl font-semibold text-gray-900">文捕</span>
            <span class="hidden sm:inline-block ml-2 text-sm text-gray-500">博客内容捕手</span>
          </div>
          <nav class="flex space-x-4 sm:space-x-8">
            <a href="/" class="text-gray-900 hover:text-gray-600 px-3 py-2 rounded-md text-sm font-medium">首页</a>
            <a href="/help" class="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">使用教程</a>
            <a href="/contact" class="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">联系我们</a>
          </nav>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="flex-1 container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <BlogParser />
    </main>
  </div>
</template>

<script setup lang="ts">
import BlogParser from './components/BlogParser.vue'
</script>
