#main.py


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from user.router import user_router
from resource.router import resource_router
from booking.router import booking_router


app: FastAPI = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(user_router)
app.include_router(resource_router)
app.include_router(booking_router)


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)