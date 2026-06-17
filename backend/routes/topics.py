"""
主题路由 — CRUD 操作，所有操作需要登录
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
接口列表：
  GET    /api/topics       → 获取当前用户的所有主题
  POST   /api/topics       → 创建新主题
  PUT    /api/topics/{id}  → 修改主题（名称/描述/颜色）
  DELETE /api/topics/{id}  → 删除主题（级联删除任务）
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import get_db
from models import Topic, Category, User
from schemas import TopicCreate, TopicUpdate
from routes.auth import get_current_user

router = APIRouter(prefix="/api/topics", tags=["主题管理"])


@router.get("")
async def list_topics(
    category_id: int = None,
    current_user: User = Depends(get_current_user),  # 登录校验
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前登录用户的所有主题，可按分类筛选。
    
    关键：query 中加了 where(Topic.user_id == current_user.id)，
    保证每个用户只能看到自己的主题。
    """
    # selectinload 是 SQLAlchemy 的预加载 — 一次性把 Topic 及其关联的 Category 查出来
    # 避免 N+1 查询问题（查 10 个主题如果不预加载就要查 11 次）
    query = (
        select(Topic)
        .options(selectinload(Topic.category))
        .where(Topic.user_id == current_user.id)  # ← 数据隔离的关键
        .order_by(Topic.is_default.desc(), Topic.created_at)
    )
    if category_id is not None:
        query = query.where(Topic.category_id == category_id)
    result = await db.execute(query)
    topics = result.scalars().all()
    # categoryType 在 to_dict() 里是 None，这里用预先加载的关系填充
    return [
        {**t.to_dict(), "categoryType": t.category.type if t.category else None}
        for t in topics
    ]


@router.post("")
async def create_topic(
    data: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新主题 — 绑定到当前登录用户。
    """
    # 检查分类是否存在（防止传入不存在的 categoryId）
    result = await db.execute(select(Category).where(Category.id == data.categoryId))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="分类不存在")

    # 检查同名主题（同一用户下不能重名）
    result = await db.execute(
        select(Topic).where(
            Topic.name == data.name,
            Topic.category_id == data.categoryId,
            Topic.user_id == current_user.id,  # 只查当前用户的
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该分类下已存在同名主题")

    topic = Topic(
        name=data.name,
        description=data.description,
        category_id=data.categoryId,
        user_id=current_user.id,  # ← 绑定到当前用户
        color=data.color,
    )
    db.add(topic)
    await db.flush()
    await db.refresh(topic)
    return topic.to_dict()


@router.put("/{topic_id}")
async def update_topic(
    topic_id: int,
    data: TopicUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新主题（名称/描述/颜色均可修改）。
    
    只能修改自己的主题。
    """
    result = await db.execute(
        select(Topic).where(Topic.id == topic_id, Topic.user_id == current_user.id)
    )
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="主题不存在或无权限")

    # model_dump(exclude_unset=True) 只包含前端传了值的字段
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(topic, key, value)
    await db.flush()
    await db.refresh(topic)
    return topic.to_dict()


@router.delete("/{topic_id}")
async def delete_topic(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除主题 — 会级联删除其下所有任务。
    只能删除自己的主题，默认主题不可删除。
    """
    result = await db.execute(
        select(Topic).where(Topic.id == topic_id, Topic.user_id == current_user.id)
    )
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="主题不存在或无权限")
    if topic.is_default:
        raise HTTPException(status_code=400, detail="默认主题不可删除")

    await db.delete(topic)
    await db.flush()
    return {"ok": True, "message": f"主题「{topic.name}」已删除"}
