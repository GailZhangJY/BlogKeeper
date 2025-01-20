<!-- 联系我们组件 -->
<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
    <h2 class="text-3xl font-bold text-center text-gray-900 mb-12">联系我们</h2>
    
    <div class="flex justify-center">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-4xl">
        <!-- Twitter -->
        <div class="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 flex flex-col items-center justify-between h-50">
          <div class="flex items-center justify-center space-x-3">
            <img 
              src="/twitter.svg" 
              alt="Twitter" 
              class="h-6 w-6" 
              width="24" 
              height="24" 
              loading="lazy"
            />
            <h3 class="text-lg font-medium text-gray-900">Twitter</h3>
          </div>
          <a 
            href="https://x.com/ZhangJY929" 
            target="_blank"
            class="text-green-600 hover:text-green-700 hover:underline text-center"
          >
            @ZhangJY929
          </a>
        </div>

        <!-- Email -->
        <div class="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 flex flex-col items-center justify-between h-50">
          <div class="flex items-center justify-center space-x-3">
            <img 
              src="/email.png" 
              alt="电子邮箱" 
              class="h-7 w-7" 
              width="28" 
              height="28" 
              loading="lazy"
            />
            <h3 class="text-lg font-medium text-gray-900">电子邮箱</h3>
          </div>
          <a 
            href="mailto:blog-keeper@zhangjy.me"
            class="text-green-600 hover:text-green-700 hover:underline text-center"
          >
          blog-keeper@zhangjy.me
          </a>
        </div>

        <!-- WeChat -->
        <div class="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 flex flex-col items-center justify-between h-50">
          <div class="flex items-center justify-center space-x-3">
            <img 
              src="/wechat.svg" 
              alt="微信公众号" 
              class="h-7 w-7" 
              width="28" 
              height="28" 
              loading="lazy"
            />
            <h3 class="text-lg font-medium text-gray-900">微信公众号</h3>
          </div>
          <div class="text-center">
            <img 
              src="/qrcode.jpg" 
              alt="微信公众号二维码" 
              class="w-20 h-20 object-cover rounded cursor-pointer transition-transform hover:scale-105 mx-auto" 
              width="80" 
              height="80" 
              loading="lazy"
              @click="showQRCode = true"
            />
            <p class="text-sm text-gray-600 mt-2">点击二维码放大查看</p>
          </div>
        </div>
      </div>
    </div>

    <!-- QR Code Modal -->
    <div 
      v-if="showQRCode" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showQRCode = false"
    >
      <div class="bg-white p-6 rounded-lg max-w-sm w-full mx-4">
        <img 
          src="/qrcode_max.jpg" 
          alt="微信公众号二维码" 
          class="w-full h-auto rounded" 
          width="400" 
          height="400" 
          loading="lazy"
        />
        <p class="text-center text-gray-900 font-medium mt-4">扫码关注公众号</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showQRCode = ref(false)
</script>
