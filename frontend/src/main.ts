import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// Views
import HomeView from './views/HomeView.vue'
import TopicView from './views/TopicView.vue'
import AchievementView from './views/AchievementView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/topic/:id', name: 'topic', component: TopicView, props: true },
  { path: '/achievement/:id', name: 'achievement', component: AchievementView, props: true },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
