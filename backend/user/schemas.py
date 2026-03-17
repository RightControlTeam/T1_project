# user/schemas.py

from pydantic import BaseModel, field_validator
from user.validation import is_username_valid, is_password_valid


class RegisterUser(BaseModel):
    username: str
    password: str
    is_admin: bool

    @staticmethod
    @field_validator('username')
    def validate_username(value: str):
        if not is_username_valid(value):
            raise ValueError("Username validation error")
        return value

    @staticmethod
    @field_validator('password')
    def validate_password(value: str):
        if not is_password_valid(value):
            raise ValueError("Password validation error")
        return value


class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    is_deleted: bool
