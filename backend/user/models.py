# user/models.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from enum import IntEnum

from core.database import Base

class AdminLevel(IntEnum):
    NONE = 0
    ADMIN = 1
    CREATOR = 2

class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    admin_level: Mapped[int] = mapped_column(default=AdminLevel.NONE, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False, nullable=False)

    @property
    def is_admin(self) -> bool:
        return self.admin_level == AdminLevel.ADMIN

    @property
    def is_creator(self) -> bool:
        return self.admin_level == AdminLevel.CREATOR
