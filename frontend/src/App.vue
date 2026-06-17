<script setup lang="ts">
/**
 * 留痕 · 根组件
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 这个组件是整个应用的顶层框架：
 *  1. 启动时验证登录状态（checkAuth）
 *  2. 已登录 → 显示 AppLayout（侧栏 + 主内容）
 *  3. 未登录 → 只显示路由视图（登录/注册页）
 */
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppLayout from './layouts/AppLayout.vue'
import { Loader2 } from '@lucide/vue'

const auth = useAuthStore()
// 启动时是否还在检查登录状态
const checking = ref(true)

onMounted(async () => {
  // 从 localStorage 恢复登录态（如果有的话）
  // checkAuth 会调后端 /auth/me 验证 token 是否还有效
  await auth.checkAuth()
  checking.value = false
})
</script>

<template>
  <!-- 启动中：显示加载动画 -->
  <template v-if="checking">
    <div class="min-h-screen flex items-center justify-center bg-[var(--bg-page)]">
      <Loader2 :size="28" class="animate-spin text-primary-500" />
    </div>
  </template>

  <!-- 已登录：带侧栏的完整布局 -->
  <AppLayout v-else-if="auth.isLoggedIn">
    <router-view v-slot="{ Component }">
      <transition name="fade">
        <component :is="Component" />
      </transition>
    </router-view>
  </AppLayout>

  <!-- 未登录：只显示路由内容（登录/注册页，没有侧栏） -->
  <router-view v-else v-slot="{ Component }">
    <transition name="fade">
      <component :is="Component" />
    </transition>
  </router-view>
</template>
