"""
认证模块 — 密码哈希 + JWT 令牌生成/验证

密码安全说明：
  虽然不要求密码复杂度，但存储时使用 PBKDF2 哈希（加盐），
  数据库中永远不会存明文密码，所以即使数据库泄露密码也不会暴露。

JWT 令牌说明：
  JWT = JSON Web Token，是一种自包含的身份凭证。
  登录成功后服务端生成令牌发给前端，前端每次请求都带上它，
  服务端验证令牌就知道是谁在请求。类比你手机 App 里的登录态 token。
"""
import hashlib
import os
import time
from datetime import datetime, timedelta, timezone

import jwt  # pip install pyjwt

# ──────────────────────────────────────────────
# JWT 配置（生产环境应使用环境变量，这里为简单写死）
# ──────────────────────────────────────────────
# SECRET 是签名令牌的密钥，只有服务端知道。泄露了 = 任何人可以伪造令牌。
# 建议改成随机字符串：python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = "liuhen-dev-secret-change-me-in-production"
# 令牌有效期：7 天
TOKEN_EXPIRE_DAYS = 7
# 加密算法（HS256 是对称加密，最常见的选择）
ALGORITHM = "HS256"


# ──────────────────────────────────────────────
# 密码处理
# ──────────────────────────────────────────────
def hash_password(password: str) -> str:
    """
    将明文密码哈希后存储。
    使用 PBKDF2-HMAC-SHA256 + 随机盐，每次哈希结果都不同。
    盐值拼接在哈希结果里，验证时可以分离出来重新计算。
    """
    salt = os.urandom(32)  # 32 字节随机盐
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    # 格式：salt的hex + ":" + 哈希结果的hex
    return salt.hex() + ":" + key.hex()


def verify_password(password: str, stored_hash: str) -> bool:
    """
    验证密码：提取存储的盐，用同样的算法计算一次，比较结果。
    """
    try:
        salt_hex, key_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        stored_key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return new_key == stored_key
    except (ValueError, AttributeError):
        return False


# ──────────────────────────────────────────────
# JWT 令牌
# ──────────────────────────────────────────────
def create_token(user_id: int, username: str) -> str:
    """
    为用户生成一个 JWT 令牌（登录成功时调用）。
    payload 里放了用户 ID 和用户名，后续可以从令牌中直接读出这些信息。
    exp = 过期时间，过期后令牌失效，需要重新登录。
    """
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS),
        "iat": datetime.now(timezone.utc),  # 签发时间
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    验证并解析 JWT 令牌，返回 payload 中的用户信息。
    返回 None 表示令牌无效或已过期。
    
    注意：这里只验证签名和过期时间，不查数据库，
    所以返回的 user_id 和 username 是可信的（除非密钥泄露）。
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user_id": payload["user_id"], "username": payload["username"]}
    except jwt.ExpiredSignatureError:
        return None  # 令牌已过期
    except jwt.InvalidTokenError:
        return None  # 令牌被篡改或无效
