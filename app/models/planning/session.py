# bonus/api/app/models/planning/session.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Session(BaseModel):
    id: int
    title: str
    start_date: datetime
    end_date: datetime
    is_valid: bool