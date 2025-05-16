from pydantic import BaseModel, HttpUrl
from typing import Optional

class LdapServerBase(BaseModel):
    url: str  # Using str instead of HttpUrl as LDAP URLs might not be HTTP
    bind_dn: str
    user_base_dn: str
    user_object_class_filter: str
    user_attributes: str
    username_attribute: str
    mail_attribute: str
    is_encrypted: bool = True

class LdapServerCreate(LdapServerBase):
    password: str

class LdapServerUpdate(LdapServerBase):
    password: Optional[str] = None

class LdapServer(LdapServerBase):
    id: int
    password: str  # Note: This should be handled carefully in responses

    class Config:
        from_attributes = True 