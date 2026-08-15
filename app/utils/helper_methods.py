# built in imports
from fastapi import HTTPException, status
import re

# custom imports


class HelperMethods:
  def email_validator(self , email: str)-> str | None:
    """ this method verifies formate of email """
    if not email:
            raise ValueError("Email is required")

    if "@" not in email:
        raise ValueError("Invalid email")

    if not re.search(r"[0-9]", email):
        raise ValueError("Email should contain at least one digit")

    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return email


  def password_validator(self, password: str)-> str | None:
    """ this method verifies password formate or strength """
    if not password:
            raise ValueError("Password is required")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")

    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one number")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")

    return password.strip()

  def name_validator(self, name: str)-> str | None:
    """ sirf spaces hai to error do ya space remove karke name return karo """
    name = name.strip()

    if not name:
        raise ValueError("Name is required")

    return name


helper_methods = HelperMethods()