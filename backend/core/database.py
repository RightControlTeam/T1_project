

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr
from core.config import settings

RENAME_USER_MODULE_SQL = text("""
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'user_module'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'user'
    ) THEN
        ALTER TABLE user_module RENAME TO "user";
    END IF;
END $$;
""")


engine = create_async_engine(settings.database_url, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


async def get_db():
    async with async_session() as session:
        yield session


async def ensure_schema() -> None:
    """Create missing tables on startup (e.g. Render without Shell / Pre-Deploy)."""
    from booking.booking import Booking  # noqa: F401
    from resource.models import Resource, ResourceSchedule  # noqa: F401
    from user_module.user import User  # noqa: F401

    async with engine.begin() as conn:
        await conn.execute(RENAME_USER_MODULE_SQL)
        await conn.run_sync(Base.metadata.create_all)