from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from slugify import slugify  # pip install python-slugify
from app.models.shared import UserShort

class AnswerType(BaseModel):
    id: int
    create_user: Optional[UserShort]
    update_user: Optional[UserShort]
    title: str
    title_fr: Optional[str] = None
    description: Optional[str]
    keywords: Optional[str]
    sort: Optional[int]
    revision: Optional[int]
    create_date: Optional[datetime]
    update_date: Optional[datetime]
    is_valid: bool
    conditional: Optional[str]

class AnswerTypeCreate(BaseModel):
    title: str
    title_fr: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    sort: Optional[int] = None
