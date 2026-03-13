from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from core.database import get_db
from core.dependencies import get_current_user
from user.models import User
from . import schemas, crud


router = APIRouter(
    prefix="/resource",
    tags=["resource"],
    responses={404: {"description": "Not found"}}
)

@router.post(
    "/",
    response_model=schemas.ResourceOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_resource(resource_data: schemas.ResourceCreate,db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user))->schemas.ResourceOut:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can do this")
    return await crud.create_resource(db, resource_data)


@router.get(
    "/{resource_id}",
    response_model=schemas.ResourceOut,
)
async def get_resource(resource_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user))-> schemas.ResourceOut:
    resource = await crud.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return resource

@router.get(
    "/",
    response_model=List[schemas.ResourceOut],
)
async def get_resources( db: AsyncSession = Depends(get_db),user: User = Depends(get_current_user))-> List[schemas.ResourceOut]:
    return await crud.get_resources(db)


@router.put(
    "/{resource_id}",
    response_model=schemas.ResourceOut,
)
async def update_resource(resource_id:int,resource_data: schemas.ResourceUpdate, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)) -> schemas.ResourceOut:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can do this")
    return await crud.update_resource(db, resource_id, resource_data)


@router.delete(
    "/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_resource(resource_id: int, db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can do this")
    await crud.delete_resource(db, resource_id)
    return None