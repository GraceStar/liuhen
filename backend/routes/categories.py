"""分类路由 - GET /api/categories 类似 Android 的 @GET("categories")"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Category

router = APIRouter(prefix="/api/categories", tags=["分类管理"])


@router.get("")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """获取所有分类（工作/学习/观察）"""
    result = await db.execute(select(Category).order_by(Category.sort_order))
    categories = result.scalars().all()
    return [c.to_dict() for c in categories]


@router.get("/{category_id}")
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category.to_dict()
