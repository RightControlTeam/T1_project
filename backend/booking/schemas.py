from pydantic import BaseModel, field_validator
from datetime import datetime, UTC

class BookingCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime

    @field_validator('start_time')
    def check_start_time(cls, value: datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        if value < datetime.now(UTC):
            raise ValueError('Start time cannot be before current time')
        return value

    @field_validator('end_time')
    def check_times(cls, value, info):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        start = info.data.get('start_time')
        if start:
            if value <= start:
                raise ValueError('Время окончания должно быть позже времени начала')
            duration = value - start
            if duration.total_seconds() > 12 * 3600:
                raise ValueError('Максимальное время бронирования 12 часов')
        return value


class BookingOut(BaseModel):
    # fields
    id: int
    user_id: int
    resource_id: int
    start_time: datetime
    end_time: datetime

    # properties
    is_cancelled: bool
    is_pending: bool
    is_active: bool
    is_ended: bool

    model_config = {"from_attributes": True}
