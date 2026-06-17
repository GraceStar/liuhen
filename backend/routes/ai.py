"""
AI 分析路由 — DeepSeek 复盘 + 年终工作总结
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
接口列表：
  POST /api/ai/analyze        → AI 复盘分析（成果 + 建议）
  POST /api/ai/annual-summary → 年终工作总结（PPT 友好格式）
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Task, Topic, User
from schemas import AIAnalysisRequest, AnnualSummaryRequest
from services.ai_service import analyze_achievements, generate_annual_summary
from routes.auth import get_current_user

router = APIRouter(prefix="/api/ai", tags=["AI分析"])


@router.post("/analyze")
async def analyze_topic(
    data: AIAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    AI 复盘：分析指定主题的已完成任务，生成成果总结和改进建议。
    只分析当前用户自己的主题。
    """
    # 验证主题归属
    result = await db.execute(
        select(Topic).where(Topic.id == data.topicId, Topic.user_id == current_user.id)
    )
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="主题不存在或无权限")

    # 查已完成任务
    result = await db.execute(
        select(Task)
        .where(Task.topic_id == data.topicId, Task.status == "done")
        .order_by(Task.completed_at.desc())
    )
    done_tasks = result.scalars().all()

    task_list = [t.to_dict() for t in done_tasks]
    ai_result = await analyze_achievements(topic.name, task_list, data.promptExtra)

    return {
        "topicName": topic.name,
        "analysis": ai_result["analysis"],
        "suggestions": ai_result["suggestions"],
        "generatedAt": datetime.utcnow().isoformat(),
    }


@router.post("/annual-summary")
async def annual_summary(
    data: AnnualSummaryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    生成年终工作总结（PPT 友好格式：大纲 + 关键数字 + 图表建议）。
    只分析当前用户自己的主题。
    """
    result = await db.execute(
        select(Topic).where(Topic.id == data.topicId, Topic.user_id == current_user.id)
    )
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="主题不存在或无权限")

    start = datetime(data.year, 1, 1)
    end = datetime(data.year + 1, 1, 1)
    result = await db.execute(
        select(Task)
        .where(
            Task.topic_id == data.topicId,
            Task.status == "done",
            Task.completed_at >= start,
            Task.completed_at < end,
        )
        .order_by(Task.completed_at.desc())
    )
    done_tasks = result.scalars().all()

    task_list = [t.to_dict() for t in done_tasks]
    summary = await generate_annual_summary(topic.name, data.year, task_list)

    return summary
