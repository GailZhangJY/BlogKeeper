import { createRouter, createWebHistory } from 'vue-router'
import BlogParser from '../components/BlogParser.vue'
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
      path: '/contact',
      name: 'contact',
      component: ContactUs
    }
  ]
})

export default router
