/**
 * 认证 Store — 管理用户登录状态
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 核心职责：
 *  1. 存储 JWT 令牌和用户信息到 localStorage（关闭浏览器也不丢）
 *  2. 提供 login / register / logout 方法
 *  3. 判断是否已登录（isLoggedIn）
 *  4. 应用启动时自动检查 token 是否还有效
 *
 * 数据流：
 *  登录 → 后端返回 { token, user } → 存 localStorage
 *  → 其他 API 调用时从 localStorage 读取 token → 放 Authorization 头
 *  → 后端 get_current_user 验证 token → 识别用户
 */
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import http from '@/api'
import * as api from '@/api'
import type { User } from '@/types'

/** 存储键名 — 键放 localStorage 里用的名字 */
const TOKEN_KEY = 'liuhen-token'
const USER_KEY = 'liuhen-user'

export const useAuthStore = defineStore('auth', () => {
  // ─── 状态 ───
  // ref 是 Vue 的响应式变量，类似 Android LiveData
  // 值变了界面会自动刷新
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref<User | null>(null)

  // 从 localStorage 恢复用户信息
  const saved = localStorage.getItem(USER_KEY)
  if (saved) {
    try { user.value = JSON.parse(saved) } catch { /* ignore */ }
  }
  const loading = ref(false)

  // ─── 计算属性 ───
  const isLoggedIn = computed(() => !!token.value && !!user.value)

  // ─── 辅助函数 ───
  /** 持久化 token 和用户信息到 localStorage + axios */
  function persist(t: string, u: User) {
    token.value = t
    user.value = u
    localStorage.setItem(TOKEN_KEY, t)
    localStorage.setItem(USER_KEY, JSON.stringify(u))
    // 设置 axios 默认请求头 —— 后续所有 API 调用自动带 token
    http.defaults.headers.common['Authorization'] = `Bearer ${t}`
  }

  /** 清除登录状态 */
  function clear() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    // 清除 axios 请求头
    delete http.defaults.headers.common['Authorization']
  }

  // ─── 公开方法 ───

  /** 注册新用户 */
  async function register(username: string, password: string) {
    loading.value = true
    try {
      const result = await api.register(username, password)
      persist(result.token, result.user)
      return result
    } finally {
      loading.value = false
    }
  }

  /** 登录 */
  async function login(username: string, password: string) {
    loading.value = true
    try {
      const result = await api.login(username, password)
      persist(result.token, result.user)
      return result
    } finally {
      loading.value = false
    }
  }

  /** 退出登录 — 清除所有状态并跳转登录页 */
  function logout() {
    clear()
  }

  /**
   * 检查登录状态 — 应用启动时调用
   * 如果有 token，调 /auth/me 验证是否还有效
   * 返回 true = 已登录，false = 需要登录
   */
  async function checkAuth(): Promise<boolean> {
    if (!token.value) return false

    // 先设置 axios 请求头
    http.defaults.headers.common['Authorization'] = `Bearer ${token.value}`

    try {
      const u = await api.getMe()
      user.value = u
      localStorage.setItem(USER_KEY, JSON.stringify(u))
      return true
    } catch {
      // token 过期或无效 → 清除状态 → 跳到登录页
      clear()
      return false
    }
  }

  return {
    token, user, loading, isLoggedIn,
    register, login, logout, checkAuth,
  }
})
