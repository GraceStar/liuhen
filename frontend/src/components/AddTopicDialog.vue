<script setup lang="ts">
/** 添加主题对话框 */
import { ref, computed } from 'vue'
import { X, Plus } from '@lucide/vue'
import { useDataStore } from '@/stores/data'

const emit = defineEmits<{ close: [] }>()
const data = useDataStore()

const name = ref('')
const description = ref('')
const categoryId = ref<number>(data.categories[0]?.id || 0)
const saving = ref(false)

const isValid = computed(() => name.value.trim().length > 0 && categoryId.value > 0)

async function submit() {
  if (!isValid.value) return
  saving.value = true
  try {
    const topic = await data.createNewTopic(name.value.trim(), description.value.trim(), categoryId.value)
    emit('close')
    if (topic) data.selectTopic(topic.id)
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
        <h3 class="text-lg font-semibold text-[var(--text-primary)]">新建主题</h3>
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
            placeholder="如：英语学习"
            class="w-full px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface-alt)] focus:outline-none focus:ring-2 focus:ring-primary-500/30 text-[var(--text-primary)]"
            @keyup.enter="submit"
            autofocus
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-[var(--text-secondary)] mb-1">所属分类</label>
          <div class="flex gap-2">
            <button
              v-for="cat in data.categories"
              :key="cat.id"
              @click="categoryId = cat.id"
              :class="[
                'flex-1 py-2 rounded-lg text-sm font-medium transition-colors',
                categoryId === cat.id
                  ? 'bg-primary-500 text-white'
                  : 'bg-[var(--bg-surface-alt)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)]',
              ]"
            >
              {{ cat.icon }} {{ cat.name }}
            </button>
          </div>
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

      <button
        @click="submit"
        :disabled="!isValid || saving"
        class="btn-magnetic w-full flex items-center justify-center gap-2 py-2.5 text-sm font-medium bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        <Plus :size="16" />
        {{ saving ? '创建中...' : '创建主题' }}
      </button>
    </div>
  </div>
</template>
