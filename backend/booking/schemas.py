import zoneinfo

from pydantic import BaseModel, field_validator
from datetime import datetime, UTC, timedelta
from core.config import settings

class BookingCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime

    @field_validator('start_time')
    def check_start_time(cls, value: datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=settings.time_zone)
        else:
            raise ValueError('start_time must have no timezone info')
        if value < datetime.now(settings.time_zone):
            raise ValueError('Start time cannot be before current time')
        return value

    @field_validator('end_time')
    def check_end_time(cls, value, info):
        if value.tzinfo is None:
            value = value.replace(tzinfo=settings.time_zone)
        else:
            raise ValueError('end_time must have no timezone info')
        start = info.data.get('start_time')
        if start:
            if value <= start:
                raise ValueError('End time should be after start time')
            duration: timedelta = value - start
            if duration > timedelta(hours=12):
                raise ValueError('Maximum booking time length is 12 hours')
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
