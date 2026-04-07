from fastapi import HTTPException, status
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from .models import Booking
from .schemas import BookingCreate

async def create_booking(
        new_booking: BookingCreate,
        user_id: int,
        db: AsyncSession
) -> Booking:
    overlap = await db.scalar(
        select(Booking).where(
            and_(
                Booking.resource_id == new_booking.resource_id
                ,
                Booking.start_time <= new_booking.end_time
                ,
                Booking.end_time >= new_booking.start_time
            )
        )
    )

    if overlap is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking time overlaps with existing booking(s) for this resource",
        )

    booking_data = new_booking.model_dump()
    booking_data["user_id"] = user_id
    booking = Booking(**booking_data)
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


async def get_bookings(
    db: AsyncSession,
    user_id: int = None,
    resource_id: int = None
) -> Sequence[Booking]:
    query = select(Booking)

    if user_id is not None:
        query = query.where(Booking.user_id == user_id)

    if resource_id is not None:
        query = query.where(Booking.resource_id == resource_id)

    query = query.order_by(Booking.start_time.desc())

    result = await db.execute(query)
    return result.scalars().all()


