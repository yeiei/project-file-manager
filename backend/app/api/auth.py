"""认证 API"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User


router = APIRouter(prefix="/api/auth", tags=["auth"])

# Token 过期时间配置
TOKEN_EXPIRE_HOURS = 24 * 7  # 7 天


def hash_password(password: str) -> str:
    """使用 SHA-256 + salt 加密密码"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    try:
        salt, pwd_hash = password_hash.split("$")
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == pwd_hash
    except Exception:
        return False


def create_token(user_id: int) -> str:
    """创建简单的 token"""
    # 使用 user_id + 时间戳 + 随机数生成 token
    timestamp = datetime.utcnow()
    random_part = secrets.token_hex(16)
    token_data = f"{user_id}:{timestamp.isoformat()}:{random_part}"
    # 简单的 base64 编码
    import base64
    return base64.b64encode(token_data.encode()).decode()


def verify_token(token: str) -> Optional[int]:
    """验证 token 并返回 user_id"""
    try:
        import base64
        decoded = base64.b64decode(token.encode()).decode()
        parts = decoded.split(":")
        if len(parts) >= 3:
            return int(parts[0])
        return None
    except Exception:
        return None


# Pydantic 模型
class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user_id: int
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime


@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 加密密码
    password_hash = hash_password(request.password)

    # 创建用户
    user = User(
        username=request.username,
        password_hash=password_hash
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        created_at=user.created_at
    )


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    # 查找用户
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 生成 token
    token = create_token(user.id)

    return LoginResponse(
        token=token,
        user_id=user.id,
        username=user.username
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证 token")

    # 解析 Authorization header (Bearer token)
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="无效的认证方式")
    except ValueError:
        raise HTTPException(status_code=401, detail="无效的认证方式")

    # 验证 token
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="无效或已过期的 token")

    # 获取用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return UserResponse(
        id=user.id,
        username=user.username,
        created_at=user.created_at
    )
