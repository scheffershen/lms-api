from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FilialeBase(BaseModel):
    name: str
    valid: bool = True

class FilialeCreate(FilialeBase):
    pass

class Filiale(FilialeBase):
    id: int
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    create_user_id: Optional[int] = None
    update_user_id: Optional[int] = None

    class Config:
        from_attributes = True 