"""数据模型定义 - 类似 Room 的 @Entity 注解"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


# ──────────────────────────────────────────────
# 枚举类型
# ──────────────────────────────────────────────
class CategoryType(str, enum.Enum):
    """三大类型"""
    WORK = "work"       # 工作
    STUDY = "study"     # 学习
    OBSERVE = "observe" # 观察


class TaskStatus(str, enum.Enum):
    """任务三态"""
    TODO = "todo"       # 计划
    DOING = "doing"     # 进行中
    DONE = "done"       # 已完成


class ImportanceLevel(int, enum.Enum):
    """重要程度 1-5 星"""
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


# ──────────────────────────────────────────────
# 数据表
# ──────────────────────────────────────────────
class Category(Base):
    """分类表：工作 / 学习 / 观察"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    type = Column(String(30), nullable=False, unique=True)  # work/study/observe
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


class Topic(Base):
    """主题表：日常工作、英语学习、育儿观察 等"""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    is_default = Column(Integer, default=0)  # 1=默认主题（日常工作）
    color = Column(String(20), default="#5B7C99")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="topics")
    tasks = relationship("Task", back_populates="topic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "categoryId": self.category_id,
            "categoryType": None,  # 将由路由层填充
            "isDefault": bool(self.is_default),
            "color": self.color,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }


class Task(Base):
    """任务表：Todo / Doing / Done 三态"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    status = Column(String(10), nullable=False, default="todo")  # todo / doing / done
    importance = Column(Integer, default=3)  # 1-5
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    completed_at = Column(DateTime, nullable=True)  # done 时间
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
