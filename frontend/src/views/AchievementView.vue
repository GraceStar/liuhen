<script setup lang="ts">
/** 成果面板 - 多维统计 + AI 分析 */
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import { getAchievements, getAnnualSummary } from '@/api'
import { ArrowLeft, Loader2, FileText, TrendingUp } from '@lucide/vue'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  ArcElement, Title, Tooltip, Legend, PointElement, LineElement,
} from 'chart.js'
import AIAnalysisPanel from '@/components/AIAnalysisPanel.vue'
import type { AchievementSummary, AnnualSummary } from '@/types'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, PointElement, LineElement, Title, Tooltip, Legend)

const route = useRoute()
const router = useRouter()
const data = useDataStore()

const summary = ref<AchievementSummary | null>(null)
const selectedYear = ref(new Date().getFullYear())
const selectedMonth = ref<number | null>(null)
const minImportance = ref<number | null>(null)

// 年终总结
const annualLoading = ref(false)
const annualSummary = ref<AnnualSummary | null>(null)
const annualYear = ref(new Date().getFullYear())

const topicId = computed(() => Number(route.params.id))

async function loadData() {
  const id = topicId.value
  if (!id) return
  if (data.topics.length === 0) await data.loadTopics()
  if (data.activeTopicId !== id) await data.selectTopic(id)
  await loadAchievements()
}

async function loadAchievements() {
  if (!topicId.value) return
  summary.value = await getAchievements(topicId.value, {
    year: selectedYear.value,
    month: selectedMonth.value || undefined,
    min_importance: minImportance.value || undefined,
  })
}

async function generateAnnual() {
  if (!topicId.value || !data.activeTopic) return
  annualLoading.value = true
  try {
    annualSummary.value = await getAnnualSummary(topicId.value, annualYear.value)
  } finally {
    annualLoading.value = false
  }
}

// 每月完成柱状图
const barChartData = computed(() => {
  if (!summary.value) return null
  const months = Object.keys(summary.value.doneByMonth)
  const values = Object.values(summary.value.doneByMonth)
  return {
    labels: months,
    datasets: [{
      label: '完成数',
      data: values,
      backgroundColor: '#5b7c99',
      borderRadius: 6,
      borderSmooth: true,
    }],
  }
})

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true, ticks: { stepSize: 1 }, grid: { color: '#e5e8ed' } },
    x: { grid: { display: false } },
  },
}

// 重要程度分布
const doughnutData = computed(() => {
  if (!summary.value) return null
  const high = summary.value.highImportanceTasks.length
  const normal = summary.value.totalDone - high
  return {
    labels: ['高优先级(4-5★)', '普通(1-3★)'],
    datasets: [{
      data: [high, normal],
      backgroundColor: ['#5b7c99', '#bfd3e0'],
      borderColor: 'transparent',
    }],
  }
})

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' as const } },
}

watch(
  () => route.params.id,
  async () => { await loadData(); },
  { immediate: true },
)

// 监听筛选变化
watch([selectedYear, selectedMonth, minImportance], loadAchievements)
</script>

