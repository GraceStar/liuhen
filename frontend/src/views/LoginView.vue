<script setup lang="ts">
/**
 * 登录页面 — 用户名 + 密码登录
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 流程：
 *  1. 用户输入用户名密码
 *  2. 点击「登录」→ 调用 auth.login()
 *  3. 成功 → router.push('/')（跳回主页）
 *  4. 失败 → 显示错误提示
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { LogIn, UserPlus, Loader2 } from '@lucide/vue'

const router = useRouter()
const auth = useAuthStore()

// 表单数据（v-model 双向绑定）
const username = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

async function handleLogin() {
  // 简单校验
  if (!username.value.trim() || !password.value.trim()) {
    errorMessage.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    await auth.login(username.value.trim(), password.value)
    router.push('/')  // 登录成功，跳回主页
  } catch (e: any) {
    // 后端返回的错误信息在 e.response.data.detail 里
    errorMessage.value = e?.response?.data?.detail || '登录失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

function goRegister() {
  router.push('/register')
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-[var(--bg-page)] p-4">
    <div class="card w-full max-w-sm p-8 space-y-6">
      <!-- Logo -->
      <div class="text-center">
        <div class="w-12 h-12 rounded-xl gradient-brand flex items-center justify-center text-white font-bold text-lg mx-auto">
          留
        </div>
        <h1 class="text-xl font-bold text-[var(--text-primary)] mt-3">登录留痕</h1>
        <p class="text-xs text-[var(--text-tertiary)] mt-1">记录你的工作与生活轨迹</p>
      </div>

      <!-- 表单 -->
      <form @submit.prevent="handleLogin" class="space-y-3">
        <!-- 用户名 -->
        <div>
          <label class="block text-xs font-medium text-[var(--text-secondary)] mb-1">用户名</label>
          <input
            v-model="username"
            type="text"
            placeholder="输入用户名"
            autocomplete="username"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface-alt)] focus:outline-none focus:ring-2 focus:ring-primary-500/30 text-[var(--text-primary)]"
          />
        </div>

        <!-- 密码 -->
        <div>
          <label class="block text-xs font-medium text-[var(--text-secondary)] mb-1">密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="输入密码"
            autocomplete="current-password"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface-alt)] focus:outline-none focus:ring-2 focus:ring-primary-500/30 text-[var(--text-primary)]"
            @keyup.enter="handleLogin"
          />
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="text-xs text-red-500 bg-red-50 dark:bg-red-900/20 rounded-lg p-2">
          {{ errorMessage }}
        </div>

        <!-- 登录按钮 -->
        <button
          type="submit"
          :disabled="loading"
          class="btn-magnetic w-full flex items-center justify-center gap-2 py-2.5 text-sm font-medium bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-40"
        >
          <Loader2 v-if="loading" :size="16" class="animate-spin" />
          <LogIn v-else :size="16" />
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <!-- 注册入口 -->
      <div class="text-center">
        <button
          @click="goRegister"
          class="text-sm text-primary-500 hover:text-primary-600 flex items-center gap-1 mx-auto"
        >
          <UserPlus :size="14" />
          还没有账号？去注册
        </button>
      </div>
    </div>
  </div>
</template>
