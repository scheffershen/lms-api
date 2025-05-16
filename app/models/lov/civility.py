# bonus/api/app/models/lov/civility.py
from pydantic import BaseModel

class Civility(BaseModel):
    id: int
    title: str