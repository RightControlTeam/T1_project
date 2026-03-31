from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Boolean, UniqueConstraint, Index,PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

from core.database import Base


class Booking(Base):
    id: Mapped[int] = mapped_column(Integer, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    deleted: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)


    user = relationship("User", backref="bookings")
    resource = relationship("Resource", backref="bookings")

    __table_args__ = (
        PrimaryKeyConstraint('id', 'start_time', name='booking_pkey'),
        Index('idx_booking_resource_time', 'resource_id', 'start_time'),
        Index('idx_booking_user_status', 'user_id', 'status'),
        Index('idx_booking_status_time', 'status', 'start_time'),
        {
            'postgresql_partition_by': 'RANGE (start_time)'
        }
    )

    def __repr__(self):
        return f"<Booking(id={self.id}, resource_id={self.resource_id}, start={self.start_time})>"