# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import decode_token
from app.repositories.auth_repo.user_auth_repository import user_auth_repository

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    # Header se token nikalo
    token = credentials.credentials

    # Decode karo
    payload = decode_token(token)

    # User dhundo
    user_id = payload.get("sub")
    user = await user_auth_repository.find_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user