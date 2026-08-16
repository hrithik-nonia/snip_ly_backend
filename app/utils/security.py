# built in imports
from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
from jose import jwt
import os
from dotenv import load_dotenv

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