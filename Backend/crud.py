# crud.py
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import UserDB
from auth import get_password_hash, verify_password
from typing import Optional, Tuple, Sequence
import schemas


async def get_user(db: AsyncSession, user_id: int) -> Optional[UserDB]:
    result = await db.execute(select(UserDB).where(UserDB.id == user_id))
    return result.scalar_one_or_none()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[UserDB]:
    result = await db.execute(
        select(UserDB).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def create_user(db: AsyncSession, user_create: schemas.UserCreate) -> UserDB:
    existing_user = await db.execute(
        select(UserDB).where(UserDB.username == user_create.username)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"User already exists",
        )
    password_hash = get_password_hash(user_create.password)
    db_user = UserDB(
        username = user_create.username,
        password_hash = password_hash,
        is_admin = user_create.is_admin,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[UserDB]:
    result = await db.execute(select(UserDB).where(UserDB.username == username))
    return result.scalar_one_or_none()

async def verify_user(db: AsyncSession, username: str, password: str) -> Tuple[Optional[schemas.UserOut], str]:
    user = await get_user_by_username(db, username)
    if not user:
        return None, "User not found"
    if user.is_deleted:
        return None, "User is deleted"
    if verify_password(password, user.password_hash):
        return schemas.UserOut(
            id = user.id,
            username = user.username,
            is_admin= user.is_admin,
            is_deleted= user.is_deleted
        ), "Password match"
    return None, "Password not match"
