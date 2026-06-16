<script setup lang="ts">
/** 快速添加任务表单 */
import { ref } from 'vue'
import { Plus, Loader2 } from '@lucide/vue'
import StarRating from './StarRating.vue'
import type { TaskStatus } from '@/types'

const emit = defineEmits<{
  add: [data: { title: string; status: TaskStatus; importance: number }]
}>()

const title = ref('')
const importance = ref(3)
const saving = ref(false)

async function submit() {
  const t = title.value.trim()
  if (!t) return
  saving.value = true
  try {
    emit('add', { title: t, status: 'todo', importance: importance.value })
    title.value = ''
    importance.value = 3
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="card p-3">
    <form @submit.prevent="submit" class="flex items-center gap-3">
      <input
        v-model="title"
        type="text"
        placeholder="添加新待办..."
        class="flex-1 px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface-alt)] focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)]"
        :disabled="saving"
      />
      <StarRating v-model="importance" />
      <button
        type="submit"
        :disabled="!title.trim() || saving"
        class="btn-magnetic shrink-0 flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <Loader2 v-if="saving" :size="14" class="animate-spin" />
        <Plus v-else :size="14" />
        添加
      </button>
    </form>
  </div>
</template>
