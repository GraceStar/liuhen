/**
 * API 层 — 所有后端接口的封装
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * axios 是前端最常用的 HTTP 请求库，类似 Android 的 OkHttp + Retrofit。
 * 这里把所有接口函数集中写在一个文件里，方便维护。
 *
 * 每个函数格式：export const xxx = (params) => http.get/post/put/delete(url, data)
 * 返回值统一通过 .then(r => r.data) 解包（axios 默认把响应体包在 r.data 里）。
 *
 * 认证说明：
 *   http 实例在 auth store 初始化时会设置 Authorization 请求头
 *   格式："Bearer xxxxyyyyzzzz"（JWT 令牌）
 *   后端通过 get_current_user 函数解析这个头来识别用户。
 */
import axios from 'axios'
import type {
  Category, Topic, Task, TaskStatus,
  AchievementSummary, AIAnalysisResult, AnnualSummary,
  AuthResult, User,
} from './types'

/** 创建 axios 实例 — 所有请求共享同一个 baseURL 和拦截器 */
const http = axios.create({ baseURL: '/api' })

// 导出 http 实例供 auth store 设置 token
export default http

// ──────────────────────────────────────────────
// 认证接口
// ──────────────────────────────────────────────
/** 注册新用户 */
export const register = (username: string, password: string) =>
  http.post<AuthResult>('/auth/register', { username, password }).then(r => r.data)

/** 登录 */
export const login = (username: string, password: string) =>
  http.post<AuthResult>('/auth/login', { username, password }).then(r => r.data)

/** 获取当前登录用户信息（验证 token） */
export const getMe = () =>
  http.get<User>('/auth/me').then(r => r.data)

// ──────────────────────────────────────────────
// 分类（无需登录）
// ──────────────────────────────────────────────
export const getCategories = () =>
  http.get<Category[]>('/categories').then(r => r.data)

// ──────────────────────────────────────────────
// 主题（需要登录）
// ──────────────────────────────────────────────
export const getTopics = (categoryId?: number) =>
  http.get<Topic[]>('/topics', {
    params: categoryId ? { category_id: categoryId } : {}
  }).then(r => r.data)

export const createTopic = (data: {
  name: string; description?: string; categoryId: number; color?: string
}) => http.post<Topic>('/topics', data).then(r => r.data)

export const updateTopic = (id: number, data: {
  name?: string; description?: string; color?: string
}) => http.put<Topic>(`/topics/${id}`, data).then(r => r.data)

export const deleteTopic = (id: number) =>
  http.delete<{ ok: boolean }>(`/topics/${id}`).then(r => r.data)

// ──────────────────────────────────────────────
// 任务（需要登录）
// ──────────────────────────────────────────────
export const getTasks = (params?: {
  topic_id?: number; status?: TaskStatus; importance?: number
}) => http.get<Task[]>('/tasks', { params }).then(r => r.data)

export const createTask = (data: {
  title: string; description?: string; status: TaskStatus;
  importance: number; topicId: number
}) => http.post<Task>('/tasks', data).then(r => r.data)

export const updateTask = (id: number, data: {
  title?: string; description?: string; status?: TaskStatus; importance?: number
}) => http.put<Task>(`/tasks/${id}`, data).then(r => r.data)

export const deleteTask = (id: number) =>
  http.delete<{ ok: boolean }>(`/tasks/${id}`).then(r => r.data)

// ──────────────────────────────────────────────
// 成果统计（需要登录）
// ──────────────────────────────────────────────
export const getAchievements = (topicId: number, params?: {
  year?: number; month?: number; min_importance?: number
}) => http.get<AchievementSummary>(`/tasks/achievements/${topicId}`, { params }).then(r => r.data)

// ──────────────────────────────────────────────
// AI 分析（需要登录）
// ──────────────────────────────────────────────
export const analyzeTopic = (topicId: number, promptExtra?: string) =>
  http.post<AIAnalysisResult>('/ai/analyze', { topicId, promptExtra }).then(r => r.data)

export const getAnnualSummary = (topicId: number, year: number) =>
  http.post<AnnualSummary>('/ai/annual-summary', { topicId, year }).then(r => r.data)
