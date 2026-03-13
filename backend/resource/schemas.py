from typing import Optional

from pydantic import BaseModel,ConfigDict

class ResourceCreate(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    is_active: bool = True

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ResourceOut(BaseModel):
    id: int
    name: str
    type: str
    description: Optional[str] = None
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


