from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import get_db
from uvicorn import run
import schemas
import crud

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/users/", response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db = Depends(get_db)):
    new_user = await crud.create_user(user, db)
    return new_user

@app.get("/users/", response_model=list[schemas.UserOut])
async def read_users(db = Depends(get_db)):
    users = await crud.get_users(0, 100, db)
    return users

@app.post("/login/", response_model=schemas.LoginResponse)
async def login(login_data: schemas.UserLogin, db = Depends(get_db)):
    user, message = await crud.verify_user(login_data, db)

    return schemas.LoginResponse(
        success=False if user is None else True,
        user=user,
        message=message,
    )

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)