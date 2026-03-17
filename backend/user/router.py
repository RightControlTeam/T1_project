# user/router.py


from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from . import schemas, crud
from core.database import get_db
from .models import User
from core.dependencies import get_current_user, get_current_admin
from security.token import TokenResponse

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@user_router.post(
    path="/register/",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
        user: schemas.RegisterUser,
        db=Depends(get_db)
):
    new_user: TokenResponse = await crud.register_user(user, db)
    return new_user


@user_router.get(
    path="/list/",
    response_model=list[schemas.UserOut]
)
async def get_users(
        db=Depends(get_db)
):
    users = await crud.get_users(0, 100, db)
    return users


@user_router.post(
    path="/login/",
    response_model=TokenResponse,
)
async def verify_user(
        login_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    response: TokenResponse = await crud.verify_user(login_data, db)
    return response


@user_router.get(
    path="/profile/",
    response_model=schemas.UserOut
)
async def get_user_profile(
        user: User = Depends(get_current_user)
):
    return user


@user_router.delete(
    path="/delete/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user_test(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    await crud.delete_user(user, db)


@user_router.delete(
    path="/delete-admin/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_admin_test(
        user: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    await crud.delete_user(user, db)
