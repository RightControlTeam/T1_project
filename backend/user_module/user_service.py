from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from fastapi.security import OAuth2PasswordRequestForm

from core.config import settings

from security.password_service import PasswordService
from security.token_service import generate_login_response, TokenResponse

from user_module.user import User
from user_module.admin_level import AdminLevel
from user_module.schemas import UserResponse, UserRequest, CreatorRequest
from user_module.user_mapper import UserMapper
from user_module.user_repository import UserRepository
from user_module.login_data_validator import LoginDataValidator

class UserService:
    @staticmethod
    def raise_if_not_found_or_not_active(user: Optional[User], user_id: int) -> None:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} doesn't exist",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with ID {user_id} is not active",
            )

    @staticmethod
    async def get_by_username(username: str, db: AsyncSession) -> Optional[UserResponse]:
        result: Optional[User] = await UserRepository.get_by_username(username, db)
        return UserMapper.to_response(result)

    @staticmethod
    async def get_by_id(user_id: int, db: AsyncSession) -> Optional[UserResponse]:
        result: Optional[User] = await UserRepository.get_by_id(user_id, db)
        return UserMapper.to_response(result)

    @staticmethod
    async def get_range(
        admins: bool,
        skip: int,
        limit: int,
        db: AsyncSession
    ) -> tuple[list[UserResponse], int]:
        result: tuple[list[User], int] = await UserRepository.get_range(admins, skip, limit, db)
        return UserMapper.list_to_response(result[0]), result[1]


    @staticmethod
    async def create(
            request: UserRequest,
            db: AsyncSession,
            admin_level: int
    ) -> TokenResponse:
        existing_user = await UserRepository.get_by_username(request.username, db)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User already exists",
            )

        if admin_level == AdminLevel.creator:
            existing_creator = await UserRepository.find_creator(db)
            if existing_creator is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Creator already exists",
                )

        new_user: User = UserMapper.from_request(request)
        new_user.admin_level = admin_level
        new_user = await UserRepository.create(new_user, db)
        return generate_login_response(new_user)


    @staticmethod
    async def create_creator(request: CreatorRequest, db: AsyncSession) -> TokenResponse:
        if request.creator_registration_key != settings.CREATOR_REGISTRATION_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Creator registration key is incorrect"
            )
        return await UserService.create(request, db, AdminLevel.creator)


    @staticmethod
    async def verify_user(login_data: OAuth2PasswordRequestForm, db: AsyncSession) -> TokenResponse:
        if not LoginDataValidator.is_username_valid(login_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username validation error",
            )
        if not LoginDataValidator.is_password_valid(login_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password validation error",
            )
        user: Optional[User] = await UserRepository.get_by_username(login_data.username, db)
        if (
            user is None
            or
            not PasswordService.verify_password(login_data.password, user.password_hash)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        return generate_login_response(user)


    @staticmethod
    async def delete_by_id(user_id: int, db: AsyncSession) -> UserResponse:
        user = await UserRepository.get_by_id(user_id, db)
        UserService.raise_if_not_found_or_not_active(user, user_id)
        user.is_active = False
        result: User = await UserRepository.update(user, db)
        return UserMapper.to_response(result)


    @staticmethod
    async def delete_other_by_id(user_id: int, db: AsyncSession, creator_id: int) -> UserResponse:
        if user_id == creator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete yourself by id, use simple delete"
            )
        return await UserService.delete_by_id(user_id, db)


    @staticmethod
    async def update(user_id: int, request: UserRequest, db: AsyncSession) -> UserResponse:
        user: Optional[User] = await UserRepository.get_by_id(user_id, db)
        UserService.raise_if_not_found_or_not_active(user, user_id)
        user = UserMapper.from_request(request, user)
        user = await UserRepository.update(user, db)
        return UserMapper.to_response(user)

