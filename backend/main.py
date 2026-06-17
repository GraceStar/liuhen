"""
留痕 · 后端入口 — FastAPI 应用的主文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
类比 Android 开发的对应概念：
  main.py                  → Application.onCreate()    启动入口
  @router.get("/api/xxx")  → Retrofit @GET("/api/xxx")  API 定义
  SQLAlchemy Model         → Room @Entity               数据表
  Pydantic Schema          → Kotlin data class           数据校验
  Depends(get_db)          → RoomDatabase.dao()          数据库依赖注入
  Depends(get_current_user)→ 登录拦截器                   用户鉴权

启动方式：
  开发环境: python main.py  → 自动生成 API 文档 http://localhost:8000/docs
  生产环境: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
from database import init_db
# 必须先导入所有 Model，SQLAlchemy 才知道要建哪些表
from models import User, Category, Topic, Task
from routes import categories, topics, tasks, ai, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理 — FastAPI 启动/关闭时自动调用的钩子。
    
    @asynccontextmanager 是 Python 的异步上下文管理器，
    yield 之前 = 启动时执行，yield 之后 = 关闭时执行。
    类似 Android 的 Application.onCreate() / onTerminate()。
    """
    await init_db()       # 创建所有数据库表（如果还不存在）
    await seed_data()     # 插入预置的分类数据
    yield                 # 应用正式开始运行
    # 这里可以加关闭时的清理逻辑（如果需要的话）


async def seed_data():
    """
    初始化数据 — 只在数据库为空时执行。
    
    现在只插入三大分类（所有用户共享），
    默认「日常工作」主题改为在用户注册时自动创建，每人一个。
    """
    from sqlalchemy import select
    from database import async_session
    from models import Category, CategoryType

    async with async_session() as db:
        # 检查是否已经有数据了
        result = await db.execute(select(Category).limit(1))
        if result.scalar_one_or_none():
            return  # 已有数据，不重复插入

        # 三大分类（全站共享）
        cats = [
            Category(name="工作", type=CategoryType.WORK.value, icon="💼", sort_order=1),
            Category(name="学习", type=CategoryType.STUDY.value, icon="📚", sort_order=2),
            Category(name="观察", type=CategoryType.OBSERVE.value, icon="🔍", sort_order=3),
        ]
        db.add_all(cats)
        await db.commit()


# ──────────────────────────────────────────────
# FastAPI 应用实例
# ──────────────────────────────────────────────
app = FastAPI(
    title="留痕 API",
    description="个人工作与学习进度记录面板 — 支持多用户",
    version="1.1.0",
    lifespan=lifespan,
)

# ──────────────────────────────────────────────
# CORS 跨域配置
# ──────────────────────────────────────────────
# 为什么需要 CORS？
#   前端 (localhost:5173) 和后端 (localhost:8000) 在不同端口，
#   浏览器默认禁止跨域请求。加了这个中间件就允许前端调后端 API。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# 全局异常处理 — 把错误信息返回给前端，方便调试
# ──────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()  # 服务端打印完整错误堆栈
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
    )

# ──────────────────────────────────────────────
# 注册所有 API 路由
# ──────────────────────────────────────────────
app.include_router(auth.router)        # 注册/登录
app.include_router(categories.router)  # 分类列表
app.include_router(topics.router)      # 主题 CRUD（需登录）
app.include_router(tasks.router)       # 任务 CRUD（需登录）
app.include_router(ai.router)          # AI 分析（需登录）


@app.get("/")
async def root():
    return {
        "name": "留痕 API",
        "version": "1.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    # reload=True 表示代码改了就自动重启（仅开发环境用）
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
