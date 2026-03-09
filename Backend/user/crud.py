#user/crud.py
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import User
from security import get_password_hash, verify_password, create_jwt
from typing import Optional, Tuple, Sequence
from . import schemas
from .schemas import LoginResponse


async def get_user(user_id: int, db: AsyncSession) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_users(skip: int, limit: int, db: AsyncSession) -> Sequence[User]:
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_user(user_create: schemas.UserCreate, db: AsyncSession) -> User:
    existing_user = await db.execute(
        select(User).where(User.username == user_create.username)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"User already exists",
        )
    password_hash = get_password_hash(user_create.password)
    db_user = User(
        username = user_create.username,
        password_hash = password_hash,
        is_admin = user_create.is_admin,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_username(username: str, db: AsyncSession) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def verify_user(login_data: schemas.UserLogin, db: AsyncSession) -> LoginResponse:
    user = await get_user_by_username(login_data.username, db)

    if(
        not user
        or user.is_deleted
        or not verify_password(login_data.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )


    token_data = {
        "sub": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    }

    jwt = create_jwt(data=token_data)

    return LoginResponse(
        jwt = jwt["jwt"],
        token_type = "bearer",
        username = user.username,
        is_admin = user.is_admin,
        jwt_exp_time = jwt["exp_time"]
    )


