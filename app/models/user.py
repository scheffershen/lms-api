from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    username: str
    email: EmailStr
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    valid: bool = True
    language: Optional[str] = None
    timezone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    laboratory_id: Optional[int] = None
    filiale_id: Optional[int] = None
    niveau_id: Optional[int] = None

class User(UserBase):
    id: int
    laboratory_id: Optional[int] = None
    filiale_id: Optional[int] = None
    niveau_id: Optional[int] = None
    roles: List[str]
    last_login: Optional[datetime] = None
    uuid: UUID
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    ldap_user: bool = False
    ticket_edit_rights_id: Optional[int] = None

    class Config:
        from_attributes = True 