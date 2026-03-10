#user/router.py


from fastapi import APIRouter, Depends
from . import schemas, crud
from database import get_db


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}}
)


@router.post(
    path ="/register/",
    response_model=schemas.LoginResponse
)
async def register_user(user: schemas.RegisterUser, db = Depends(get_db)):
    new_user = await crud.register_user(user, db)
    return new_user


@router.get(
    path = "/list/",
    response_model=list[schemas.UserOut]
)
async def get_users(db = Depends(get_db)):
    users = await crud.get_users(0, 100, db)
    return users


@router.post(
    path = "/login/",
    response_model = schemas.LoginResponse,
    responses = {401: {"description": "Incorrect username or password"}}
)
async def verify_user(login_data: schemas.UserLogin, db = Depends(get_db)):
    response = await crud.verify_user(login_data, db)
    return response
