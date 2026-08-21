# built in imports
from datetime import timezone, timedelta, datetime
import os
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from fastapi import Request, HTTPException, status


load_dotenv()

# custom imports
from app.repositories.url_repository.url_repository import url_repository
from app.models.url_model import CreateLink, CreateUrlSchema
from app.utils.shortcode import generate_short_code
from app.services.url_service.click_service import click_service
from app.repositories.url_repository.click_repository import click_repository


BASE_URL = os.getenv("BASE_URL")

class UrlService:
  def __init__(self):
    self.url_repo = url_repository
    self.click_repo = click_repository


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
    

  async def get_and_track(self, short_code: str, request: Request):
    url = await self.url_repo.find_by_url(short_code)

    if not url or not url["is_active"]:
        return RedirectResponse(url="http://localhost:5173/notFoundPage")

    # expiry check
    from datetime import datetime, timezone
    if url["expires_at"].replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return RedirectResponse(url="http://localhost:5173/linkExpiry410Page")

    # ✅ click track karo — asyncio se background mein chalao
    import asyncio
    asyncio.create_task(click_service.track_click(short_code, request))
    
    return RedirectResponse(url=url["original_url"])


  async def home_stats_data(self)-> dict:
     clicks = await self.click_repo.get_dashboard_stats()

     # links collection se - alag query
     total_links = await self.url_repo.total_links_count()

     return {
        "clicks": clicks,
        "total_links":total_links
     }

#   logged in user ke liya only
  async def create_short_url(self, data: CreateUrlSchema, user_id: str)-> dict:
    # custom alias check
    if data.custom_alias:
        existing = await self.url_repo.find_existing_alias(data.custom_alias)
        if existing:
            raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="Alias already taken")
        short_code = data.custom_alias
    else:
        short_code = generate_short_code()

    expires_at = datetime.now(timezone.utc) + timedelta(days=30)

    link_data_dict = {
       "user_id": user_id,
       "original_url": str(data.original_url),
       "short_code": short_code,
       "expires_at": expires_at,
       "created_at": datetime.now(timezone.utc),
       "is_active": True
    }

    await self.url_repo.create_link(link_data_dict)

    return {
        "success": True,
        "short_url": f"{BASE_URL}/{short_code}",
        "original_url": data.original_url,
        "expires_at": expires_at
    }


  async def get_user_links_data(self, user_id: str , page: int = 1, limit: int = 5, search: str="")->dict:
     if not user_id:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "User Not Found")
     
     stats_data = await self.url_repo.get_user_dashboard_stats(user_id)

     links = await self.url_repo.get_user_links(user_id , page, limit, search)
     
     return {
        "stats": stats_data,
        "links": links,
        "BASE_URL": BASE_URL
    }
url_service = UrlService()

  