<script setup lang="ts">
/** 总览面板 - 首页 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import { Plus, Circle, Clock, CheckCircle2, Sparkles, Loader2 } from '@lucide/vue'
import AddTopicDialog from '@/components/AddTopicDialog.vue'

const router = useRouter()
const data = useDataStore()
const showAddTopic = ref(false)
const ready = ref(false)

onMounted(async () => {
  if (data.categories.length === 0) await data.loadCategories()
  if (data.topics.length === 0) await data.loadTopics()
  ready.value = true
})

// 按分类聚合（仅分组，不加载所有任务）
const categoryStats = computed(() => {
  return data.categories.map(cat => {
    const catTopics = data.topics.filter(t => t.categoryId === cat.id)
    return {
      ...cat,
      topicCount: catTopics.length,
      topics: catTopics,
    }
  })
})

function goTopic(topicId: number) {
  data.selectTopic(topicId)
  router.push(`/topic/${topicId}`)
}
</script>

<template>
  <div v-if="!ready" class="flex items-center justify-center h-64">
    <Loader2 :size="24" class="animate-spin text-primary-500" />
  </div>

  <div v-else class="p-6 max-w-5xl mx-auto space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-[var(--text-primary)]">总览面板</h1>
        <p class="text-sm text-[var(--text-secondary)] mt-0.5">结构化记录工作、学习与生活观察</p>
      </div>
      <button
        @click="showAddTopic = true"
        class="btn-magnetic flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-primary-500 text-white rounded-lg hover:bg-primary-600"
      >
        <Plus :size="16" /> 新建主题
      </button>
    </div>

    <!-- 分类卡片网格 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
        v-for="stat in categoryStats"
        :key="stat.id"
        class="card p-5 space-y-4 hover:border-primary-200 dark:hover:border-primary-800 transition-colors"
      >
        <!-- 分类头部 -->
        <div class="flex items-center gap-2.5">
          <span class="text-2xl">{{ stat.icon }}</span>
          <div>
            <h3 class="font-semibold text-[var(--text-primary)]">{{ stat.name }}</h3>
            <p class="text-xs text-[var(--text-tertiary)]">{{ stat.topicCount }} 个主题</p>
          </div>
        </div>

        <!-- 主题列表 -->
        <div v-if="stat.topics.length > 0" class="space-y-1.5">
          <p class="text-xs font-medium text-[var(--text-tertiary)] uppercase">主题</p>
          <button
            v-for="topic in stat.topics"
            :key="topic.id"
            @click="goTopic(topic.id)"
            class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm hover:bg-[var(--bg-surface-hover)] transition-colors group"
          >
            <span class="text-[var(--text-primary)]">{{ topic.name }}</span>
            <span class="text-xs text-[var(--text-tertiary)] opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
              <Sparkles :size="12" /> 进入
            </span>
          </button>
        </div>
        <div v-else class="py-4 text-center text-xs text-[var(--text-tertiary)]">
          暂无主题，点击上方「新建主题」
        </div>
      </div>
    </div>
  </div>

  <!-- 新建主题对话框 -->
  <AddTopicDialog v-if="showAddTopic" @close="showAddTopic = false" />
</template>
