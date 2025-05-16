from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnswerType(BaseModel):
    id: int
    create_user_id: Optional[int]
    update_user_id: Optional[int]
    title: str
    description: Optional[str]
    keywords: Optional[str]
    sort: Optional[int]
    revision: Optional[int]
    create_date: Optional[datetime]
    update_date: Optional[datetime]
    is_valid: bool
    conditional: Optional[str]
