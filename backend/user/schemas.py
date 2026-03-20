# user/schemas.py

from pydantic import BaseModel, field_validator
from user.validation import is_username_valid, is_password_valid


class RegisterUser(BaseModel):
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

class RegisterAdmin(RegisterUser):
    admin_registration_key: str




class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    is_deleted: bool
