from pydantic import BaseModel

class UserShort(BaseModel):
    user_id: int
    firstname: str
    lastname: str 