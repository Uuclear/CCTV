# JWT 认证与密码哈希工具
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import AdminUser

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """对明文密码做 bcrypt 哈希。"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文密码是否匹配哈希。"""
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    """签发管理员访问令牌。"""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": subject, "exp": expire},
        settings.secret_key,
        algorithm="HS256",
    )


def _resolve_admin(
    creds: HTTPAuthorizationCredentials | None,
    db: Session,
) -> AdminUser | None:
    """解析令牌中的管理员，无效则返回 None。"""
    if creds is None:
        return None
    try:
        payload = jwt.decode(creds.credentials, settings.secret_key, algorithms=["HS256"])
        username = payload.get("sub")
    except JWTError:
        return None
    if not username:
        return None
    return db.query(AdminUser).filter(AdminUser.username == username).first()


def get_current_admin(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> AdminUser:
    """从 Bearer Token 解析当前管理员，失败则 401。"""
    user = _resolve_admin(creds, db)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="未登录或令牌无效")
    return user


def get_optional_admin(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> AdminUser | None:
    """可选管理员：无令牌时返回 None，不抛错。"""
    return _resolve_admin(creds, db)
