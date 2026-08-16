# built in imports
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated
from datetime import datetime

# custom imports
from app.utils.helper_methods import helper_methods


class UserBaseClass(BaseModel):
  email : EmailStr
  password : str

  @field_validator("email")
  @classmethod
  def verify_email(cls, value: str)-> str | None:
    return helper_methods.email_validator(value)

  @field_validator("password")
  @classmethod
  def varify_password(cls, value: str)-> str | None:
    return helper_methods.password_validator(value)

class CreateUser(UserBaseClass):
  name : Annotated[str, Field(min_length= 1, max_length= 50)] 

  @field_validator("name")
  @classmethod
  def verify_name(cls, value: str)-> str | None:
    return helper_methods.name_validator(value)


class UserResponse(BaseModel):
    """ response after signup """
    id: str
    username: str
    email: str
    created_at: datetime
    access_token: str
    token_type: str
    

class RegisterResponse(BaseModel):
    """ response after register """
    success: bool
    message: str
    user_email: EmailStr 


class VerifyOtp(BaseModel):
    """ otp verify schema """
    otp: str
    email: str