<script setup lang="ts">
/** 编辑主题对话框：重命名 + 修改描述 + 删除 */
import { ref, computed } from 'vue'
import { X, Save, Trash2, Loader2 } from '@lucide/vue'
import { useDataStore } from '@/stores/data'
import type { Topic } from '@/types'

const props = defineProps<{ topic: Topic }>()
const emit = defineEmits<{ close: [] }>()

const data = useDataStore()

const name = ref(props.topic.name)
const description = ref(props.topic.description)
const saving = ref(false)
const showDeleteConfirm = ref(false)

const hasChanges = computed(() =>
  name.value.trim() !== props.topic.name ||
  description.value.trim() !== props.topic.description
)

async function save() {
  if (!name.value.trim()) return
  saving.value = true
  try {
    await data.updateTopic(props.topic.id, {
      name: name.value.trim(),
      description: description.value.trim(),
    })
    emit('close')
  } finally {
    saving.value = false
  }
}

async function remove() {
  saving.value = true
  try {
    await data.removeTopic(props.topic.id)
    emit('close')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/30" @click="emit('close')" />
    <div class="card relative w-full max-w-md p-6 space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-[var(--text-primary)]">编辑主题</h3>
        <button @click="emit('close')" class="p-1 rounded hover:bg-[var(--bg-surface-hover)] text-[var(--text-tertiary)]">
          <X :size="18" />
        </button>
      </div>

      <div class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-[var(--text-secondary)] mb-1">主题名称</label>
          <input
            v-model="name"
            type="text"
            class="w-full px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface-alt)] focus:outline-none focus:ring-2 focus:ring-primary-500/30 text-[var(--text-primary)]"
            @keyup.enter="save"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-[var(--text-secondary)] mb-1">描述（选填）</label>
          <input
            v-model="description"
            type="text"
            placeholder="简短描述这个主题的用途"
            class="w-full px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface-alt)] focus:outline-none focus:ring-2 focus:ring-primary-500/30 text-[var(--text-primary)]"
          />
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex gap-2">
        <button
          @click="save"
          :disabled="!hasChanges || !name.trim() || saving"
          class="btn-magnetic flex-1 flex items-center justify-center gap-1.5 py-2 text-sm font-medium bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Loader2 v-if="saving" :size="14" class="animate-spin" />
          <Save v-else :size="14" />
          {{ saving ? '保存中...' : '保存' }}
        </button>

        <button
          v-if="!topic.isDefault && !showDeleteConfirm"
          @click="showDeleteConfirm = true"
          class="btn-magnetic px-3 py-2 text-sm font-medium border border-red-200 dark:border-red-800 text-red-500 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20"
        >
          <Trash2 :size="14" />
        </button>
      </div>

      <!-- 删除确认 -->
      <div v-if="showDeleteConfirm" class="border border-red-200 dark:border-red-800 rounded-lg bg-red-50 dark:bg-red-900/20 p-3 space-y-2">
        <p class="text-sm text-red-600 dark:text-red-400">
          确定删除「{{ topic.name }}」及其所有任务？此操作不可撤销。
        </p>
        <div class="flex gap-2">
          <button
            @click="showDeleteConfirm = false"
            class="flex-1 py-1.5 text-xs font-medium rounded border border-[var(--border-color)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)]"
          >
            取消
          </button>
          <button
            @click="remove"
            :disabled="saving"
            class="flex-1 py-1.5 text-xs font-medium rounded bg-red-500 text-white hover:bg-red-600 disabled:opacity-40"
          >
            {{ saving ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
