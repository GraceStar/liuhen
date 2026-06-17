"""
认证路由 — 注册 / 登录 / 获取当前用户信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API 端点说明：
  POST /api/auth/register  → 注册新用户
  POST /api/auth/login     → 登录，返回 JWT 令牌
  GET  /api/auth/me        → 获取当前登录用户信息（需要令牌）

JWT 工作流程（类比 Android 的 Session/Token）：
  1. 用户输入用户名密码 → 调用 login 接口
  2. 后端验证成功 → 签发一个 JWT 令牌返回
  3. 前端把令牌存 localStorage → 以后每次请求都放在 Authorization 头里
  4. 后端用 get_current_user 解析令牌 → 知道是谁在操作
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User, Topic
from schemas import RegisterRequest, LoginResponse, UserOut
from auth import hash_password, verify_password, create_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["用户认证"])


# ──────────────────────────────────────────────
# 辅助函数：从请求头中解析当前用户
# ──────────────────────────────────────────────
async def get_current_user(
    authorization: str = Header(None),  # HTTP 请求头中的 Authorization 字段
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    从请求头中取出 JWT 令牌，解析出用户 ID，查出完整用户对象。
    
    这是后端最重要的一个函数 — 所有需要登录的接口都靠它来识别用户。
    任何需要登录的操作（创建主题、添加任务等）都会先调用它。
    
    类比 Android：就像你在每个 Activity 的 onCreate 里先检查
    SharedPreferences 里有没有存登录 token。
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="请先登录")

    # 格式："Bearer xxxxxyyyyyzzzzz" → 取第二部分
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="令牌格式错误")

    token = parts[1]
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="令牌无效或已过期，请重新登录")

    # 查用户是否存在（防止令牌有效但用户被删除了的情况）
    result = await db.execute(select(User).where(User.id == payload["user_id"]))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user


# ──────────────────────────────────────────────
# 注册
# ──────────────────────────────────────────────
@router.post("/register", response_model=LoginResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    用户注册：用户名 + 密码即可，没有复杂度要求。
    
    1. 检查用户名是否已被占用
    2. 对密码做哈希（不存明文）
    3. 创建用户
    4. 自动创建默认的「日常工作」主题
    5. 返回 JWT 令牌（注册即登录）
    """
    # 检查用户名唯一性
    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已被占用")

    # 创建用户
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.flush()  # flush 使 user.id 生成

    # 自动创建默认「日常工作」主题（每个新用户都有）
    from models import Category, CategoryType
    result = await db.execute(
        select(Category).where(Category.type == CategoryType.WORK.value)
    )
    work_category = result.scalar_one()
    default_topic = Topic(
        name="日常工作",
        description="默认工作主题，用于记录日常工作事务",
        category_id=work_category.id,
        user_id=user.id,      # 绑定到当前用户
        is_default=1,
    )
    db.add(default_topic)

    await db.flush()
    await db.refresh(user)

    # 生成令牌，直接返回（前端拿到后存 localStorage 就登录了）
    token = create_token(user.id, user.username)
    return LoginResponse(
        token=token,
        user=UserOut(id=user.id, username=user.username, createdAt=user.created_at.isoformat()),
    )


# ──────────────────────────────────────────────
# 登录
# ──────────────────────────────────────────────
@router.post("/login", response_model=LoginResponse)
async def login(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    用户登录：验证用户名密码，返回 JWT 令牌。
    """
    # 按用户名查找
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_token(user.id, user.username)
    return LoginResponse(
        token=token,
        user=UserOut(id=user.id, username=user.username, createdAt=user.created_at.isoformat()),
    )


# ──────────────────────────────────────────────
# 获取当前用户
# ──────────────────────────────────────────────
@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的信息。
    前端每次打开页面时会先调这个，用于判断登录状态是否有效。
    """
    return UserOut(
        id=current_user.id,
        username=current_user.username,
        createdAt=current_user.created_at.isoformat(),
    )
