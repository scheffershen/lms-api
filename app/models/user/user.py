from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: EmailStr
    firstname: str
    lastname: str
    enabled: bool = True
    salt: Optional[str] = None
    password: Optional[str] = None
    last_login: Optional[datetime] = None
    confirmation_token: Optional[str] = None
    password_requested_at: Optional[datetime] = None
    roles: List[str] = []
    photo: Optional[str] = None
    function: Optional[str] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None
    address_bis: Optional[str] = None
    phone: Optional[str] = None
    ldap_user: bool = False
    user_dn: Optional[str] = None
    keycloak_id: Optional[str] = None
    hierarchy_level: int = 0
    is_valid: bool = True
    last_change_password: Optional[datetime] = None
    laboratory_id: Optional[int] = None
    ldap_server_id: Optional[int] = None
