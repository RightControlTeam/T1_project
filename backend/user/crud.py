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
from .admin_level import AdminLevel


#region get user/users

async def get_user_by_username(username: str, db: AsyncSession) -> Optional[User]:
    result = await db.scalar(
        select(User).where(User.username == username).where(User.is_active == True)
    )
    return result

async def get_user_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
    result = await db.scalar(
        select(User).where(User.id == user_id)
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )
    return result


async def get_users(admins: bool, skip: int, limit: int, db: AsyncSession) -> Sequence[User]:
    query = select(User).offset(skip).limit(limit).where(User.is_active == True)
    if admins:
        query = query.where(User.admin_level == AdminLevel.admin)
    else:
        query = query.where(User.admin_level == AdminLevel.user)
    result = await db.execute(query)
    return result.scalars().all()
#endregion

#region register
async def register_user(
        user_create: schemas.RegisterUser,
        db: AsyncSession,
        admin_level: int
) -> TokenResponse:
    existing_user = await get_user_by_username(user_create.username, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User already exists",
        )

    if admin_level == AdminLevel.creator:
        existing_creator = await db.scalar(
            select(User).where(User.admin_level == AdminLevel.creator)
        )
        if existing_creator is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Creator already exists",
            )


    password_hash: str = get_password_hash(user_create.password)
    new_user: User = User(
        username=user_create.username,
        password_hash=password_hash,
        admin_level= admin_level
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return generate_login_response(new_user.id, new_user.admin_level)

#endregion


#region misc
async def verify_user(login_data: OAuth2PasswordRequestForm, db: AsyncSession) -> TokenResponse:
    user: Optional[User] = await get_user_by_username(login_data.username, db)
    if (
        not user
        or not verify_password(login_data.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    return generate_login_response(user.id, user.admin_level)


async def test_delete(user: User, db: AsyncSession) -> None:
    # потом будет не очистка из бд, а отметка об удалении
    await db.delete(user)
    await db.commit()
#endregion


async def delete_by_id(user_id: int, db: AsyncSession) -> None:
    user: User = await get_user_by_id(user_id, db)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User is already deleted",
        )
    user.is_active = False
    await db.commit()
    await db.refresh(user)