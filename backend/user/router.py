from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from .validation import is_password_valid, is_username_valid

from . import schemas, crud
from core.database import get_db
from .models import User
from core.dependencies import get_current_user, get_current_admin, get_current_creator
from security.token import TokenResponse
from core.config import settings
from .admin_level import AdminLevel

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)

#region register
@user_router.post(
    path="/register-user",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
        user: schemas.RegisterUser,
        db=Depends(get_db)
):
    new_user: TokenResponse = await crud.register_user(user, db, AdminLevel.user)
    return new_user



@user_router.post(
    path="/register-admin",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_admin(
        user: schemas.RegisterUser,
        db=Depends(get_db),
        _creator: User = Depends(get_current_creator)
):
    new_user: TokenResponse = await crud.register_user(user, db, AdminLevel.admin)
    return new_user

@user_router.post(
    path="/register-creator",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_creator(
        user: schemas.RegisterAdmin,
        db=Depends(get_db)
):
    if user.creator_registration_key != settings.CREATOR_REGISTRATION_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Creator registration key is incorrect"
        )
    new_user: TokenResponse = await crud.register_user(user, db, AdminLevel.creator)
    return new_user
#endregion

#region login
@user_router.post(
    path="/login/",
    response_model=TokenResponse,
)
async def verify_user(
        login_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    if not is_username_valid(login_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username validation error",
        )
    if not is_password_valid(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password validation error",
        )
    response: TokenResponse = await crud.verify_user(login_data, db)
    return response
#endregion

#region get
@user_router.get(
    path="/profile/",
    response_model=schemas.UserOut
)
async def get_profile(
        user: User = Depends(get_current_user)
):
    return user


@user_router.get(
    path="/",
    response_model=list[schemas.UserOut]
)
async def get_users(
    admins: bool = False,
    skip: int = 0,
    limit: int = 10,
    _: User = Depends(get_current_creator),
    db=Depends(get_db)
):
    users = await crud.get_users(admins, skip, limit, db)
    return users


@user_router.get(
    path="/{user_id}",
    response_model=schemas.UserOut
)
async def get_by_id(
    user_id: int,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await crud.get_user_by_id(user_id, db)
    return result
#endregion

#region delete
@user_router.delete(
    path="/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_me(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    await crud.delete_by_id(user.id, db)

@user_router.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_by_id(
        user_id: int,
        creator: User = Depends(get_current_creator),
        db: AsyncSession = Depends(get_db)
):
    if user_id == creator.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't delete yourself by id, use simple delete"
        )
    await crud.delete_by_id(user_id, db)

#endregion

#region ONLY FOR TEST
@user_router.delete(
    path="/delete/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user_test(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    await crud.test_delete(user, db)


@user_router.delete(
    path="/delete-admin/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_admin_test(
        user: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db)
):
    await crud.test_delete(user, db)

#endregion