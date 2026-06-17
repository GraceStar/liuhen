/**
 * 应用入口 — Vue 应用启动的起点
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 这个文件做四件事：
 *  1. 创建 Vue 应用实例
 *  2. 安装插件：Pinia（状态管理）+ Vue Router（页面路由）
 *  3. 设置路由守卫：判断是否需要登录
 *  4. 挂载到 index.html 的 <div id="app"> 上
 *
 * 和 Android 的对比：
 *   main.ts     → Application.onCreate()
 *   createRouter → AndroidManifest + NavGraph
 *   Pinia Store → ViewModel
 *   router.beforeEach → 路由拦截器（类似登录检查）
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// ─── 导入页面组件（懒加载会在构建时自动代码分割） ───
import HomeView from './views/HomeView.vue'
import TopicView from './views/TopicView.vue'
import AchievementView from './views/AchievementView.vue'
import LoginView from './views/LoginView.vue'
import RegisterView from './views/RegisterView.vue'

// ─── 路由配置 ───
// 每个路由 = 一个 URL 路径 + 对应的页面组件
// meta.requiresAuth = true 表示需要登录才能访问
const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false },  // 登录页不需要登录
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresAuth: false },  // 注册页不需要登录
  },
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true },
  },
  {
    path: '/topic/:id',
    name: 'topic',
    component: TopicView,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/achievement/:id',
    name: 'achievement',
    component: AchievementView,
    props: true,
    meta: { requiresAuth: true },
  },
]

// createWebHashHistory = URL 里用 # 号分隔（如 /#/topic/1）
// 为什么用 Hash 模式？不需要服务端配置，兼容所有静态服务器
const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// ─── 路由守卫：保护需要登录的页面 ───
// 每次导航发生前（URL 变化、router.push 等）都会调用这个函数
router.beforeEach(async (to, from, next) => {
  // 如果目标页面需要登录...
  if (to.meta.requiresAuth) {
    // 动态导入 auth store（避免循环依赖）
    const { useAuthStore } = await import('@/stores/auth')
    const auth = useAuthStore()

    if (auth.isLoggedIn) {
      // 已登录 → 放行
      next()
    } else {
      // 没登录 → 跳转到登录页
      next({ name: 'login', query: { redirect: to.fullPath } })
    }
  } else {
    // 不需要登录的页面（登录页、注册页）→ 直接放行
    next()
  }
})

// ─── 创建并挂载应用 ───
const app = createApp(App)
app.use(createPinia())  // Pinia 状态管理
app.use(router)         // Vue Router
app.mount('#app')       // 挂载到 index.html 的 #app
