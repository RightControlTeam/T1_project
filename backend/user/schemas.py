#user/schemas.py

from pydantic import BaseModel, Field, field_validator
from re import match

class RegisterUser(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    password: str = Field(min_length=8, max_length=40)
    is_admin: bool

    @field_validator('username')
    def validate_username(cls, value: str):
        if not match(r'^\w+$', value):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        if match(r'^[0-9_]', value):
            raise ValueError('Username cannot start with a digit or an underscore')
        return value


class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    is_deleted: bool