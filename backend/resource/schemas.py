from datetime import time
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ResourceCreate(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    is_active: bool = True

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ResourceScheduleCreate(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time

class ResourceScheduleOut(BaseModel):
    id: int
    day_of_week: int
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)

class ResourceOut(BaseModel):
    id: int
    name: str
    type: str
    description: Optional[str] = None
    is_active: bool
    schedules: List[ResourceScheduleOut] = []
    model_config = ConfigDict(from_attributes=True)

