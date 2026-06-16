<script setup lang="ts">
/** 任务卡片 - 支持 inline 编辑和状态流转 */
import { ref, computed } from 'vue'
import { Trash2, Edit3, ArrowRight, ArrowLeft, Check } from '@lucide/vue'
import StarRating from './StarRating.vue'
import type { Task, TaskStatus } from '@/types'

const props = defineProps<{ task: Task }>()
const emit = defineEmits<{
  update: [id: number, data: { title?: string; status?: TaskStatus; importance?: number }]
  delete: [id: number]
}>()

const editing = ref(false)
const editTitle = ref('')
const editImportance = ref(3)

const statusConfig: Record<TaskStatus, { label: string; next: TaskStatus | null; prev: TaskStatus | null }> = {
  todo: { label: '待办', next: 'doing', prev: null },
  doing: { label: '进行中', next: 'done', prev: 'todo' },
  done: { label: '已完成', next: null, prev: 'doing' },
}

const config = computed(() => statusConfig[props.task.status])

function startEdit() {
  editTitle.value = props.task.title
  editImportance.value = props.task.importance
  editing.value = true
}

function saveEdit() {
  if (editTitle.value.trim()) {
    emit('update', props.task.id, {
      title: editTitle.value.trim(),
      importance: editImportance.value,
    })
  }
  editing.value = false
}

function moveTo(status: TaskStatus) {
  emit('update', props.task.id, { status })
}
</script>

<template>
  <div
    :class="[
      'card p-3.5 group transition-all duration-200',
      task.status === 'done' ? 'opacity-70' : '',
    ]"
  >
    <!-- 编辑模式 -->
    <div v-if="editing" class="space-y-2">
      <input
        v-model="editTitle"
        class="w-full px-3 py-1.5 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] focus:outline-none focus:ring-2 focus:ring-primary-500/30 text-[var(--text-primary)]"
        @keyup.enter="saveEdit"
        @keyup.escape="editing = false"
        autofocus
      />
      <div class="flex items-center justify-between">
        <StarRating v-model="editImportance" />
        <button @click="saveEdit" class="btn-magnetic px-3 py-1 text-xs font-medium bg-primary-500 text-white rounded-lg hover:bg-primary-600">
          保存
        </button>
      </div>
    </div>

    <!-- 展示模式 -->
    <template v-else>
      <div class="flex items-start gap-3">
        <!-- 状态指示 -->
        <div
          :class="[
            'shrink-0 w-2.5 h-2.5 mt-1.5 rounded-full',
            task.status === 'todo' ? 'bg-slate-300 dark:bg-slate-600' :
            task.status === 'doing' ? 'bg-amber-400' : 'bg-emerald-400',
          ]"
          :title="config.label"
        />

        <div class="flex-1 min-w-0">
          <!-- 标题 -->
          <p
            :class="[
              'text-sm leading-relaxed',
              task.status === 'done' ? 'line-through text-[var(--text-tertiary)]' : 'text-[var(--text-primary)]',
            ]"
          >
            {{ task.title }}
          </p>

          <!-- 底部：重要程度 + 时间 -->
          <div class="flex items-center gap-3 mt-2">
            <StarRating :model-value="task.importance" readonly />
            <span class="text-xs text-[var(--text-tertiary)]">
              {{ task.completedAt ? task.completedAt.slice(0, 10) : task.createdAt.slice(0, 10) }}
            </span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="hidden group-hover:flex items-center gap-1 shrink-0">
          <!-- 状态流转 -->
          <button
            v-if="config.prev"
            @click="moveTo(config.prev)"
            class="p-1 rounded hover:bg-[var(--bg-surface-hover)] text-[var(--text-tertiary)] hover:text-primary-500"
            title="回退"
          >
            <ArrowLeft :size="14" />
          </button>
          <button
            v-if="config.next"
            @click="moveTo(config.next)"
            class="p-1 rounded hover:bg-[var(--bg-surface-hover)] text-[var(--text-tertiary)] hover:text-emerald-500"
            title="推进"
          >
            <ArrowRight :size="14" />
          </button>

          <!-- 编辑 -->
          <button @click="startEdit" class="p-1 rounded hover:bg-[var(--bg-surface-hover)] text-[var(--text-tertiary)] hover:text-primary-500">
            <Edit3 :size="14" />
          </button>

          <!-- 删除 -->
          <button @click="emit('delete', task.id)" class="p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-[var(--text-tertiary)] hover:text-red-500">
            <Trash2 :size="14" />
          </button>
        </div>
      </div>
    </template>
  </div>
</template>
