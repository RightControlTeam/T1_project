from fastapi import HTTPException, status
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from .models import Booking
from .schemas import BookingRequest, BookingOut
from .booking_mapper import BookingMapper

from booking_repository import BookingRepository


class BookingService:


    @staticmethod
    async def run_booking_checks(
            booking: Booking,
            db: AsyncSession,
    ) -> None:
        resource_exists = await BookingRepository.check_resource_exists(booking, db)
        if not resource_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )

        schedule_match = await BookingRepository.check_schedule_match(booking, db)
        if not schedule_match:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking time range does not match schedule"
            )

        no_overlaps = await BookingRepository.check_no_overlaps(booking, db)
        if not no_overlaps:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking time overlaps with existing booking(s) for this resource",
            )


    @staticmethod
    def raise_if_not_found(booking: Booking) -> None:
        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking does not exist"
            )


    @staticmethod
    async def get_by_id(
            booking_id: int,
            db: AsyncSession
    ) -> BookingOut:
        booking: Booking = await BookingRepository.get_by_id(booking_id, db)
        BookingService.raise_if_not_found(booking)
        return BookingMapper.from_model_to_response(booking)


    @staticmethod
    async def create(
            request: BookingRequest,
            user_id: int,
            db: AsyncSession
    ) -> BookingOut:
        booking: Booking = BookingMapper.from_request_to_new(request, user_id)
        await BookingService.run_booking_checks(booking, db)
        booking = await BookingRepository.create(booking, db)
        return BookingMapper.from_model_to_response(booking)


    @staticmethod
    async def get_all(
        db: AsyncSession,
        user_id: int = None,
        resource_id: int = None
    ) -> list[BookingOut]:
        result: list[Booking] = await BookingRepository.get_all(db, user_id, resource_id)
        return BookingMapper.list_to_response(result)


    @staticmethod
    async def update(
            request: BookingRequest,
            booking_id: int,
            user_id: int,
            db: AsyncSession
    ) -> BookingOut:
        booking = await BookingRepository.get_by_id(booking_id, db)
        BookingService.raise_if_not_found(booking)

        if booking.is_cancelled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update a cancelled booking"
            )
        if user_id != booking.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to edit this booking"
            )

        booking = BookingMapper.from_request_to_existing(request, booking)
        await BookingService.run_booking_checks(booking, db)
        booking = await BookingRepository.update(booking, db)
        return BookingMapper.from_model_to_response(booking)


    @staticmethod
    async def cancel(
            booking_id: int,
            user_id: int,
            db: AsyncSession,
    ) -> BookingOut:
        booking: Booking = await BookingRepository.get_by_id(booking_id, db)
        BookingService.raise_if_not_found(booking)

        if user_id != booking.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to cancel this booking"
            )

        booking.is_cancelled = True
        booking = await BookingRepository.update(booking, db)
        return BookingMapper.from_model_to_response(booking)

