# built in imports
from datetime import timezone, timedelta, datetime
import os
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse

load_dotenv()

# custom imports
from app.repositories.url_repository.url_repository import url_repository
from app.models.url_model import CreateLink
from app.utils.shortcode import generate_short_code


BASE_URL = os.getenv("BASE_URL")

class UrlService:
  def __init__(self):
    self.url_repo = url_repository


  async def create_link(self, link_data: CreateLink, user_id: str | None = None) -> dict:

    original_url = str(link_data.original_url)

    # already exist karta hai?
    existing = await self.url_repo.find_existing_link(original_url, user_id)
    if existing:
        return {
            "success": True,
            "short_url": f"{BASE_URL}/{existing['short_code']}",
            "original_url": original_url,
            "expires_at": existing["expires_at"]
        }

    # expiry set karo
    if user_id:
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    short_code = generate_short_code()

    link_data_dict = {
        "user_id": user_id if user_id else None,
        "original_url": original_url,
        "short_code": short_code,
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc),
        "is_active": True
      }

    await self.url_repo.create_link(link_data_dict)

    return {
        "success": True,
        "short_url": f"{BASE_URL}/{short_code}",
        "original_url": original_url,
        "expires_at": expires_at
    }
    

  async def redirect_url(self, short_code: str):
    url = await self.url_repo.find_by_url(short_code)

    if not url or not url["is_active"]:
        return RedirectResponse(url="http://localhost:5173/notFoundPage")

    # expiry check
    from datetime import datetime, timezone
    if url["expires_at"].replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return RedirectResponse(url="http://localhost:5173/linkExpiry410Page")

    return RedirectResponse(url=url["original_url"])
   
     
url_service = UrlService()

  