# built in imports
from fastapi import APIRouter, status, Response, Request
from app.core.limiter import limiter


# custom imports
from app.models.user import CreateUser, RegisterResponse, VerifyOtp, UserBaseClass, UserResponse
from app.services.auth_service.auth_services import user_auth_services


router = APIRouter(prefix="/auth", tags=["Authentication"])


# user signup
@router.post("/sign-up", status_code= status.HTTP_200_OK, description="Creates a new user account.")
@limiter.limit("5/minute")
async def signup(user_data: CreateUser, request: Request):
  return await user_auth_services.user_signup(user_data)


# otp
@router.post("/otp", status_code= status.HTTP_200_OK, description="Verify Otp." , response_model= RegisterResponse)
@limiter.limit("5/minute")
async def otp(data: VerifyOtp, request: Request):
  return await user_auth_services.verify_otp(data.otp, data.email)

# login
@router.post("/login", status_code= status.HTTP_200_OK, description= "login", response_model= UserResponse)
@limiter.limit("10/minute")
async def login(login_data : UserBaseClass, response: Response, request: Request):
  return await user_auth_services.login(login_data, response)

# token retate
@router.post("/refresh")
@limiter.limit("20/minute")
async def refresh(request: Request, response: Response):
  refresh_token = request.cookies.get("refresh_token")
  return await user_auth_services.refresh(refresh_token ,response )


# logout
@router.post("/logout")
@limiter.limit("10/minute")
async def logout(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    return await user_auth_services.logout(refresh_token, response)