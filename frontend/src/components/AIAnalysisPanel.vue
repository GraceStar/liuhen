<script setup lang="ts">
/** AI 分析面板 */
import { ref } from 'vue'
import { Brain, Loader2, RefreshCw } from '@lucide/vue'
import { analyzeTopic } from '@/api'
import type { AIAnalysisResult } from '@/types'

const props = defineProps<{ topicId: number; topicName: string }>()

const loading = ref(false)
const result = ref<AIAnalysisResult | null>(null)
const promptExtra = ref('')
const error = ref('')

async function runAnalysis() {
  loading.value = true
  error.value = ''
  try {
    result.value = await analyzeTopic(props.topicId, promptExtra.value)
  } catch (e: any) {
    error.value = e?.message || '分析失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card p-6">
    <div class="flex items-center gap-2.5 mb-4">
      <div class="w-8 h-8 rounded-lg bg-purple-50 dark:bg-purple-900/30 flex items-center justify-center">
        <Brain :size="18" class="text-purple-500" />
      </div>
      <div>
        <h3 class="font-semibold text-[var(--text-primary)]">AI 复盘分析</h3>
        <p class="text-xs text-[var(--text-tertiary)]">{{ topicName }} · 基于已完成任务</p>
      </div>
    </div>

    <!-- 提示词输入 -->
    <div class="flex gap-2 mb-4">
      <input
        v-model="promptExtra"
        type="text"
        placeholder="额外提示（选填）：如「重点关注时间管理」"
        class="flex-1 px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface-alt)] focus:outline-none focus:ring-2 focus:ring-purple-500/30 text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)]"
        @keyup.enter="runAnalysis"
      />
      <button
        @click="runAnalysis"
        :disabled="loading"
        class="btn-magnetic flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-40"
      >
        <Loader2 v-if="loading" :size="14" class="animate-spin" />
        <RefreshCw v-else :size="14" />
        {{ loading ? '分析中...' : '开始分析' }}
      </button>
    </div>

    <!-- 错误 -->
    <div v-if="error" class="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
      {{ error }}
    </div>

    <!-- 结果 -->
    <div v-if="result" class="space-y-4">
      <div class="prose prose-sm max-w-none text-[var(--text-primary)]" v-html="result.analysis.replace(/\n/g, '<br>')" />
      <div class="border-t border-[var(--border-light)] pt-4">
        <h4 class="text-sm font-semibold text-[var(--text-primary)] mb-2">改进建议</h4>
        <div class="prose prose-sm max-w-none text-[var(--text-secondary)]" v-html="result.suggestions.replace(/\n/g, '<br>')" />
      </div>
      <p class="text-xs text-[var(--text-tertiary)]">生成时间：{{ result.generatedAt.slice(0, 16).replace('T', ' ') }}</p>
    </div>

    <!-- 空状态 -->
    <div v-if="!result && !loading" class="py-8 text-center text-sm text-[var(--text-tertiary)]">
      <p>点击「开始分析」，AI 将根据已完成任务给出复盘建议</p>
      <p class="text-xs mt-1">需要先完成一些任务才能获得有意义的分析</p>
    </div>
  </div>
</template>
