from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.db.session import get_db_connection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db_connection)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    async with db.cursor() as cursor:
        await cursor.execute(
            "SELECT id, email, firstname, lastname, valid FROM users WHERE email = %s AND valid = TRUE",
            (email,)
        )
        user = await cursor.fetchone()
        
    if user is None:
        raise credentials_exception
        
    return {
        "id": user[0],
        "email": user[1],
        "firstname": user[2],
        "lastname": user[3],
        "valid": user[4]
    }

# For private endpoints
def get_auth_user():
    return Depends(get_current_user)

# For public endpoints with optional auth
async def get_optional_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False))
):
    if not token:
        return None
    return await get_current_user(token) 