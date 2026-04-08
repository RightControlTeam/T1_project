from datetime import time

from sqlalchemy.orm import Mapped, relationship

from core.database import Base
from sqlalchemy import String, Text, Boolean, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

class Resource(Base):
    __tablename__ = "resource"
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    name:Mapped[str] = mapped_column(String(100),nullable=False)
    type:Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active:Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)

    schedules: Mapped[list["ResourceSchedule"]] = relationship(back_populates="resource", cascade="all, delete-orphan")

class ResourceSchedule(Base):
    __tablename__ = "resource_schedule"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id", ondelete="CASCADE"))
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    resource: Mapped["Resource"] = relationship(back_populates="schedules")
