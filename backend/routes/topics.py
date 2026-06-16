"""主题路由 - CRUD"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database import get_db
from models import Topic, Category
from schemas import TopicCreate, TopicUpdate

router = APIRouter(prefix="/api/topics", tags=["主题管理"])


@router.get("")
async def list_topics(category_id: int = None, db: AsyncSession = Depends(get_db)):
    """获取所有主题，可按分类筛选"""
    query = select(Topic).options(selectinload(Topic.category)).order_by(Topic.is_default.desc(), Topic.created_at)
    if category_id is not None:
        query = query.where(Topic.category_id == category_id)
    result = await db.execute(query)
    topics = result.scalars().all()
    return [
        {**t.to_dict(), "categoryType": t.category.type if t.category else None}
        for t in topics
    ]


@router.post("")
async def create_topic(data: TopicCreate, db: AsyncSession = Depends(get_db)):
    """创建新主题"""
    # 检查分类是否存在
    result = await db.execute(select(Category).where(Category.id == data.categoryId))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="分类不存在")
    # 检查同名
    result = await db.execute(
        select(Topic).where(Topic.name == data.name, Topic.category_id == data.categoryId)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该分类下已存在同名主题")

    topic = Topic(
        name=data.name,
        description=data.description,
        category_id=data.categoryId,
        color=data.color,
    )
    db.add(topic)
    await db.flush()
    await db.refresh(topic)
    return topic.to_dict()


@router.put("/{topic_id}")
async def update_topic(topic_id: int, data: TopicUpdate, db: AsyncSession = Depends(get_db)):
    """更新主题（名称/描述/颜色均可修改）"""
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="主题不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(topic, key, value)
    await db.flush()
    await db.refresh(topic)
    return topic.to_dict()


@router.delete("/{topic_id}")
async def delete_topic(topic_id: int, db: AsyncSession = Depends(get_db)):
    """删除主题（级联删除其下所有任务）"""
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="主题不存在")
    if topic.is_default:
        raise HTTPException(status_code=400, detail="默认主题不可删除")

    await db.delete(topic)
    await db.flush()
    return {"ok": True, "message": f"主题「{topic.name}」已删除"}
