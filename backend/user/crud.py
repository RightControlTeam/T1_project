# user/crud.py


from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Sequence
from fastapi.security import OAuth2PasswordRequestForm

from security.password import get_password_hash, verify_password
from security.token import generate_login_response, TokenResponse
from .models import User
from . import schemas

async def get_user_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(username: str, db: AsyncSession) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_users(skip: int, limit: int, db: AsyncSession) -> Sequence[User]:
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def register_user(user_create: schemas.RegisterUser, db: AsyncSession) -> TokenResponse:
    existing_user = await get_user_by_username(user_create.username, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User already exists",
        )
    password_hash: str = get_password_hash(user_create.password)
    db_user: User = User(
        username=user_create.username,
        password_hash=password_hash,
        is_admin=user_create.is_admin,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return generate_login_response(db_user.id)


async def verify_user(login_data: OAuth2PasswordRequestForm, db: AsyncSession) -> TokenResponse:

    user: Optional[User] = await get_user_by_username(login_data.username, db)
    if (
            not user
            or user.is_deleted
            or not verify_password(login_data.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    return generate_login_response(user.id)


async def delete_user(user: User, db: AsyncSession) -> None:
    # потом будет не очистка из бд, а отметка об удалении
    await db.delete(user)
    await db.commit()
