/**
 * 核心类型定义 — 整个前端共享的数据结构
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * TypeScript 的 interface 类似 Kotlin 的 data class，
 * 用于定义对象的"形状"（有哪些字段、什么类型）。
 * 好处是编译时就能发现拼写错误和类型不匹配。
 */

export type CategoryType = 'work' | 'study' | 'observe'

export interface Category {
  id: number
  name: string
  type: CategoryType
  icon: string
  sortOrder: number
  createdAt: string
}

export interface Topic {
  id: number
  name: string
  description: string
  categoryId: number
  categoryType: CategoryType
  isDefault: boolean
  color: string
  createdAt: string
  updatedAt: string
}

/** 任务的三态 — 看板的核心流转 */
export type TaskStatus = 'todo' | 'doing' | 'done'

export interface Task {
  id: number
  title: string
  description: string
  status: TaskStatus
  importance: number  // 1 ~ 5 星
  topicId: number
  completedAt: string | null
  createdAt: string
  updatedAt: string
}

/** 成果统计数据（对应后端 /tasks/achievements 接口） */
export interface AchievementSummary {
  totalDone: number
  avgImportance: number
  doneByMonth: Record<string, number>
  highImportanceTasks: Task[]
  recentDone: Task[]
}

/** AI 复盘分析结果 */
export interface AIAnalysisResult {
  topicName: string
  analysis: string
  suggestions: string
  generatedAt: string
}

/** 年终工作总结（PPT 友好格式） */
export interface AnnualSummary {
  title: string
  outline: string        // Markdown 大纲
  keyNumbers: string      // 关键数据
  chartSuggestions: string // 图表建议
  pptContent: string      // PPT 可用图文
}

/** 主题色模式 */
export type ThemeMode = 'light' | 'dark' | 'system'

// ──────────────────────────────────────────────
// 认证相关类型（新增）
// ──────────────────────────────────────────────

/** 登录用户信息（从后端 /auth/me 接口返回） */
export interface User {
  id: number
  username: string
  createdAt: string | null
}

/** 登录/注册返回结果 */
export interface AuthResult {
  token: string    // JWT 令牌，后续所有 API 调用都要带上
  user: User       // 用户基本信息
}
