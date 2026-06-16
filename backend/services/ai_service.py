"""AI 分析服务 - 封装 DeepSeek API 调用"""
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "sk-placeholder"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


async def analyze_achievements(
    topic_name: str,
    done_tasks: list[dict],
    prompt_extra: str = "",
) -> dict:
    """根据已完成任务分析成果并给出建议"""
    if not done_tasks:
        return {
            "analysis": "暂无已完成任务，无法进行分析。",
            "suggestions": "建议先完成一些任务，积累数据后再来复盘。",
        }

    # 拼接任务摘要
    task_summary = "\n".join(
        f"- [{t['importance']}★] {t['title']}"
        + (f"（完成于 {t['completedAt'][:10]}）" if t.get("completedAt") else "")
        for t in done_tasks
    )

    system_prompt = """你是一个专业的工作与生活复盘教练。根据用户提供的已完成任务列表，你需要：
1. 用简洁的结构化语言总结成果（分类归纳，突出亮点）
2. 指出不足之处或遗漏的方向
3. 给出 3-5 条具体的后续行动建议和改进措施

回复使用 Markdown 格式，分「成果总结」「不足与反思」「行动建议」三个章节。语言简洁有洞察力。"""

    user_prompt = f"""主题：{topic_name}

已完成任务列表：
{task_summary}

共完成 {len(done_tasks)} 项任务。
{"用户补充：" + prompt_extra if prompt_extra else ""}"""

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        content = response.choices[0].message.content

        # 简单拆分三段
        parts = content.split("##")
        analysis = parts[0].strip() if len(parts) > 0 else content
        suggestions = ""
        for p in parts[1:]:
            suggestions += "##" + p
        if not suggestions:
            suggestions = content

        return {"analysis": analysis, "suggestions": suggestions.strip()}
    except Exception as e:
        return {
            "analysis": f"AI 分析暂不可用。",
            "suggestions": f"错误信息：{str(e)}\n请检查 DeepSeek API Key 是否配置正确。",
        }


async def generate_annual_summary(
    topic_name: str,
    year: int,
    done_tasks: list[dict],
) -> dict:
    """生成年终工作总结（PPT 友好格式）"""
    if not done_tasks:
        return {
            "title": f"{year} 年工作总结 —— {topic_name}",
            "outline": "暂无数据",
            "keyNumbers": "暂无数据",
            "chartSuggestions": "暂无数据",
            "pptContent": "暂无数据",
        }

    task_summary = "\n".join(
        f"- [{t['importance']}★] {t['title']}"
        + (f"（{t['completedAt'][:10]}）" if t.get("completedAt") else "")
        for t in done_tasks
    )

    # 统计数据
    total = len(done_tasks)
    high_priority = sum(1 for t in done_tasks if t["importance"] >= 4)
    months = set()
    for t in done_tasks:
        if t.get("completedAt"):
            months.add(t["completedAt"][:7])

    stats = f"共 {total} 项，其中高优先级 {high_priority} 项，横跨 {len(months)} 个月"

    system_prompt = f"""你是一个专业的工作总结撰写助手。请根据用户提供的年度已完成任务，生成一份适合放入 PPT 的工作总结。

要求：
1. 【大纲】用层级清晰的结构（一级、二级标题）组织内容，包含：年度概览、核心成果、亮点突破、不足反思
2. 【关键数字】提取 5-8 个有说服力的量化指标（如完成数、高优先级占比、覆盖月份等）
3. 【图表建议】建议 2-3 种适合在 PPT 中展示的数据图表（如柱状图/折线图/饼图），说明用哪些数据、为什么
4. 【PPT图文】生成一段可直接放入 PPT 页面的结构化内容（含标题+要点+数据），每页一个主题

年份：{year}年"""

    user_prompt = f"""主题：{topic_name}
基础数据：{stats}

任务列表：
{task_summary}"""

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=3000,
        )
        content = response.choices[0].message.content

        return {
            "title": f"{year} 年工作总结 —— {topic_name}",
            "outline": content,
            "keyNumbers": stats,
            "chartSuggestions": "🧠 DeepSeek 已生成图表建议（见大纲）",
            "pptContent": content,
        }
    except Exception as e:
        return {
            "title": f"{year} 年工作总结 —— {topic_name}",
            "outline": f"生成失败：{str(e)}",
            "keyNumbers": stats,
            "chartSuggestions": "AI 暂不可用",
            "pptContent": f"基础数据：{stats}",
        }
