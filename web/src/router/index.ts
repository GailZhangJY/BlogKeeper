import { createRouter, createWebHistory } from 'vue-router'
import BlogParser from '../components/BlogParser.vue'
import Guide from '../components/Guide.vue'
import Changelog from '../components/Changelog.vue'
import ContactUs from '../components/ContactUs.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: BlogParser
    },
    {
      path: '/guide',
      name: 'guide',
      component: Guide
    },
    {
      path: '/changelog',
      name: 'changelog',
      component: Changelog
    },
    {
      path: '/contact',
      name: 'contact',
      component: ContactUs
    }
  ]
})

export default router
