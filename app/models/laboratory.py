from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LaboratoryBase(BaseModel):
    name: str
    valid: bool = True

class LaboratoryCreate(LaboratoryBase):
    pass

class Laboratory(LaboratoryBase):
    id: int
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    create_user_id: Optional[int] = None
    update_user_id: Optional[int] = None

    class Config:
        from_attributes = True 