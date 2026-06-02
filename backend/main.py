#main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

import logging

from core.database import ensure_schema
from user_module.user_router import user_router
from resource.router import resource_router
from booking.router import booking_router
from booking.new_router import new_booking_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_schema()
    yield


app: FastAPI = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("backend.log")
    ]
)
logger = logging.getLogger("t1_project")

app.include_router(user_router)
app.include_router(resource_router)
app.include_router(booking_router)
app.include_router(new_booking_router)


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)