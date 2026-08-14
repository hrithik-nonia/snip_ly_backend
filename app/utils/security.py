# built in imports
from pwdlib import PasswordHash

# custom imports

# PasswordHash ka instance banaya
password_hash = PasswordHash.recommended()

async def hash_password(password: str)-> str:
  hashed_password = password_hash.hash(password)
  return hashed_password

async def verify_password(original_password: str, hashed_password: str)-> bool:
  return password_hash.verify(original_password, hashed_password)