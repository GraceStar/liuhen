/** API 层 - 所有后端接口封装 */
import axios from 'axios'
import type {
  Category, Topic, Task, TaskStatus,
  AchievementSummary, AIAnalysisResult, AnnualSummary,
} from './types'

const http = axios.create({ baseURL: '/api' })

// ─── 分类 ───
export const getCategories = () =>
  http.get<Category[]>('/categories').then(r => r.data)

// ─── 主题 ───
export const getTopics = (categoryId?: number) =>
  http.get<Topic[]>('/topics', { params: categoryId ? { category_id: categoryId } : {} }).then(r => r.data)

export const createTopic = (data: { name: string; description?: string; categoryId: number; color?: string }) =>
  http.post<Topic>('/topics', data).then(r => r.data)

export const updateTopic = (id: number, data: { name?: string; description?: string; color?: string }) =>
  http.put<Topic>(`/topics/${id}`, data).then(r => r.data)

export const deleteTopic = (id: number) =>
  http.delete<{ ok: boolean }>(`/topics/${id}`).then(r => r.data)

// ─── 任务 ───
export const getTasks = (params?: { topic_id?: number; status?: TaskStatus; importance?: number }) =>
  http.get<Task[]>('/tasks', { params }).then(r => r.data)

export const createTask = (data: { title: string; description?: string; status: TaskStatus; importance: number; topicId: number }) =>
  http.post<Task>('/tasks', data).then(r => r.data)

export const updateTask = (id: number, data: { title?: string; description?: string; status?: TaskStatus; importance?: number }) =>
  http.put<Task>(`/tasks/${id}`, data).then(r => r.data)

export const deleteTask = (id: number) =>
  http.delete<{ ok: boolean }>(`/tasks/${id}`).then(r => r.data)

// ─── 成果统计 ───
export const getAchievements = (topicId: number, params?: { year?: number; month?: number; min_importance?: number }) =>
  http.get<AchievementSummary>(`/tasks/achievements/${topicId}`, { params }).then(r => r.data)

// ─── AI ───
export const analyzeTopic = (topicId: number, promptExtra?: string) =>
  http.post<AIAnalysisResult>('/ai/analyze', { topicId, promptExtra }).then(r => r.data)

export const getAnnualSummary = (topicId: number, year: number) =>
  http.post<AnnualSummary>('/ai/annual-summary', { topicId, year }).then(r => r.data)
