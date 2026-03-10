#user/router.py


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas, crud
from core.database import get_db
from .models import User
from core.dependencies import get_current_user
from security.token import TokenResponse

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}}
)


@router.post(
    path ="/register/",
    response_model = TokenResponse
)
async def register_user(
    user: schemas.RegisterUser,
    db = Depends(get_db)
):
    new_user: TokenResponse = await crud.register_user(user, db)
    return new_user


@router.get(
    path = "/list/",
    response_model=list[schemas.UserOut]
)
async def get_users(
        db = Depends(get_db)
):
    users = await crud.get_users(0, 100, db)
    return users


@router.post(
    path = "/login/",
    response_model = TokenResponse,
    responses = {401: {"description": "Incorrect username or password"}}
)
async def verify_user(
        login_data: schemas.UserLogin,
        db: AsyncSession = Depends(get_db)
):
    response = await crud.verify_user(login_data, db)
    return response


@router.get(
    path = "/profile/",
    response_model=schemas.UserOut
)
async def get_user_profile(
    user: User = Depends(get_current_user)
):
    return user
