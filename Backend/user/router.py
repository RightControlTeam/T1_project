#user/router.py


from fastapi import APIRouter, Depends
from . import schemas, crud
from database import get_db


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}}
)


@router.post("/register/", response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db = Depends(get_db)):
    new_user = await crud.create_user(user, db)
    return new_user


@router.get("/list/", response_model=list[schemas.UserOut])
async def read_users(db = Depends(get_db)):
    users = await crud.get_users(0, 100, db)
    return users


@router.post(
    path = "/login/",
    response_model = schemas.LoginResponse,
    responses = {401: {"description": "Incorrect username or password"}}
    )
async def login(login_data: schemas.UserLogin, db = Depends(get_db)):
    response = await crud.verify_user(login_data, db)
    return response
