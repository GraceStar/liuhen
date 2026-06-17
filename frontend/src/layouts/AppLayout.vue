<script setup lang="ts">
/**
 * 应用布局 — 侧栏导航 + 主内容区 + 主题切换 + 用户信息
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 类比 Android：这是带 DrawerLayout + BottomNavigation 的主 Activity 布局。
 */
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useDataStore } from '@/stores/data'
import { useAuthStore } from '@/stores/auth'
import { Sun, Moon, Monitor, Pencil, Trash2, LayoutDashboard, BarChart3, Menu, X, LogOut, User } from '@lucide/vue'
import type { ThemeMode, Topic } from '@/types'
import EditTopicDialog from '@/components/EditTopicDialog.vue'

const router = useRouter()
const route = useRoute()
const theme = useThemeStore()
const data = useDataStore()
const auth = useAuthStore()

const mobileMenuOpen = ref(false)
const editingTopic = ref<Topic | null>(null)

const themeOptions: { mode: ThemeMode; icon: any; label: string }[] = [
  { mode: 'light', icon: Sun, label: '浅色' },
  { mode: 'dark', icon: Moon, label: '深色' },
  { mode: 'system', icon: Monitor, label: '跟随系统' },
]

const categoryLabels: Record<string, string> = {
  work: '工作',
  study: '学习',
  observe: '观察',
}

onMounted(async () => {
  await data.loadCategories()
  await data.loadTopics()
  // 如果有主题，默认选中第一个
  if (data.topics.length > 0 && !data.activeTopicId) {
    data.selectTopic(data.topics[0].id)
  }
})

function goTopic(topicId: number) {
  mobileMenuOpen.value = false
  router.push(`/topic/${topicId}`)
}

function goHome() {
  mobileMenuOpen.value = false
  router.push('/')
}

function goAchievement(topicId: number) {
  mobileMenuOpen.value = false
  router.push(`/achievement/${topicId}`)
}

function openEdit(topic: Topic) {
  editingTopic.value = topic
}

async function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-[var(--bg-page)]">
    <!-- 手机遮罩 -->
    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 bg-black/30 z-20 lg:hidden"
      @click="mobileMenuOpen = false"
    />

    <!-- ─── 侧栏 ─── -->
    <aside
      :class="[
        'fixed lg:static inset-y-0 left-0 z-30 w-64 flex flex-col',
        'bg-[var(--bg-surface)] border-r border-[var(--border-color)]',
        'transition-transform duration-200',
        mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
      ]"
    >
      <!-- Logo -->
      <div class="flex items-center justify-between px-5 h-14 border-b border-[var(--border-color)] shrink-0">
        <router-link to="/" class="flex items-center gap-2.5" @click="mobileMenuOpen = false">
          <div class="w-8 h-8 rounded-lg gradient-brand flex items-center justify-center text-white font-bold text-sm">
            留
          </div>
          <span class="font-semibold text-[var(--text-primary)] tracking-tight">留痕</span>
        </router-link>
        <button class="lg:hidden p-1.5 rounded-md hover:bg-[var(--bg-surface-hover)]" @click="mobileMenuOpen = false">
          <X :size="18" />
        </button>
      </div>

      <!-- 导航区 -->
      <nav class="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <!-- 首页 -->
        <button
          @click="goHome"
          :class="[
            'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
            route.name === 'home'
              ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-300 font-medium'
              : 'text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)]',
          ]"
        >
          <LayoutDashboard :size="18" />
          总览面板
        </button>

        <!-- 按分类分组主题 -->
        <div v-for="cat in data.categories" :key="cat.id" class="pt-2">
          <p class="px-3 text-xs font-medium text-[var(--text-tertiary)] uppercase tracking-wider mb-1">
            {{ cat.name }}
          </p>
          <div v-for="topic in data.topics.filter(t => t.categoryId === cat.id)" :key="topic.id" class="group">
            <div class="flex items-center">
              <button
                @click="goTopic(topic.id)"
                :class="[
                  'flex-1 flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors text-left',
                  data.activeTopicId === topic.id
                    ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-300 font-medium'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)]',
                ]"
              >
                <span class="w-2 h-2 rounded-full shrink-0" :style="{ background: topic.color || '#5b7c99' }" />
                <span class="truncate">{{ topic.name }}</span>
              </button>

              <!-- 操作按钮 -->
              <div class="hidden group-hover:flex items-center gap-0.5 pr-1">
                <button
                  @click.stop="openEdit(topic)"
                  class="p-1 rounded hover:bg-[var(--bg-surface-hover)] text-[var(--text-tertiary)] hover:text-primary-500"
                  title="编辑"
                >
                  <Pencil :size="14" />
                </button>
                <button
                  @click.stop="goAchievement(topic.id)"
                  class="p-1 rounded hover:bg-[var(--bg-surface-hover)] text-[var(--text-tertiary)] hover:text-primary-500"
                  title="成果面板"
                >
                  <BarChart3 :size="14" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <!-- 底部：用户信息 + 主题切换 -->
      <div class="border-t border-[var(--border-color)] p-3 space-y-3">
        <!-- 用户信息 -->
        <div v-if="auth.user" class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-full bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center">
              <User :size="14" class="text-primary-600 dark:text-primary-300" />
            </div>
            <span class="text-xs font-medium text-[var(--text-primary)] truncate max-w-[120px]">{{ auth.user.username }}</span>
          </div>
          <button @click="handleLogout" class="p-1 rounded hover:bg-[var(--bg-surface-hover)] text-[var(--text-tertiary)] hover:text-red-500" title="退出登录">
            <LogOut :size="14" />
          </button>
        </div>

        <!-- 主题切换 -->
        <div class="flex bg-[var(--bg-surface-alt)] rounded-lg p-0.5">
          <button
            v-for="opt in themeOptions"
            :key="opt.mode"
            @click="theme.setMode(opt.mode)"
            :class="[
              'flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-md text-xs transition-colors',
              theme.mode === opt.mode
                ? 'bg-[var(--bg-surface)] text-[var(--text-primary)] shadow-sm font-medium'
                : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]',
            ]"
            :title="opt.label"
          >
            <component :is="opt.icon" :size="14" />
            {{ opt.label }}
          </button>
        </div>
      </div>
    </aside>

    <!-- ─── 主内容区 ─── -->
    <main class="flex-1 flex flex-col min-w-0">
      <!-- 顶部栏（移动端） -->
      <header class="lg:hidden flex items-center justify-between h-14 px-4 border-b border-[var(--border-color)] bg-[var(--bg-surface)] shrink-0">
        <button @click="mobileMenuOpen = true" class="p-1.5 rounded-md hover:bg-[var(--bg-surface-hover)]">
          <Menu :size="20" />
        </button>
        <span class="font-semibold text-sm">留痕 · 记录与复盘</span>
        <div class="w-8" />
      </header>

      <!-- 页面内容 -->
      <div class="flex-1 overflow-y-auto">
        <slot />
      </div>
    </main>

    <!-- 编辑主题对话框 -->
    <EditTopicDialog
      v-if="editingTopic"
      :topic="editingTopic"
      @close="editingTopic = null"
    />
  </div>
</template>
