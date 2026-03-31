from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.booking import BookingCreate, BookingRead
from logic.booking import create_new_booking
from security.auth import get_current_user

from backend.booking.models import Booking

router = APIRouter(
    prefix="/booking",
    tags=["booking"],
    responses={404: {"description": "Not found"}}

)


@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def make_booking(
        payload: BookingCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    new_booking = create_new_booking(
        db,
        user_id=current_user.id,
        resource_id=payload.resource_id,
        start=payload.start_time,
        end=payload.end_time,
        comment=payload.comment
    )

    if not new_booking:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Выбранное время уже занято. Пожалуйста, выберите другие слоты."
        )
    return new_booking

@router.get("/busy/{resource_id}")
async def get_busy_slots(
    resource_id: int,
    date: str,
    db: Session = Depends(get_db)
):
    day_start = datetime.strptime(date, "%Y-%m-%d")
    day_end = day_start + timedelta(days=1)

    busy = db.query(Booking).filter(
        Booking.resource_id == resource_id,
        Booking.deleted == False,
        Booking.start_time >= day_start,
        Booking.start_time < day_end
    ).all()

    return [{"start": b.start_time, "end": b.end_time} for b in busy]


@router.get("/my", response_model=list[BookingRead])
async def my_bookings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.deleted == False
    ).order_by(Booking.start_time.desc()).all()


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено или вы не его владелец")

    booking.deleted = True
    booking.status = "cancelled"
    db.commit()
    return None


@router.patch("/{booking_id}", response_model=BookingRead)
async def update_booking(
        booking_id: int,
        payload: BookingCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == current_user.id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")

    if booking.start_time.month != payload.start_time.month:
        booking.deleted = True
        booking.status = "cancelled"

        new_book = create_new_booking(
            db,
            user_id=current_user.id,
            **payload.model_dump()
        )
        if not new_book:
            db.rollback()
            raise HTTPException(status_code=409, detail="Новое время в другом месяце уже занято")
        db.commit()
        return new_book

    conflict = db.query(Booking).filter(
        Booking.resource_id == payload.resource_id,
        Booking.id != booking_id,
        Booking.deleted == False,
        Booking.start_time < payload.end_time,
        Booking.end_time > payload.start_time
    ).first()

    if conflict:
        raise HTTPException(status_code=409, detail="Новое время уже занято")

    booking.start_time = payload.start_time
    booking.end_time = payload.end_time
    booking.comment = payload.comment

    db.commit()
    db.refresh(booking)
    return booking

