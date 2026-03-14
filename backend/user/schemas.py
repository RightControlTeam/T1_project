#user/schemas.py

from pydantic import BaseModel

class RegisterUser(BaseModel):
    username: str
    password: str
    is_admin: bool

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    is_deleted: bool