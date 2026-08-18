# built in imports
from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError, JWSError
import os
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

load_dotenv()

# custom imports

# PasswordHash ka instance banaya
password_hash = PasswordHash.recommended()

async def hash_password(password: str)-> str:
  hashed_password = password_hash.hash(password)
  return hashed_password

async def verify_password(original_password: str, hashed_password: str)-> bool:
  return password_hash.verify(original_password, hashed_password)

# --- Token helpers ---
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(  # ← None ki jagah exception raise karo
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


# ======= token dependency=============
bearer_scheme = HTTPBearer()  # token ko read karne ke liya

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
   token = credentials.credentials
   try:
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # payload nikala isme user id v set kiya tha
      user_id: str = payload.get("sub")  # payload se user id nikala 
      if not user_id:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
      return {"user_id": user_id}

   except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))) -> dict | None:
    if not credentials:
        return None
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        return {"user_id": user_id}
    except:
        return None
    