<template>
  <div v-if="data.loading" class="flex items-center justify-center h-64">
    <Loader2 :size="24" class="animate-spin text-primary-500" />
  </div>

  <div v-else-if="data.activeTopic" class="p-6 max-w-5xl mx-auto space-y-6">
    <!-- 返回 -->
    <button @click="router.push(`/topic/${topicId}`)"
      class="flex items-center gap-1.5 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
      <ArrowLeft :size="16" />
      返回看板
    </button>

    <!-- 标题 -->
    <div>
      <h1 class="text-xl font-bold text-[var(--text-primary)]">成果面板</h1>
      <p class="text-sm text-[var(--text-secondary)] mt-0.5">{{ data.activeTopic.name }} · 已完成任务统计与分析</p>
    </div>

    <!-- 筛选 -->
    <div class="flex flex-wrap gap-3">
      <select v-model="selectedYear" class="px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] text-[var(--text-primary)]">
        <option :value="null">所有年份</option>
        <option v-for="y in [2025, 2026, 2027]" :key="y" :value="y">{{ y }}</option>
      </select>
      <select v-model="selectedMonth" class="px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] text-[var(--text-primary)]">
        <option :value="null">所有月份</option>
        <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
      </select>
      <select v-model="minImportance" class="px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] text-[var(--text-primary)]">
        <option :value="null">所有重要程度</option>
        <option :value="4">★4 以上</option>
        <option :value="5">★5</option>
      </select>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card p-4 text-center">
        <p class="text-2xl font-bold text-[var(--text-primary)]">{{ summary?.totalDone || 0 }}</p>
        <p class="text-xs text-[var(--text-tertiary)] mt-1">总完成数</p>
      </div>
      <div class="card p-4 text-center">
        <p class="text-2xl font-bold text-[var(--text-primary)]">{{ summary?.avgImportance || 0 }}</p>
        <p class="text-xs text-[var(--text-tertiary)] mt-1">平均重要度</p>
      </div>
      <div class="card p-4 text-center">
        <p class="text-2xl font-bold text-[var(--text-primary)]">{{ summary?.highImportanceTasks?.length || 0 }}</p>
        <p class="text-xs text-[var(--text-tertiary)] mt-1">高优先级任务</p>
      </div>
      <div class="card p-4 text-center">
        <p class="text-2xl font-bold text-[var(--text-primary)]">{{ Object.keys(summary?.doneByMonth || {}).length }}</p>
        <p class="text-xs text-[var(--text-tertiary)] mt-1">覆盖月份</p>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="card p-5">
        <h4 class="text-sm font-semibold text-[var(--text-primary)] mb-3">每月完成趋势</h4>
        <div class="h-56">
          <Bar v-if="barChartData" :data="barChartData" :options="barChartOptions" />
          <div v-else class="flex items-center justify-center h-full text-sm text-[var(--text-tertiary)]">暂无数据</div>
        </div>
      </div>
      <div class="card p-5">
        <h4 class="text-sm font-semibold text-[var(--text-primary)] mb-3">重要程度分布</h4>
        <div class="h-56">
          <Doughnut v-if="doughnutData" :data="doughnutData" :options="doughnutOptions" />
          <div v-else class="flex items-center justify-center h-full text-sm text-[var(--text-tertiary)]">暂无数据</div>
        </div>
      </div>
    </div>

    <!-- 最近完成列表 -->
    <div v-if="summary?.recentDone?.length" class="card p-5">
      <h4 class="text-sm font-semibold text-[var(--text-primary)] mb-3">最近完成</h4>
      <div class="space-y-2">
        <div v-for="t in summary.recentDone" :key="t.id" class="flex items-center gap-3 text-sm">
          <span class="text-emerald-400">✓</span>
          <span class="text-[var(--text-primary)]">{{ t.title }}</span>
          <span class="text-xs text-[var(--text-tertiary)]">{{ t.completedAt?.slice(0, 10) }}</span>
        </div>
      </div>
    </div>

    <!-- AI 分析 -->
    <AIAnalysisPanel :topic-id="topicId" :topic-name="data.activeTopic.name" />

    <!-- 年终总结（仅工作分类显示） -->
    <div v-if="data.activeTopic.categoryType === 'work'" class="card p-5">
      <div class="flex items-center gap-2.5 mb-4">
        <div class="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center">
          <FileText :size="18" class="text-blue-500" />
        </div>
        <div>
          <h3 class="font-semibold text-[var(--text-primary)]">年度工作总结</h3>
          <p class="text-xs text-[var(--text-tertiary)]">生成适合放入 PPT 的大纲与图文</p>
        </div>
      </div>

      <div class="flex gap-3 mb-4">
        <select v-model="annualYear" class="px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] text-[var(--text-primary)]">
          <option v-for="y in [2025, 2026, 2027]" :key="y" :value="y">{{ y }}年</option>
        </select>
        <button @click="generateAnnual" :disabled="annualLoading"
          class="btn-magnetic flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-40">
          <Loader2 v-if="annualLoading" :size="14" class="animate-spin" />
          <TrendingUp v-else :size="14" />
          生成总结
        </button>
      </div>

      <!-- 总结内容 -->
      <div v-if="annualSummary" class="prose prose-sm max-w-none text-[var(--text-primary)] bg-[var(--bg-surface-alt)] rounded-lg p-4 whitespace-pre-wrap">
        {{ annualSummary.outline }}
      </div>
      <div v-else class="py-8 text-center text-sm text-[var(--text-tertiary)]">
        选择年份并点击「生成总结」，AI 将输出 PPT 友好的内容
      </div>
    </div>
  </div>
</template>
