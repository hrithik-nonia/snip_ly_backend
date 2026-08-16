# built in imports
from fastapi import HTTPException, status, Response

# built in imports
from app.models.user import CreateUser, UserBaseClass
from app.repositories.auth_repo.user_auth_repository import user_auth_repository
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
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
        name = user_data.name,
        email=user_data.email,
        otp=otp,
        hashed_password=hashed_password
    )

    # email bhejo
    await send_otp(user_data.email, otp)  

    return {
        "success": True,
        "message": "OTP sent to your email. Verify to complete signup.",
        "email": user_data.email
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
        name = temp_user["name"],
        email=temp_user["email"],
        hashed_password=temp_user["hashed_password"]
    )

    # temp delete karo
    await self.user_auth_repo.delete_temp_user(email)

    return {
      "success": True,
      "message": "Account verified successfully.",
      "user_email": created_user["email"]
    }


  async def login(self, login_data: UserBaseClass, response: Response)-> dict:
    """ user login service """
    existing_user =  await self.user_auth_repo.find_by_email(login_data.email)

    if not existing_user :
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "User Does Not Exist")

    is_password_metch = await verify_password(login_data.password, existing_user["hashed_password"])

    if not is_password_metch:
       raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail= "Wrong Password")

    # Token payload
    token_data = {"sub": str(existing_user["_id"]), "email": existing_user["email"]}

    # create tokens
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # 5. Refresh token → HttpOnly cookie mein daal do
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,        # JS se access nahi hoga (XSS safe)
        secure=True,          # Sirf HTTPS pe jayega
        samesite="lax",       # CSRF protection
        max_age=60 * 60 * 24 * 7,  # 7 din (seconds mein)
        path="/auth/refresh"  # Sirf refresh endpoint pe jayega
    )

    # 6. Access token → response body mein bhejo
    return {
        "id":str(existing_user["_id"]),
        "username": existing_user["name"],
        "email": existing_user["email"],
        "created_at": existing_user["created_at"],
        "access_token": access_token,
        "token_type": "bearer"

    }
    

user_auth_services = UserAuthServices()