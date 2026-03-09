#user/schemas.py


from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    is_deleted: bool


class UserLogin(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    jwt: str
    token_type: str = "bearer"
    username: str
    is_admin: bool = False
    jwt_exp_time: int