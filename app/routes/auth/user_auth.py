# built in imports
from fastapi import APIRouter, status

# custom imports
from app.models.user import CreateUser, RegisterResponse
from app.services.auth_service.auth_services import user_auth_services


router = APIRouter(prefix="/auth", tags=["Authentication"])


# user signup
@router.post("/sign-up", status_code= status.HTTP_200_OK, description="Creates a new user account.")
async def signup(user_data: CreateUser):
  return await user_auth_services.user_signup(user_data)


# otp
@router.post("/otp", status_code= status.HTTP_200_OK, description="Verify Otp." , response_model= RegisterResponse)
async def otp(otp: str, email: str):
  return await user_auth_services.verify_otp(otp, email)
