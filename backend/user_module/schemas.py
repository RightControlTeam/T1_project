from pydantic import BaseModel, field_validator
from user_module.login_data_validator import is_username_valid, is_password_valid


class UserRequest(BaseModel):
    username: str
    password: str

    @field_validator('username')
    def validate_username(cls, value: str):
        if not is_username_valid(value):
            raise ValueError("Username validation error")
        return value

    @field_validator('password')
    def validate_password(cls, value: str):
        if not is_password_valid(value):
            raise ValueError("Password validation error")
        return value

class CreatorRequest(UserRequest):
    creator_registration_key: str

class UserResponse(BaseModel):
    id: int
    username: str
    admin_level: int
    is_active: bool
