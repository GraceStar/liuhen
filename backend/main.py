"""留痕 · 后端入口
──────── 类比 Android ────────
main.py          → Application 启动入口
@router.get/post → Retrofit 接口定义（但写在同一文件）
SQLAlchemy Model → Room Entity
Pydantic Schema  → Kotlin data class
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
from database import init_db
from models import Category
from routes import categories, topics, tasks, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库并插入默认数据"""
    await init_db()
    # 初始化三大分类 + 默认主题
    await seed_data()
    yield


async def seed_data():
    """插入三大分类和默认「日常工作」主题"""
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from database import async_session
    from models import CategoryType, Topic

    async with async_session() as db:
        # 检查是否需要插入
        result = await db.execute(select(Category).limit(1))
        if result.scalar_one_or_none():
            return  # 已有数据，跳过

        # 三大分类
        cats = [
            Category(name="工作", type=CategoryType.WORK.value, icon="💼", sort_order=1),
            Category(name="学习", type=CategoryType.STUDY.value, icon="📚", sort_order=2),
            Category(name="观察", type=CategoryType.OBSERVE.value, icon="🔍", sort_order=3),
        ]
        db.add_all(cats)
        await db.flush()

        # 默认主题：日常工作（属于「工作」分类）
        default_topic = Topic(
            name="日常工作",
            description="默认工作主题，用于记录日常工作事务",
            category_id=cats[0].id,
            is_default=1,
        )
        db.add(default_topic)
        await db.commit()


app = FastAPI(
    title="留痕 API",
    description="个人工作与学习进度记录面板",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
    )

# 注册路由
app.include_router(categories.router)
app.include_router(topics.router)
app.include_router(tasks.router)
app.include_router(ai.router)


@app.get("/")
async def root():
    return {"name": "留痕 API", "version": "1.0.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
