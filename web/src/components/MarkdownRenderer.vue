<template>
  <div class="markdown-body" v-html="renderedContent"></div>
</template>

<script setup lang="ts">
import { ref, watchEffect } from 'vue'
import { marked } from 'marked'

const props = defineProps<{
  content: string
}>()

const renderedContent = ref('')

watchEffect(() => {
  renderedContent.value = marked(props.content)
})
</script>

<style>
.markdown-body {
  box-sizing: border-box;
  min-width: 200px;
  max-width: 980px;
  margin: 0 auto;
  padding: 25px;
  color: #374151;
  line-height: 1.5;
}

.markdown-body h1 {
  font-size: 1.875em;
  margin-bottom: 0.75em;
  color: #111827;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.3em;
}

.markdown-body h2 {
  font-size: 1.5em;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  color: #1f2937;
  font-weight: 600;
}

.markdown-body h3 {
  font-size: 1.25em;
  margin-top: 1.2em;
  margin-bottom: 0.4em;
  color: #374151;
  font-weight: 600;
}

.markdown-body p {
  margin-bottom: 0.75em;
  line-height: 1.5;
}

.markdown-body ul {
  margin-bottom: 0.75em;
  padding-left: 1.5em;
}

.markdown-body li {
  margin-bottom: 0.25em;
  line-height: 1.5;
}

.markdown-body li::marker {
  color: #10b981;
}

.markdown-body a {
  color: #10b981;
  text-decoration: none;
}

.markdown-body a:hover {
  text-decoration: underline;
}

.markdown-body code {
  background-color: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-size: 0.875em;
  color: #1f2937;
}

.markdown-body pre {
  background-color: #f3f4f6;
  padding: 1em;
  border-radius: 0.5em;
  overflow: auto;
  margin-bottom: 0.75em;
}

.markdown-body pre code {
  background-color: transparent;
  padding: 0;
  font-size: 0.875em;
  color: #1f2937;
}

.markdown-body blockquote {
  border-left: 4px solid #10b981;
  padding-left: 1em;
  margin: 0.75em 0;
  color: #4b5563;
}

.markdown-body hr {
  border: none;
  border-top: 2px solid #e5e7eb;
  margin: 1.5em 0;
}

.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 0.75em;
}

.markdown-body th,
.markdown-body td {
  border: 1px solid #e5e7eb;
  padding: 0.5em 0.75em;
  text-align: left;
}

.markdown-body th {
  background-color: #f9fafb;
  font-weight: 600;
}

.markdown-body img {
  max-width: 100%;
  height: auto;
  border-radius: 0.375em;
  margin: 0.75em 0;
}
</style>
