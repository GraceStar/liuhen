"""任务路由 - 三态流转：todo / doing / done"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Task, Topic
from schemas import TaskCreate, TaskUpdate, AchievementSummary

router = APIRouter(prefix="/api/tasks", tags=["任务管理"])


@router.get("")
async def list_tasks(
    topic_id: int = None,
    status: str = None,
    importance: int = None,
    db: AsyncSession = Depends(get_db),
):
    """获取任务列表，可按主题、状态、重要程度筛选"""
    query = select(Task).order_by(Task.importance.desc(), Task.created_at.desc())
    if topic_id:
        query = query.where(Task.topic_id == topic_id)
    if status and status in ("todo", "doing", "done"):
        query = query.where(Task.status == status)
    if importance:
        query = query.where(Task.importance == importance)

    result = await db.execute(query)
    tasks = result.scalars().all()
    return [t.to_dict() for t in tasks]


@router.post("")
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    """创建新任务"""
    result = await db.execute(select(Topic).where(Topic.id == data.topicId))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="主题不存在")

    task = Task(
        title=data.title,
        description=data.description,
        status=data.status,
        importance=data.importance,
        topic_id=data.topicId,
        completed_at=datetime.utcnow() if data.status == "done" else None,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task.to_dict()


@router.put("/{task_id}")
async def update_task(task_id: int, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    """更新任务（含状态流转）"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    update_data = data.model_dump(exclude_unset=True)

    # 状态变为 done 时自动记录完成时间
    if "status" in update_data and update_data["status"] == "done" and task.status != "done":
        update_data["completed_at"] = datetime.utcnow()
    # 状态从 done 变为其他时清除完成时间
    elif "status" in update_data and update_data["status"] != "done":
        update_data["completed_at"] = None

    for key, value in update_data.items():
        setattr(task, key, value)

    await db.flush()
    await db.refresh(task)
    return task.to_dict()


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """删除任务"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    await db.delete(task)
    await db.flush()
    return {"ok": True, "message": "任务已删除"}


# ──────────────────────────────────────────────
# 成果统计（Achievement）
# ──────────────────────────────────────────────
@router.get("/achievements/{topic_id}")
async def get_achievements(
    topic_id: int,
    year: int = None,
    month: int = None,
    min_importance: int = Query(None, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
):
    """获取某个主题的成果统计"""
    result = await db.execute(select(Topic).where(Topic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="主题不存在")

    # 已完成任务查询
    query = select(Task).where(Task.topic_id == topic_id, Task.status == "done")

    # 时间筛选
    if year:
        if month:
            from datetime import date
            start = datetime(year, month, 1)
            query = query.where(Task.completed_at >= start)
            if month == 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, month + 1, 1)
            query = query.where(Task.completed_at < end)
        else:
            start = datetime(year, 1, 1)
            end = datetime(year + 1, 1, 1)
            query = query.where(Task.completed_at >= start, Task.completed_at < end)

    if min_importance:
        query = query.where(Task.importance >= min_importance)

    query = query.order_by(Task.completed_at.desc())
    result = await db.execute(query)
    done_tasks = result.scalars().all()

    if not done_tasks:
        return {
            "totalDone": 0,
            "avgImportance": 0,
            "doneByMonth": {},
            "highImportanceTasks": [],
            "recentDone": [],
        }

    # 按月分组
    month_map = {}
    for t in done_tasks:
        if t.completed_at:
            key = t.completed_at.strftime("%Y-%m")
            if key not in month_map:
                month_map[key] = 0
            month_map[key] += 1

    # 排序月份
    sorted_months = dict(sorted(month_map.items()))

    return {
        "totalDone": len(done_tasks),
        "avgImportance": round(sum(t.importance for t in done_tasks) / len(done_tasks), 1),
        "doneByMonth": sorted_months,
        "highImportanceTasks": [t.to_dict() for t in done_tasks if t.importance >= 4],
        "recentDone": [t.to_dict() for t in done_tasks[:10]],
    }
