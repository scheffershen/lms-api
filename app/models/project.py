from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    laboratory_id: int
    code: str
    title: str
    email: EmailStr
    valid: bool = True
    slug: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    color_id: Optional[int] = None
    background_color_id: Optional[int] = None
    smtp_id: Optional[int] = None
    create_user_id: Optional[int] = None
    update_user_id: Optional[int] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    revision: int
    sort: int

    class Config:
        from_attributes = True 