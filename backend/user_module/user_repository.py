from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from .user import User
from .admin_level import AdminLevel


class UserRepository:
    @staticmethod
    async def get_by_username(username: str, db: AsyncSession) -> Optional[User]:
        result = await db.scalar(
            select(User).filter_by(username = username, is_active = True)
        )
        return result

    @staticmethod
    async def get_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
        result = await db.scalar(
            select(User).filter_by(id = user_id)
        )
        return result

    @staticmethod
    async def get_range(
        admins: bool,
        skip: int,
        limit: int,
        db: AsyncSession
    ) -> tuple[list[User], int]:
        base_query = select(User).filter_by(is_active = True)
        if admins:
            base_query = base_query.filter_by(admin_level = AdminLevel.admin)
        else:
            base_query = base_query.filter_by(admin_level = AdminLevel.user)


        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar_one()


        list_query = base_query.offset(skip).limit(limit)
        result = await db.execute(list_query)
        users =  result.scalars().all()

        return list(users), total_count

    @staticmethod
    async def create(user: User, db: AsyncSession) -> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update(user: User, db: AsyncSession) -> User:
        user = await db.merge(user)
        await db.commit()
        return user

    @staticmethod
    async def find_creator(db: AsyncSession) -> Optional[User]:
        return await db.scalar(
            select(User).where(User.admin_level == AdminLevel.creator)
        )