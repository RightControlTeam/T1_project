from sqlalchemy import ForeignKey, func, and_, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from datetime import datetime, UTC

from core.database import Base


class Booking(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id", ondelete="CASCADE"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_cancelled: Mapped[bool] = mapped_column(default=False)

    @hybrid_property
    def is_ended(self) -> bool:
        return self.end_time <= datetime.now(UTC)

    @is_ended.expression
    def is_ended(cls) -> bool:
        return cls.end_time <= func.now()

    @hybrid_property
    def is_pending(self):
        return self.start_time >= datetime.now(UTC)

    @is_pending.expression
    def is_pending(cls):
        return cls.start_time >= func.now()

    @hybrid_property
    def is_active(self) -> bool:
        return self.start_time <= datetime.now(UTC) <= self.end_time

    @is_active.expression
    def is_active(cls):
        now = func.now()
        return and_(cls.start_time <= now, cls.end_time >= now)

    user = relationship("User", backref="bookings")
    resource = relationship(
        "Resource",
        backref=backref(
            "bookings",
            cascade="all, delete-orphan",
            passive_deletes=True
        )
    )


    def __repr__(self):
        return f"<Booking(id={self.id}, resource_id={self.resource_id}, start={self.start_time})>"

"""
    __table_args__ = (
        PrimaryKeyConstraint('id', 'start_time', name='booking_pkey'),
        Index('idx_booking_resource_time', 'resource_id', 'start_time'),
        Index('idx_booking_user_status', 'user_id', 'status'),
        Index('idx_booking_status_time', 'status', 'start_time'),
        {
            'postgresql_partition_by': 'RANGE (start_time)'
        }
    )"""
