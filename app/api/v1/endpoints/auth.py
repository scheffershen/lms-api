from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password
from app.db.session import get_db_connection
from app.core.config import settings
import bcrypt
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPException, LDAPBindError
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_db_connection)
):
    try:
        logger.info(f"Login attempt for user: {form_data.username}")
        
        # Get user from database
        async with db.cursor() as cursor:
            await cursor.execute(
                "SELECT id, email, password, ldap_user FROM fos_user WHERE (email = %s OR username = %s) AND is_valid = TRUE AND enabled = TRUE",
                (form_data.username, form_data.username)
            )
            user = await cursor.fetchone()
            logger.info(f"User query result: {user is not None}")

        if not user:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id, email, password_hash, ldap_user = user            
        password = str(form_data.password)  # Cast to str to fix type issues
        logger.info(f"User found - ID: {user_id}, LDAP: {ldap_user}")

        if ldap_user:
            logger.info("Attempting LDAP authentication")
            async with db.cursor() as cursor:
                await cursor.execute(
                    "SELECT url, bind_dn, password, user_base_dn FROM ldap_servers WHERE id = 1"
                )
                ldap_server = await cursor.fetchone()
                ldap_url, bind_dn, bind_pw, user_base_dn = ldap_server

            try:
                # Direct bind like PHP version
                server = Server(ldap_url, get_info=ALL)
                conn = Connection(server, user=user_base_dn, password=form_data.password, auto_bind=True)
                conn.unbind()
                logger.info("LDAP authentication successful")
            except (LDAPException, LDAPBindError) as e:
                logger.error(f"LDAP authentication failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="LDAP authentication failed",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            logger.info("Attempting local password authentication")
            if not verify_password(password, password_hash):
                logger.warning("Local password authentication failed")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            logger.info("Local password authentication successful")

        # Create access token
        access_token = create_access_token(
            data={"sub": email},  # use email as subject
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        logger.info("Access token created successfully")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Symfony uses bcrypt with the format "$2y$" while Python's bcrypt uses "$2b$"
    # We need to replace the prefix to make it compatible
    if hashed_password.startswith('$2y$'):
        hashed_password = '$2b$' + hashed_password[4:]
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8')) 