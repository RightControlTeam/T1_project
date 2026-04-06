from sqlalchemy import Text, ForeignKey, Index,PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

from core.database import Base
from .status import BookingStatus


class Booking(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id", ondelete="CASCADE"))
    status: Mapped[BookingStatus] = mapped_column(default=BookingStatus.active)
    start_time: Mapped[datetime] = mapped_column()
    end_time: Mapped[datetime] = mapped_column()
    comment: Mapped[Optional[str]] = mapped_column(Text)
    deleted: Mapped[bool] = mapped_column(default=False)


    user = relationship("User", backref="bookings")
    resource = relationship("Resource", backref="bookings")

    # будем считать, что table args тут нет
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