<template>
  <div class="guide-container">
    <MarkdownRenderer :content="guideContent" />
  </div>
</template>

<script setup lang="ts">
import MarkdownRenderer from './MarkdownRenderer.vue'

const guideContent = `
# 文捕使用说明

## 开源-2025.10.24
https://github.com/GailZhangJY/BlogKeeper

一款在线博客内容解析下载工具，支持多个平台，多种格式，尽量保留文章原始排版

## 多平台支持🌐
**微信公众号**/**CSDN**/**博客园**/**简书**/**思否**/**阮一峰的网络日志**/**腾讯云开发者社区**

## 多格式导出📚

**HTML**：保留原始样式

**PDF**：适合归档打印

**Markdown**：便于编辑

**MHTML**：单文件保存，完整备份，离线浏览

## 支持的博客地址✅

**微信公众号：** https://mp.weixin.qq.com/s/bdqcwi0CgkoIvUiKsGBFog

说明：不支持图文消息和音视频下载

**CSDN：** https://blog.csdn.net/GailZhangJY/article/details/145245328

说明：免登录免关注下载文章，不支持付费文章

**博客园：** https://www.cnblogs.com/GailZhangJY/p/18679756

**简书：** https://www.jianshu.com/p/913d17e64c5c

**思否：** https://segmentfault.com/a/1190000046037559

**阮一峰的网络日志：** https://www.ruanyifeng.com/blog/2025/01/weekly-issue-334.html

**腾讯云开发者社区：** https://cloud.tencent.com/developer/article/2488049

## 注意事项⚠️

**确保文章URL可以正常访问**

**对于图片较多的文章，导出可能需要较长时间，请耐心等待**

**若文件解析正常但下载后无法查看，或下载与解析的文件大小不一致，可以尝试下载全部**

**若PDF文件下载没有展示图片，建议使用Typora等工具重新导出**

**不支持需要登录或者付费的博客文章**

**不要过多尝试不支持的博客平台**

**建议使用 Chrome 或 Edge 浏览器**

## 常见问题❓

**Q: 为什么解析失败？**

A: 可能的原因：
- 不支持的博客平台
- 文章需要登录才能访问
- 网络连接不稳定
- 博客反爬机制，请在夜深人静的时候尝试

**Q: 如何批量下载？**

A: 暂时不支持批量解析，但可以同时选择多种格式下载。

**Q: 文件保存在哪里？**

A: 文件会自动下载到浏览器的默认下载目录。
`
</script>

<style scoped>
.guide-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}
</style>
