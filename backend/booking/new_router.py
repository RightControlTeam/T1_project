from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from booking.schemas import BookingOut, BookingRequest
from core.dependencies import get_current_user

from user_module.user import User
from core.dependencies import get_db
from booking.booking_service import BookingService


new_booking_router = APIRouter(
    prefix="/booking/v2",
    tags=["booking"]
)

@new_booking_router.post(
    "/",
    response_model=BookingOut,
    status_code=status.HTTP_201_CREATED
)
async def create_booking(
    new_booking: BookingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await BookingService.create(new_booking, user.id, db)


@new_booking_router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await BookingService.get_by_id(booking_id, db)


@new_booking_router.get("/", response_model=list[BookingOut])
async def get_bookings(
    user_id: Optional[int] = Query(None),
    resource_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await BookingService.get_all(db, user_id, resource_id)


@new_booking_router.put("/{booking_id}", response_model=BookingOut)
async def update_booking(
    booking_id: int,
    request: BookingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await BookingService.update(request, booking_id, user.id, db)


@new_booking_router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def cancel_booking(
    booking_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    await BookingService.cancel(booking_id, user.id, db)


