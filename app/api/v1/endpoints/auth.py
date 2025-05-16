from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password
from app.db.session import get_db_connection
from app.core.config import settings
from passlib.hash import bcrypt

router = APIRouter()

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_db_connection)
):
    # Get user from database
    async with db.cursor() as cursor:
        await cursor.execute(
            "SELECT id, email, password FROM users WHERE email = %s AND valid = TRUE",
            (form_data.username,)
        )
        user = await cursor.fetchone()

    if not user or not verify_password(form_data.password, user[2]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user[1]},  # use email as subject
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user[0],
            "email": user[1]
        }
    } 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Symfony uses bcrypt with the format "$2y$" while Python's bcrypt uses "$2b$"
    # We need to replace the prefix to make it compatible
    if hashed_password.startswith('$2y$'):
        hashed_password = '$2b$' + hashed_password[4:]
    return bcrypt.verify(plain_password, hashed_password) 