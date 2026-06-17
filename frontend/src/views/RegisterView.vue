<script setup lang="ts">
/**
 * 注册页面 — 简单的用户名 + 密码注册
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 密码没有任何复杂度要求，想用什么就用什么。
 * 注册成功后自动登录，直接跳回主页。
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { UserPlus, ArrowLeft, Loader2, Check } from '@lucide/vue'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const loading = ref(false)

async function handleRegister() {
  // 校验
  if (!username.value.trim() || !password.value.trim()) {
    errorMessage.value = '请输入用户名和密码'
    return
  }
  if (password.value !== confirmPassword.value) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }

  loading.value = true
  errorMessage.value = ''
  try {
    await auth.register(username.value.trim(), password.value)
    router.push('/')  // 注册成功 → 跳主页
  } catch (e: any) {
    errorMessage.value = e?.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

function goLogin() {
  router.push('/login')
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
        <h1 class="text-xl font-bold text-[var(--text-primary)] mt-3">创建账号</h1>
        <p class="text-xs text-[var(--text-tertiary)] mt-1">密码没有复杂度要求，简单好记就行</p>
      </div>

      <!-- 表单 -->
      <form @submit.prevent="handleRegister" class="space-y-3">
        <!-- 用户名 -->
        <div>
          <label class="block text-xs font-medium text-[var(--text-secondary)] mb-1">用户名</label>
          <input
            v-model="username"
            type="text"
            placeholder="给自己起个好记的名字"
            autocomplete="username"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface-alt)] focus:outline-none focus:ring-2 focus:ring-primary-500/30 text-[var(--text-primary)]"
          />
        </div>

        <!-- 密码 -->
        <div>
          <label class="block text-xs font-medium text-[var(--text-secondary)] mb-1">密码（无需复杂要求）</label>
          <input
            v-model="password"
            type="password"
            placeholder="设置密码（简单好记就行）"
            autocomplete="new-password"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface-alt)] focus:outline-none focus:ring-2 focus:ring-primary-500/30 text-[var(--text-primary)]"
          />
        </div>

        <!-- 确认密码 -->
        <div>
          <label class="block text-xs font-medium text-[var(--text-secondary)] mb-1">确认密码</label>
          <input
            v-model="confirmPassword"
            type="password"
            placeholder="再输一遍确认"
            autocomplete="new-password"
            class="w-full px-3 py-2.5 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface-alt)] focus:outline-none focus:ring-2 focus:ring-primary-500/30 text-[var(--text-primary)]"
            @keyup.enter="handleRegister"
          />
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="text-xs text-red-500 bg-red-50 dark:bg-red-900/20 rounded-lg p-2">
          {{ errorMessage }}
        </div>

        <!-- 注册按钮 -->
        <button
          type="submit"
          :disabled="loading"
          class="btn-magnetic w-full flex items-center justify-center gap-2 py-2.5 text-sm font-medium bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-40"
        >
          <Loader2 v-if="loading" :size="16" class="animate-spin" />
          <UserPlus v-else :size="16" />
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <!-- 返回登录 -->
      <div class="text-center">
        <button @click="goLogin" class="text-sm text-[var(--text-secondary)] hover:text-primary-500 flex items-center gap-1 mx-auto">
          <ArrowLeft :size="14" />
          已有账号？去登录
        </button>
      </div>
    </div>
  </div>
</template>
