# built in imports
from datetime import datetime, timezone


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



user_auth_repository = UserAuthRepo()