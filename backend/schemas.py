"""Pydantic 数据校验 - 类似 Kotlin 的 data class + 类型安全请求体
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pydantic 做三件事：
  1. 定义请求/响应的数据结构（类型提示）
  2. 自动校验输入（长度、格式、类型）
  3. 自动生成 API 文档（FastAPI 内置 /docs）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ──────────────────────────────────────────────
# 认证相关
# ──────────────────────────────────────────────
class RegisterRequest(BaseModel):
    """注册/登录请求 — 共享同一个 Schema"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, max_length=100, description="密码（无复杂度要求）")


class UserOut(BaseModel):
    """用户信息（不含密码） — API 响应中返回"""
    id: int
    username: str
    createdAt: Optional[str] = None


class LoginResponse(BaseModel):
    """登录/注册成功后的返回内容"""
    token: str            # JWT 令牌，后续请求放在 Authorization 头
    user: UserOut         # 用户基本信息


# ──────────────────────────────────────────────
# Category
# ──────────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    type: str = Field(..., pattern="^(work|study|observe)$")
    icon: str = Field(default="📋")
    sort_order: int = Field(default=0, ge=0)


class CategoryOut(BaseModel):
    id: int
    name: str
    type: str
    icon: str
    sortOrder: int
    createdAt: Optional[str] = None

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Topic
# ──────────────────────────────────────────────
class TopicCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    categoryId: int
    color: str = "#5B7C99"


class TopicUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = None


class TopicOut(BaseModel):
    id: int
    name: str
    description: str
    categoryId: int
    categoryType: Optional[str] = None
    isDefault: bool
    color: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Task
# ──────────────────────────────────────────────
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    status: str = Field(default="todo", pattern="^(todo|doing|done)$")
    importance: int = Field(default=3, ge=1, le=5)
    topicId: int


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(todo|doing|done)$")
    importance: Optional[int] = Field(None, ge=1, le=5)


class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    importance: int
    topicId: int
    completedAt: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# 统计 / Achievement / AI
# ──────────────────────────────────────────────
class AchievementSummary(BaseModel):
    totalDone: int
    avgImportance: float
    doneByMonth: dict  # {"2026-01": 5, "2026-02": 8, ...}
    highImportanceTasks: List[TaskOut]
    recentDone: List[TaskOut]


class AIAnalysisRequest(BaseModel):
    topicId: int
    promptExtra: str = ""  # 用户额外提示词


class AIAnalysisResponse(BaseModel):
    topicName: str
    analysis: str
    suggestions: str
    generatedAt: str


class AnnualSummaryRequest(BaseModel):
    topicId: int
    year: int = Field(..., ge=2020, le=2099)


class AnnualSummaryResponse(BaseModel):
    title: str
    outline: str       # Markdown 大纲
    keyNumbers: str     # 关键数据
    chartSuggestions: str  # 图表建议
    pptContent: str     # 可直接放入 PPT 的图文内容
