from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from resource.models import ResourceSchedule, Resource
from .models import Booking


class BookingRepository:
    @staticmethod
    async def check_no_overlaps(
            booking: Booking,
            db: AsyncSession,
    ) -> bool:
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
        if booking.id is not None:
            query = query.where(Booking.id != booking.id)
        result = await db.scalar(query)
        return result is None


    @staticmethod
    async def check_resource_exists(
            booking: Booking,
            db: AsyncSession,
    ) -> bool:
        result = await db.scalar(
            select(Resource).where(Resource.id == booking.resource_id)
        )
        return result is not None


    @staticmethod
    async def check_schedule_match(
            booking: Booking,
            db: AsyncSession,
    ) -> bool:
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
        return match_range is not None


    @staticmethod
    async def get_by_id(
            booking_id: int,
            db: AsyncSession
    ) -> Optional[Booking]:
        return await db.scalar(
            select(Booking).where(Booking.id == booking_id)
        )


    @staticmethod
    async def create(
            booking: Booking,
            db: AsyncSession
    ) -> Booking:
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return booking


    @staticmethod
    async def update(
            booking: Booking,
            db: AsyncSession
    ) -> Booking:
        await db.merge(booking)
        await db.commit()
        await db.refresh(booking)
        return booking


    @staticmethod
    async def get_all(
        db: AsyncSession,
        user_id: int = None,
        resource_id: int = None
    ) -> list[Booking]:
        query = select(Booking)
        if user_id is not None:
            query = query.where(Booking.user_id == user_id)
        if resource_id is not None:
            query = query.where(Booking.resource_id == resource_id)
        query = query.order_by(Booking.start_time.desc())
        result = await db.execute(query)
        return list(result.scalars().all())


