<template>
  <div class="changelog-container">
    <MarkdownRenderer :content="changelogContent" />
  </div>
</template>

<script setup lang="ts">
import MarkdownRenderer from './MarkdownRenderer.vue'

const changelogContent = `# 文捕更新日志

## 说明
本站代码90%使用AI开发

开发工具：windsurf
后端：Python + 前端：Vue3

若是还没有支持的平台，比如掘金，主要是本人太菜，还不会，没有逆向基础

## 未来计划

### 计划支持的平台
- [ ] 主要看大家的需要，在看log添加添加支持

### 计划的功能
- [ ] 支持博客收录系统，请求呼声多的博客平台优先支持

## 更新历史

#### 2025-01-19
- [x] 增加使用说明页面
- [x] 增加更新日志页面
- [x] 优化Toast报错信息
- [x] 修复简书作者名获取

#### 2025-01-18
- [x] 增加阮一峰的网络日志平台支持
- [x] 增加腾讯云平台支持
- [x] 优化Log输出

#### 2025-01-17
- [x] 获得科技爱好者周刊推荐
- [x] https://github.com/ruanyf/weekly/blob/master/docs/issue-334.md
- [x] https://www.ruanyifeng.com/blog/2025/01/weekly-issue-334.html

#### 2025-01-16
- [x] 自荐科技爱好者周刊，提交issue
- [x] https://github.com/ruanyf/weekly/issues/5933

#### 2024-12-24
- [x] 支持返回html/md文件内容，方便coze调用
- [x] 增加Coze机器人，支持微信公众号一键转存飞书
- [x] https://www.coze.cn/space/7438590937032622099/bot/7451868613352816692

#### 2024-12-13
- [x] SEO优化

#### 2024-12-5
- [x] 优化CSS处理速度
- [x] 多线程优化文章处理速度
- [x] 支持响应式页面
- [x] 凌晨定期清理文件目录

#### 2024-12-4
- [x] 优化PDF展示
- [x] 域名
- [x] 支持简书

#### 2024-11-29
- [x] Github提交
- [x] 完善前后端交互
- [x] 支持Docker和部署脚本

#### 2024-11-28
- [x] 核心功能完善
- [x] 支持博客园/CSDN/微信公众号
- [x] 前端页面实现

#### 2024-11-27
- [x] 第一行代码

`
</script>

<style scoped>
.changelog-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}
</style>
