import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, or_

from app.schemas.user import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.utils.security import hash_password, verify_password, create_access_token
from app.db.mysql import get_db
from app.db.redis import (
    get_redis, blacklist_token, store_refresh_token,
    get_refresh_user, revoke_refresh_token,
)
from app.middleware.auth import get_current_user
from app.models.user import User
from app.config import settings

router = APIRouter()


@router.post("/register")
async def register(req: RegisterRequest, db=Depends(get_db)):
    result = await db.execute(
        select(User.id).where(or_(User.username == req.username, User.email == req.email))
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "Username or email already exists")

    user = User(username=req.username, email=req.email, password_hash=hash_password(req.password))
    db.add(user)
    await db.flush()
    await db.commit()
    return {"success": True, "user_id": user.id, "username": user.username}


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db=Depends(get_db)):
    result = await db.execute(
        select(User.id, User.username, User.password_hash).where(User.username == req.username)
    )
    row = result.first()
    if not row or not verify_password(req.password, row[2]):
        raise HTTPException(401, "Invalid username or password")

    user_id = row[0]
    username = row[1]

    access_token = create_access_token(user_id)
    refresh_token = str(uuid.uuid4())

    r = await get_redis()
    await store_refresh_token(user_id, refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user_id,
        username=username,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest, db=Depends(get_db)):
    user_id = await get_refresh_user(req.refresh_token)
    if not user_id:
        raise HTTPException(401, "Invalid refresh token")

    result = await db.execute(select(User.username).where(User.id == user_id))
    row = result.first()
    if not row:
        raise HTTPException(404, "User not found")

    await revoke_refresh_token(req.refresh_token)

    access_token = create_access_token(user_id)
    new_refresh = str(uuid.uuid4())

    await store_refresh_token(user_id, new_refresh, settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        user_id=user_id,
        username=row[0],
    )


@router.post("/logout")
async def logout(req: RefreshRequest, user: dict = Depends(get_current_user)):
    await revoke_refresh_token(req.refresh_token)
    return {"success": True, "message": "Logged out"}
