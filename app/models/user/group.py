from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class Group(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_valid: bool