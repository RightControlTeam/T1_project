#core/dependencies.py


from fastapi import HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db
from security.token import decode_jwt, JWTPayload
from user.crud import get_user_by_id
from user.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login/")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:

    payload: JWTPayload = decode_jwt(token)
    user_id: int = int(payload.sub)

    user: User = await get_user_by_id(user_id, db)

    if user is None:
        raise HTTPException(
            status_code = 404,
            detail = "User not found."
        )

    if user.is_deleted:
        raise HTTPException(
            status_code = 401,
            detail = "User is deleted."
        )

    return user