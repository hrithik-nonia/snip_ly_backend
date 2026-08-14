# built in imports
from fastapi import HTTPException, status
import re

# custom imports


class HelperMethods:
  def email_validator(self , email: str)-> str | None:
    """ this method verifies formate of email """
    if not email : 
      raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_CONTENT , detail= ["Email Required"]) 

    if "@" not in email :
      raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= ["Invalid Email"])

    if not re.search(r"[0-9]", email):
       raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_CONTENT, detail= ["Email Should Contain At Least One Digit"])

    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    if not re.match(pattern, email):
      raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail= ["Invalid Email Formate"])
    return email


  def password_validator(self, password: str)-> str | None:
    """ this method verifies password formate or strength """
    if not password :
      raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_CONTENT, detail= ["Password Is Required"])

    if len(password) < 8:
      raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_CONTENT, detail= ["Password Must Be 8 Character Or Larger"])

    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    
    if not re.search(r"[0-9]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")

    password = password.strip()
    return password

  def name_validator(self, name: str)-> str | None:
    """ sirf spaces hai to error do ya space remove karke name return karo """
    name = name.strip()
  
    if not name :
       raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_CONTENT, detail= ["Name Is Required"])

    return name
       


helper_methods = HelperMethods()