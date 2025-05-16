from fastapi import APIRouter, Depends
from app.api.v1.deps.auth import get_current_user

router = APIRouter()

@router.get("/me")
async def read_user_me(current_user = Depends(get_current_user)):
    return current_user 