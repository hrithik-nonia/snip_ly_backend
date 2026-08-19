# app/dependencies.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.security import decode_access_token
from app.repositories.auth_repo.user_auth_repository import user_auth_repository

bearer_scheme = HTTPBearer()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
):
    # pehle header check karo, phir cookie
    token = None
    if credentials:
        token = credentials.credentials
    else:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    user = await user_auth_repository.find_by_id(user_id)

    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user