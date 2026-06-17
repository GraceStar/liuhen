"""
数据模型定义 — 定义数据库中所有的表和字段结构
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
类比 Android Room 开发：
  SQLAlchemy Model  = Room 的 @Entity 注解的数据类
  Column(...)       = Room 的 @ColumnInfo 字段属性
  relationship(...) = Room 的 @Relation 外键关系
  Base              = RoomDatabase 的基类
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


# ──────────────────────────────────────────────
# 枚举类型（固定选项的字段，类似 Kotlin 的 enum class）
# ──────────────────────────────────────────────
class CategoryType(str, enum.Enum):
    """三大分类类型 — 用于主题分组"""
    WORK = "work"       # 工作
    STUDY = "study"     # 学习
    OBSERVE = "observe" # 观察


class TaskStatus(str, enum.Enum):
    """任务的三态流转 — Todo → Doing → Done"""
    TODO = "todo"       # 计划中，还没开始
    DOING = "doing"     # 正在进行中（可以有多个）
    DONE = "done"       # 已完成


class ImportanceLevel(int, enum.Enum):
    """任务重要程度 — 1 到 5 星"""
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


# ──────────────────────────────────────────────
# 用户表 — 每个用户可以独立注册账号
# ──────────────────────────────────────────────
class User(Base):
    """
    用户表：存储每个注册用户的基本信息。

    密码存储使用 PBKDF2 哈希 + 随机盐 (见 auth.py)，
    数据库中绝不存储明文密码。
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True, index=True)  # 唯一用户名，建立索引加速查询
    password_hash = Column(String(200), nullable=False)  # 哈希后的密码，不是明文
    created_at = Column(DateTime, default=datetime.utcnow)

    # 一对多关系：一个用户有多个主题，删除用户时级联删除其所有主题
    topics = relationship("Topic", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        """转为 API 可返回的字典格式"""
        return {
            "id": self.id,
            "username": self.username,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


# ──────────────────────────────────────────────
# 分类表 — 全局共享（所有用户看到的分类相同）
# ──────────────────────────────────────────────
class Category(Base):
    """
    分类表：工作 / 学习 / 观察 —— 系统预置，所有用户共享。
    不绑定到具体用户，由 seed_data() 自动创建。
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    type = Column(String(30), nullable=False, unique=True)  # 对应 CategoryType 的值
    icon = Column(String(10), default="📋")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    topics = relationship("Topic", back_populates="category", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "icon": self.icon,
            "sortOrder": self.sort_order,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }


# ──────────────────────────────────────────────
# 主题表 — 每个用户独立管理自己的主题
# ──────────────────────────────────────────────
class Topic(Base):
    """
    主题表：日常工作、英语学习、育儿观察等。
    
    关键改动：新增 user_id 外键，每个用户只能看到和操作自己的主题。
    这样 A 用户创建的主题，B 用户完全看不到。
    """
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 新增：归属用户
    is_default = Column(Integer, default=0)  # 1 = 默认主题（每个用户注册时创建的"日常工作"）
    color = Column(String(20), default="#5B7C99")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # SQLAlchemy 的关系映射 — 用法类似 Room 的 @Relation
    category = relationship("Category", back_populates="topics")
    user = relationship("User", back_populates="topics")
    tasks = relationship("Task", back_populates="topic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "categoryId": self.category_id,
            "categoryType": None,  # 由路由层查询 category 关系后填充
            "isDefault": bool(self.is_default),
            "color": self.color,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


# ──────────────────────────────────────────────
# 任务表 — Todo / Doing / Done 三态流转
# ──────────────────────────────────────────────
class Task(Base):
    """
    任务表：Todo / Doing / Done 三态，带重要程度星级。
    
    任务属于具体主题，主题属于具体用户。
    所以查询任务时通过 topic → user_id 就能确保数据隔离。
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)       # 任务标题
    description = Column(Text, default="")             # 详细描述
    status = Column(String(10), nullable=False, default="todo")  # todo / doing / done
    importance = Column(Integer, default=3)            # 重要程度 1-5 星
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    completed_at = Column(DateTime, nullable=True)     # 完成时间（status 变为 done 时自动记录）
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    topic = relationship("Topic", back_populates="tasks")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "importance": self.importance,
            "topicId": self.topic_id,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
