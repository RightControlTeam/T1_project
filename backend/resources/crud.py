from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from fastapi import HTTPException, status

from .models import Resource
from . import schemas

async def create_resource(db: AsyncSession,resource_data: schemas.ResourceCreate)-> Resource:
    data = resource_data.model_dump()
    db_resource = Resource(name = data["name"],
                           type = data["type"],
                           description = data.get("description"),
                           is_active = data.get("is_active",False)
                           )
    db.add(db_resource)
    await db.commit()
    await db.refresh(db_resource)
    return db_resource

async def get_resource(db: AsyncSession,resource_id:int) -> Optional[Resource]:
    result = await db.execute(
        select(Resource).where(Resource.id == resource_id)
    )
    return result.scalar_one_or_none()
async def get_resources(db: AsyncSession,  skip: int = 0,  limit: int = 100, type: Optional[str] = None) -> List[Resource]:
    query = select(Resource)
    if type:
           query = query.where(Resource.type == type)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_resource(db: AsyncSession,resource_id: int,resource_data: schemas.ResourceUpdate) -> Resource:
    resource = await get_resource(db,resource_id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Resource not found")
    update_data = resource_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)
    await db.commit()
    await db.refresh(resource)
    return resource

async def delete_resource(db: AsyncSession,resource_id) -> None:
    resource = await get_resource(db,resource_id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resource not found")
    await db.delete(resource)
    await db.commit()

