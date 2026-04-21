# user/models.py
from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base
from .admin_level import AdminLevel



class User(Base):
    __table_args__ = (
        Index(
            'uq_active_username',
            'username',
            unique=True,
            postgresql_where='is_active = true'
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50))
    password_hash: Mapped[str] = mapped_column(String(60))
    admin_level: Mapped[int] = mapped_column(default=AdminLevel.user)
    is_active: Mapped[bool] = mapped_column(default=True)

    @property
    def is_admin(self) -> bool:
        return self.admin_level == AdminLevel.admin

    @property
    def is_creator(self) -> bool:
        return self.admin_level == AdminLevel.creator
