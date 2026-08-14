# built in imports
from fastapi import HTTPException, status
from datetime import datetime, timezone

# built in imports
from app.models.user import CreateUser, UserStoreData
from app.repositories.auth_repo.user_auth_repository import user_auth_repository
from app.utils.security import hash_password, verify_password
from app.core.email import generate_otp, send_otp



class UserAuthServices:
  def __init__(self):
    self.user_auth_repo = user_auth_repository
  
  async def user_signup(self , user_data: CreateUser )-> dict :
    """ password hashing, otp sending task do in this method """
    # email already registered hai?
    existing_user = await self.user_auth_repo.find_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # pending OTP already hai?
    existing_otp = await self.user_auth_repo.find_pending_otp(user_data.email)
    if existing_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP already sent. Check your email."
        )

    # password hash
    hashed_password = await hash_password(user_data.password)

    # gen otp
    otp = generate_otp()

    # temporary save karo
    await self.user_auth_repo.save_temp_user(
        email=user_data.email,
        otp=otp,
        hashed_password=hashed_password
    )

    # email bhejo
    await send_otp(user_data.email, otp)  

    return {
        "success": True,
        "message": "OTP sent to your email. Verify to complete signup."
    }


  async def verify_otp(self, otp: str, email: str)-> dict | None:
    """ otp verify karega aur sign up confirm karega """
    # temp user find
    temp_user = await self.user_auth_repo.find_pending_otp(email)

    if not temp_user:
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail="OTP expired or invalid. Please signup again."
      )

    # OTP match karo
    if temp_user["otp"] != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong OTP. Please try again."
        )

    # permanent save karo
    created_user = await self.user_auth_repo.create_user(
        email=temp_user["email"],
        hashed_password=temp_user["hashed_password"]
    )

    # temp delete karo
    await self.user_auth_repo.delete_temp_user(email)

    return {
      "success": True,
      "message": "Account verified successfully.",
      "user": {
          "id": str(created_user["_id"]),
          "email": created_user["email"],
          "username": created_user.get("username", ""),
          "created_at": created_user["created_at"]
      }
    }

user_auth_services = UserAuthServices()