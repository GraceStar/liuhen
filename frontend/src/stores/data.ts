/** 数据 Store - 分类/主题/任务管理 */
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Category, Topic, Task, TaskStatus } from '@/types'
import * as api from '@/api'

export const useDataStore = defineStore('data', () => {
  // ─── State ───
  const categories = ref<Category[]>([])
  const topics = ref<Topic[]>([])
  const tasks = ref<Task[]>([])
  const activeCategoryId = ref<number | null>(null)
  const activeTopicId = ref<number | null>(null)
  const loading = ref(false)

  // ─── Getters ───
  const activeCategory = computed(() =>
    categories.value.find(c => c.id === activeCategoryId.value) || null
  )

  const activeTopic = computed(() =>
    topics.value.find(t => t.id === activeTopicId.value) || null
  )

  const filteredTopics = computed(() => {
    if (!activeCategoryId.value) return topics.value
    return topics.value.filter(t => t.categoryId === activeCategoryId.value)
  })

  const todoTasks = computed(() =>
    tasks.value.filter(t => t.status === 'todo')
  )

  const doingTasks = computed(() =>
    tasks.value.filter(t => t.status === 'doing')
  )

  const doneTasks = computed(() =>
    tasks.value.filter(t => t.status === 'done')
  )

  // ─── Actions ───
  async function loadCategories() {
    categories.value = await api.getCategories()
  }

  async function loadTopics(categoryId?: number) {
    topics.value = await api.getTopics(categoryId)
  }

  async function loadTasks(topicId: number) {
    loading.value = true
    try {
      tasks.value = await api.getTasks({ topic_id: topicId })
    } finally {
      loading.value = false
    }
  }

  async function selectTopic(topicId: number) {
    activeTopicId.value = topicId
    if (topicId) {
      const t = topics.value.find(tp => tp.id === topicId)
      if (t) activeCategoryId.value = t.categoryId
      await loadTasks(topicId)
    } else {
      tasks.value = []
    }
  }

  async function addTask(title: string, status: TaskStatus, importance: number) {
    if (!activeTopicId.value) return
    const task = await api.createTask({
      title,
      status,
      importance,
      topicId: activeTopicId.value,
    })
    tasks.value.unshift(task)
    return task
  }

  async function editTask(id: number, data: { title?: string; status?: TaskStatus; importance?: number }) {
    const task = await api.updateTask(id, data)
    const idx = tasks.value.findIndex(t => t.id === id)
    if (idx >= 0) tasks.value[idx] = task
    return task
  }

  async function removeTask(id: number) {
    await api.deleteTask(id)
    tasks.value = tasks.value.filter(t => t.id !== id)
  }

  async function createNewTopic(name: string, description: string, categoryId: number) {
    const topic = await api.createTopic({ name, description, categoryId })
    topics.value.push(topic)
    return topic
  }

  async function removeTopic(id: number) {
    await api.deleteTopic(id)
    topics.value = topics.value.filter(t => t.id !== id)
    if (activeTopicId.value === id) {
      activeTopicId.value = null
      tasks.value = []
    }
  }

  async function updateTopic(id: number, data: { name?: string; description?: string; color?: string }) {
    const updated = await api.updateTopic(id, data)
    const idx = topics.value.findIndex(t => t.id === id)
    if (idx >= 0) topics.value[idx] = updated
    return updated
  }

  function setCategory(categoryId: number | null) {
    activeCategoryId.value = categoryId
    activeTopicId.value = null
    tasks.value = []
  }

  return {
    // state
    categories, topics, tasks, activeCategoryId, activeTopicId, loading,
    // getters
    activeCategory, activeTopic, filteredTopics,
    todoTasks, doingTasks, doneTasks,
    // actions
    loadCategories, loadTopics, loadTasks, selectTopic,
    addTask, editTask, removeTask, createNewTopic, removeTopic, updateTopic, setCategory,
  }
})
