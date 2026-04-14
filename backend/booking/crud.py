from fastapi import HTTPException, status
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from resource.models import ResourceSchedule, Resource
from .models import Booking
from .schemas import BookingCreate

# region Checks

async def check_time_overlap(
        booking: BookingCreate,
        db: AsyncSession,
        filter_id: int | None = None
) -> None:
    query = select(Booking).where(
            and_(
                Booking.resource_id == booking.resource_id
                ,
                Booking.start_time < booking.end_time
                ,
                Booking.end_time > booking.start_time
                ,
                Booking.is_cancelled == False
            )
        )
    if filter_id is not None:
        query = query.where(Booking.id != filter_id)

    result = await db.scalar(query)

    if result is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking time overlaps with existing booking(s) for this resource",
        )


async def check_existing_resource(
        booking: BookingCreate,
        db: AsyncSession,
) -> None:
    existing_resource = await db.scalar(
        select(Resource).where(Resource.id == booking.resource_id)
    )
    if existing_resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )


async def check_schedule(
        booking: BookingCreate,
        db: AsyncSession,
) -> None:
    week_day: int = booking.start_time.weekday()
    match_range = await db.scalar(
        select(ResourceSchedule).where(
            and_(
                ResourceSchedule.resource_id == booking.resource_id,
                ResourceSchedule.start_time <= booking.start_time.time(),
                ResourceSchedule.end_time >= booking.end_time.time(),
                ResourceSchedule.day_of_week == week_day
            )
        )
    )
    if match_range is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking time range does not match schedule"
        )


async def check_and_find_existing_booking(
        booking_id: int,
        db: AsyncSession,
) -> Booking:
    existing_booking = await get_booking_by_id(booking_id, db)
    if existing_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return existing_booking
# endregion

# region Crud

async def get_booking_by_id(
        booking_id: int,
        db: AsyncSession
):
    return await db.scalar(
        select(Booking).where(Booking.id == booking_id)
    )


async def create_booking(
        new_booking: BookingCreate,
        user_id: int,
        db: AsyncSession
) -> Booking:

    await check_existing_resource(new_booking, db)
    await check_schedule(new_booking, db)
    await check_time_overlap(new_booking, db)

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


async def update_booking(
        updated_booking: BookingCreate,
        booking_id: int,
        user_id: int,
        db: AsyncSession
) -> Booking:
    await check_existing_resource(updated_booking, db)
    await check_schedule(updated_booking, db)
    await check_time_overlap(updated_booking, db, booking_id)
    existing_booking = await check_and_find_existing_booking(booking_id, db)

    if existing_booking.is_cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a cancelled booking"
        )

    if user_id != existing_booking.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this booking"
        )

    existing_booking.start_time = updated_booking.start_time
    existing_booking.end_time = updated_booking.end_time
    existing_booking.resource_id = updated_booking.resource_id

    await db.commit()
    await db.refresh(existing_booking)
    return existing_booking



async def cancel_booking(
        booking_id: int,
        user_id: int,
        db: AsyncSession,
) -> None:
    existing_booking = await check_and_find_existing_booking(booking_id, db)

    if user_id != existing_booking.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this booking"
        )

    existing_booking.is_cancelled = True
    await db.commit()

# endregion
