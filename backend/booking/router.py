import logging
from typing import Sequence, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from booking.schemas import BookingOut, BookingRequest
from core.dependencies import get_current_user

from user_module.user import User
from core.dependencies import get_db
from booking import crud

logger = logging.getLogger(__name__)
booking_router = APIRouter(
    prefix="/booking",
    tags=["booking"]
)

@booking_router.post(
    "/",
    response_model=BookingOut,
    status_code=status.HTTP_201_CREATED
)
async def create_booking(
    new_booking: BookingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"User {user.username} (ID {user.id}) is creating a booking for resource {new_booking.resource_id}")
    return await crud.create_booking(new_booking, user.id, db)


@booking_router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_booking_by_id(booking_id, db)


@booking_router.get("/", response_model=Sequence[BookingOut])
async def get_bookings(
    user_id: Optional[int] = Query(None),
    resource_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_bookings(db, user_id, resource_id)


@booking_router.put("/{booking_id}", response_model=BookingOut)
async def update_booking(
    booking_id: int,
    edited_booking: BookingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"User {user.username} (ID {user.id}) is updating booking ID {booking_id}")
    return await crud.update_booking(edited_booking, booking_id, user.id, db)


@booking_router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_booking(
    booking_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    logger.info(f"User {user.username} (ID: {user.id}) is cancelling booking ID: {booking_id}")
    await crud.cancel_booking(booking_id, user.id, db)


