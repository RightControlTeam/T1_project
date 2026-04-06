#core/dependencies.py


from fastapi import HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from security.token import decode_jwt, JWTPayload
from user.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login/")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:

    payload: JWTPayload = decode_jwt(token)
    user_id: int = int(payload.sub)

    user: User | None = await db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code = 404,
            detail = "User not found."
        )

    if not user.is_active:
        raise HTTPException(
            status_code = 401,
            detail = "User is deleted."
        )

    return user


async def get_current_admin(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    user: User = await get_current_user(token, db)
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin privileges required."
        )
    return user


async def get_current_creator(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    user: User = await get_current_user(token, db)
    if not user.is_creator:
        raise HTTPException(
            status_code=403,
            detail="Access denied. Creator privileges required."
        )
    return user
