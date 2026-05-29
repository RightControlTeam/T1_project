from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from . import schemas
from core.database import get_db
from .user import User
from core.dependencies import get_current_user, get_current_admin, get_current_creator
from security.token_service import TokenResponse
from .admin_level import AdminLevel
import logging
from .user_service import UserService

from .user_mapper import UserMapper

logger = logging.getLogger(__name__)
user_router = APIRouter(
    prefix = "/user",
    tags = ["user"],
)

#region register
@user_router.post(
    path = "/register-user",
    response_model = TokenResponse,
    status_code = status.HTTP_201_CREATED
)
async def register_user(
        user: schemas.UserRequest,
        db=Depends(get_db)
):
    return await UserService.create(user, db, AdminLevel.user)


@user_router.post(
    path = "/register-admin",
    response_model = TokenResponse,
    status_code = status.HTTP_201_CREATED
)
async def register_admin(
        user: schemas.UserRequest,
        db=Depends(get_db),
        _creator: User = Depends(get_current_creator)
):
    return await UserService.create(user, db, AdminLevel.admin)

@user_router.post(
    path="/register-creator",
    response_model = TokenResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_creator(
        user: schemas.CreatorRequest,
        db=Depends(get_db)
):
    return await UserService.create_creator(user, db)
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
    return await UserService.verify_user(login_data, db)
#endregion

#region get
@user_router.get(
    path="/profile/",
    response_model=schemas.UserResponse
)
async def get_profile(
        user: User = Depends(get_current_user)
):
    return UserMapper.to_response(user)


@user_router.get(
    path="/",
    response_model=list[schemas.UserResponse]
)
async def get_range(
    response: Response,
    admins: bool = False,
    skip: int = 0,
    limit: int = 10,
    _: User = Depends(get_current_creator),
    db=Depends(get_db)
):
    users, total_count = await UserService.get_range(admins, skip, limit, db)
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    return users


@user_router.get(
    path="/{user_id}",
    response_model=schemas.UserResponse
)
async def get_by_id(
    user_id: int,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    return await UserService.get_by_id(user_id, db)
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
    await UserService.delete_by_id(user.id, db)


@user_router.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_by_id(
        user_id: int,
        creator: User = Depends(get_current_creator),
        db: AsyncSession = Depends(get_db)
):
    await UserService.delete_other_by_id(user_id, db, creator.id)
#endregion

#region Update
@user_router.put(
    path="/",
    response_model=schemas.UserResponse
)
async def update(
    request: schemas.UserRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await UserService.update(user.id, request, db)
#endregion