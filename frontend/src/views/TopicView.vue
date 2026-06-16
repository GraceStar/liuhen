<script setup lang="ts">
/** 主题任务看板 - Todo / Doing / Done 三栏 */
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDataStore } from '@/stores/data'
import { BarChart3, Loader2 } from '@lucide/vue'
import AddTaskForm from '@/components/AddTaskForm.vue'
import TaskCard from '@/components/TaskCard.vue'
import type { TaskStatus } from '@/types'

const route = useRoute()
const router = useRouter()
const data = useDataStore()

// 用 watch immediate 替代 onMounted + watch 双触发
watch(
  () => route.params.id,
  async (newId) => {
    if (!newId) return
    const id = Number(newId)
    if (data.topics.length === 0) await data.loadTopics()
    if (data.activeTopicId !== id) await data.selectTopic(id)
  },
  { immediate: true },
)

async function handleAdd(payload: { title: string; status: TaskStatus; importance: number }) {
  await data.addTask(payload.title, payload.status, payload.importance)
}

async function handleUpdate(id: number, updates: { title?: string; status?: TaskStatus; importance?: number }) {
  await data.editTask(id, updates)
}

async function handleDelete(id: number) {
  await data.removeTask(id)
}

const columns = computed(() => [
  {
    key: 'todo' as TaskStatus,
    label: '待办',
    count: data.todoTasks.length,
    tasks: data.todoTasks,
    colorClass: 'status-todo',
    borderClass: 'border-t-slate-300 dark:border-t-slate-600',
  },
  {
    key: 'doing' as TaskStatus,
    label: '进行中',
    count: data.doingTasks.length,
    tasks: data.doingTasks,
    colorClass: 'status-doing',
    borderClass: 'border-t-amber-400',
  },
  {
    key: 'done' as TaskStatus,
    label: '已完成',
    count: data.doneTasks.length,
    tasks: data.doneTasks,
    colorClass: 'status-done',
    borderClass: 'border-t-emerald-400',
  },
])
</script>

<template>
  <div v-if="data.loading" class="flex items-center justify-center h-64">
    <Loader2 :size="24" class="animate-spin text-primary-500" />
  </div>

  <div v-else-if="data.activeTopic" class="p-6 space-y-4">
    <!-- 头部 -->
    <div class="flex items-center justify-between">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-xl font-bold text-[var(--text-primary)]">{{ data.activeTopic.name }}</h1>
          <span class="px-2 py-0.5 text-xs rounded-full" :class="[
            data.activeTopic.categoryType === 'work' ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' :
            data.activeTopic.categoryType === 'study' ? 'bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400' :
            'bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
          ]">
            {{ data.activeTopic.categoryType === 'work' ? '💼 工作' :
               data.activeTopic.categoryType === 'study' ? '📚 学习' : '🔍 观察' }}
          </span>
        </div>
        <p v-if="data.activeTopic.description" class="text-sm text-[var(--text-secondary)] mt-1">
          {{ data.activeTopic.description }}
        </p>
      </div>

      <button
        @click="router.push(`/achievement/${data.activeTopicId}`)"
        class="btn-magnetic flex items-center gap-1.5 px-3 py-2 text-sm rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-hover)] text-[var(--text-secondary)]"
      >
        <BarChart3 :size="16" />
        成果面板
      </button>
    </div>

    <!-- 快速添加 -->
    <AddTaskForm @add="handleAdd" />

    <!-- 三栏看板 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
        v-for="col in columns"
        :key="col.key"
        :class="['card border-t-2 overflow-hidden', col.borderClass]"
      >
        <!-- 栏头 -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-[var(--border-light)]">
          <div class="flex items-center gap-2">
            <span :class="['px-2 py-0.5 text-xs font-medium rounded-full', col.colorClass]">
              {{ col.label }}
            </span>
            <span class="text-xs text-[var(--text-tertiary)]">{{ col.count }}</span>
          </div>
        </div>

        <!-- 任务列表 -->
        <div class="p-3 space-y-2 min-h-[120px]">
          <TaskCard
            v-for="task in col.tasks"
            :key="task.id"
            :task="task"
            @update="handleUpdate"
            @delete="handleDelete"
          />

          <div
            v-if="col.tasks.length === 0"
            class="py-8 text-center text-xs text-[var(--text-tertiary)]"
          >
            {{ col.key === 'todo' ? '还没有待办事项' : col.key === 'doing' ? '没有进行中的任务' : '还没有完成的任务' }}
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 未选择主题 -->
  <div v-else class="flex items-center justify-center h-64">
    <div class="text-center">
      <p class="text-[var(--text-tertiary)] text-sm">从左侧选择或创建一个主题开始记录</p>
    </div>
  </div>
</template>
