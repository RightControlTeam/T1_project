from sqlalchemy.orm import Mapped

from core.database import Base
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional, List
from datetime import datetime

class Resource(Base):
    id:Mapped[int] = mapped_column(primary_key=True,index=True)
    name:Mapped[str] = mapped_column(String(100),nullable=False)
    type:Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active:Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)
