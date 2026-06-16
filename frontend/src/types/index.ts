/** 核心类型定义 */

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

export type TaskStatus = 'todo' | 'doing' | 'done'

export interface Task {
  id: number
  title: string
  description: string
  status: TaskStatus
  importance: number // 1-5
  topicId: number
  completedAt: string | null
  createdAt: string
  updatedAt: string
}

export interface AchievementSummary {
  totalDone: number
  avgImportance: number
  doneByMonth: Record<string, number>
  highImportanceTasks: Task[]
  recentDone: Task[]
}

export interface AIAnalysisResult {
  topicName: string
  analysis: string
  suggestions: string
  generatedAt: string
}

export interface AnnualSummary {
  title: string
  outline: string
  keyNumbers: string
  chartSuggestions: string
  pptContent: string
}

/** 主题色 */
export type ThemeMode = 'light' | 'dark' | 'system'
