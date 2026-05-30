from typing import Optional, Sequence
from .booking import Booking
from .schemas import BookingRequest, BookingOut


class BookingMapper:
    @staticmethod
    def from_request_to_new(
            request: BookingRequest,
            user_id: int,
    ) -> Booking:
        booking = Booking()
        booking.user_id = user_id
        booking.resource_id = request.resource_id
        booking.start_time = request.start_time
        booking.end_time = request.end_time
        return booking

    @staticmethod
    def from_request_to_existing(
            update_schema: BookingRequest,
            existing_booking: Booking
    ) -> Booking:
        existing_booking.resource_id = update_schema.resource_id
        existing_booking.start_time = update_schema.start_time
        existing_booking.end_time = update_schema.end_time
        return existing_booking

    @staticmethod
    def from_model_to_response(booking: Booking) -> Optional[BookingOut]:
        if booking is None:
            return None
        return BookingOut(
            id=booking.id,
            user_id=booking.user_id,
            resource_id=booking.resource_id,
            start_time=booking.start_time,
            end_time=booking.end_time,
            is_cancelled=booking.is_cancelled,
            is_pending=booking.is_pending, # type: ignore
            is_active=booking.is_active, # type: ignore
            is_ended=booking.is_ended # type: ignore
        )

    @staticmethod
    def list_to_response(bookings: Sequence[Booking]) -> list[BookingOut]:
        return [BookingMapper.from_model_to_response(booking) for booking in bookings]