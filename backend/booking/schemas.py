from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timedelta
from typing import  Optional

class BookingCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime
    comment: Optional[str] = None

    @field_validator('end_time')
    def check_times(cls, v, info):
        start = info.data.get('start_time')
        if start:
            if v <= start:
                raise ValueError('Время окончания должно быть позже времени начала')
            duration = v - start
            if duration.total_seconds() > 12 * 3600:
                raise ValueError('Максимальное время бронирования 12 часов')
        return v
class BookingRead(BaseModel):
    id: int
    user_id: int
    resource_id: int
    start_time: datetime
    end_time: datetime
    status: str
    deleted: bool

    class Config:
        from_attributes = True