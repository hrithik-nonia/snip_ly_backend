# built in imports
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from bson.errors import InvalidId

# custom imports
from app.core.mongo_db import users_collection, otps_collection

class UserAuthRepo:
  async def find_by_email(self, email: str):
    """ find user from users collection """
    return await users_collection.find_one({"email" : email})

  async def find_pending_otp(self, email: str):
    """ find otp from otps collection """
    return await otps_collection.find_one({"email" : email})


  async def save_temp_user(self, email: str, otp: str, hashed_password: str, name : str):
    """ save temperary user data """
    await otps_collection.insert_one({
        "name": name,
        "email": email,
        "otp": otp,
        "hashed_password": hashed_password,
        "created_at": datetime.now(timezone.utc)
      })

  
  # OTP verify hone ke baad permanent save
  async def create_user(self, email: str, hashed_password: str, name: str):
    result = await users_collection.insert_one({
        "name": name,
        "email": email,
        "hashed_password": hashed_password,
        "created_at": datetime.now(timezone.utc)
    })
    return await users_collection.find_one({"_id": result.inserted_id})


  # OTP verify hone ke baad temp delete karo
  async def delete_temp_user(self, email: str):
    await otps_collection.delete_one({"email": email})


  async def find_by_id(self, user_id: str) -> Optional[dict]:
      try:
          user = await users_collection.find_one({"_id": ObjectId(user_id)})
          return user
      except InvalidId:
          return None

  # set refresh token 
  async def update_refresh_token(self, user_id: str, refresh_token: str) -> None:
      await users_collection.update_one(
          {"_id": ObjectId(user_id)},
          {"$set": {"refresh_token": refresh_token}}
      )



user_auth_repository = UserAuthRepo()