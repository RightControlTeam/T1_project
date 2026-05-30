from user_module.user import User
from user_module.schemas import UserResponse, UserRequest
from security.password_service import PasswordService
from typing import Optional


class UserMapper:
    @staticmethod
    def from_request(request: UserRequest, user: Optional[User] = None) -> Optional[User]:
        if request is None:
            return user
        if user is None:
            user = User()
        user.username = request.username
        user.password_hash = PasswordService.get_password_hash(request.password)
        return user


    @staticmethod
    def to_response(user: User) -> Optional[UserResponse]:
        if user is None:
            return None
        return UserResponse(
            id = user.id,
            username = user.username,
            admin_level = user.admin_level,
            is_active = user.is_active
        )

    @staticmethod
    def list_to_response(users: list[User]) -> list[UserResponse]:
        return [UserMapper.to_response(user) for user in users]