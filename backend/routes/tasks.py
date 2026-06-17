"""
任务路由 — 三态流转：todo ↔ doing ↔ done
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
核心概念：
  Todo  = 计划中（还没开始做）
  Doing = 进行中（现在正在做的事，可以有多个）
  Done  = 已完成（记录完成时间，变成成果数据）

状态流转规则：Todo → Doing → Done（可回退）
状态变为 done 时自动记录完成时间（completedAt）。
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Task, Topic, User
from schemas import TaskCreate, TaskUpdate, AchievementSummary
from routes.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["任务管理"])


# ──────────────────────────────────────────────
# 辅助：验证主题归属
# ──────────────────────────────────────────────
async def _get_user_topic(topic_id: int, user: User, db: AsyncSession) -> Topic:
    """
    验证主题属于当前用户，防止用户操作别人的主题。
    返回 Topic 对象，如果不存在或不属于当前用户则抛 404。
    """
    result = await db.execute(
        select(Topic).where(Topic.id == topic_id, Topic.user_id == user.id)
    )
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="主题不存在或无权限")
    return topic


# ──────────────────────────────────────────────
# 获取任务列表
# ──────────────────────────────────────────────
@router.get("")
async def list_tasks(
    topic_id: int = None,
    status: str = None,
    importance: int = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取任务列表，可按主题、状态、重要程度筛选。
    
    重要：只返回当前用户的任务（通过 Topic.user_id 过滤）。
    """
    # 构建基础查询：从 Task 表出发，关联 Topic，再按 user_id 过滤
    query = (
        select(Task)
        .join(Topic)  # JOIN 是为了能按 Topic.user_id 过滤
        .where(Topic.user_id == current_user.id)
        .order_by(Task.importance.desc(), Task.created_at.desc())
    )
    if topic_id:
        query = query.where(Task.topic_id == topic_id)
    if status and status in ("todo", "doing", "done"):
        query = query.where(Task.status == status)
    if importance:
        query = query.where(Task.importance == importance)

    result = await db.execute(query)
    tasks = result.scalars().all()
    return [t.to_dict() for t in tasks]


# ──────────────────────────────────────────────
# 创建任务
# ──────────────────────────────────────────────
@router.post("")
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新任务。需确保目标主题属于当前用户。
    """
    await _get_user_topic(data.topicId, current_user, db)

    task = Task(
        title=data.title,
        description=data.description,
        status=data.status,
        importance=data.importance,
        topic_id=data.topicId,
        # 如果初始状态就是 done，直接记录完成时间
        completed_at=datetime.utcnow() if data.status == "done" else None,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task.to_dict()


# ──────────────────────────────────────────────
# 更新任务（含状态流转）
# ──────────────────────────────────────────────
@router.put("/{task_id}")
async def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新任务（标题/状态/重要程度）。
    
    状态流转逻辑：
    - 变为 done → 自动记录 completedAt
    - 从 done 变回其他状态 → 清除 completedAt（"取消完成"）
    """
    # JOIN Topic 确保任务属于当前用户
    result = await db.execute(
        select(Task).join(Topic).where(Task.id == task_id, Topic.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或无权限")

    update_data = data.model_dump(exclude_unset=True)

    # 状态流转时自动处理完成时间
    if "status" in update_data:
        if update_data["status"] == "done" and task.status != "done":
            update_data["completed_at"] = datetime.utcnow()
        elif update_data["status"] != "done":
            update_data["completed_at"] = None

    for key, value in update_data.items():
        setattr(task, key, value)

    await db.flush()
    await db.refresh(task)
    return task.to_dict()


# ──────────────────────────────────────────────
# 删除任务
# ──────────────────────────────────────────────
@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除任务 — 只能删自己的。
    """
    result = await db.execute(
        select(Task).join(Topic).where(Task.id == task_id, Topic.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在或无权限")

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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取某个主题的成果统计面板数据。
    支持按年份、月份、重要程度筛选。
    """
    # 验证主题归属
    await _get_user_topic(topic_id, current_user, db)

    # 查询已完成任务
    query = select(Task).where(Task.topic_id == topic_id, Task.status == "done")

    # 时间筛选
    if year:
        if month:
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, month + 1, 1)
            query = query.where(Task.completed_at >= start, Task.completed_at < end)
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

    # 按月分组统计
    month_map = {}
    for t in done_tasks:
        if t.completed_at:
            key = t.completed_at.strftime("%Y-%m")
            month_map[key] = month_map.get(key, 0) + 1

    return {
        "totalDone": len(done_tasks),
        "avgImportance": round(sum(t.importance for t in done_tasks) / len(done_tasks), 1),
        "doneByMonth": dict(sorted(month_map.items())),
        "highImportanceTasks": [t.to_dict() for t in done_tasks if t.importance >= 4],
        "recentDone": [t.to_dict() for t in done_tasks[:10]],
    }
