# built in imports
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Annotated
from datetime import datetime

# custom imports
from app.utils.helper_methods import helper_methods


class UserBaseClass(BaseModel):
  email : EmailStr
  password : Annotated[str, Field(min_length= 8 , max_length= 50)]

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
    id: str
    username: str
    email: str
    created_at: datetime

class RegisterResponse(BaseModel):
    success: bool
    message: str
    user: UserResponse


class UserStoreData(BaseModel):
   """ user data which is store in DB """
   email : EmailStr
   hashed_password : str
   created_at : datetime