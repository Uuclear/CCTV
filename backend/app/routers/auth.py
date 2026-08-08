# 管理员登录接口
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_admin, verify_password
from app.db import get_db
from app.models import AdminUser
from app.schemas import LoginIn, TokenOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Annotated[Session, Depends(get_db)]) -> TokenOut:
    """校验管理员账号并返回 JWT。"""
    user = db.query(AdminUser).filter(AdminUser.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    return TokenOut(access_token=create_access_token(user.username))


@router.get("/me")
def me(admin: Annotated[AdminUser, Depends(get_current_admin)]) -> dict:
    """返回当前登录管理员信息。"""
    return {"id": admin.id, "username": admin.username}
