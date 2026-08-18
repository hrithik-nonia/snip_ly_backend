# built in imports
from fastapi import APIRouter

# custom imports
from app.services.url_service.url_service import url_service


router = APIRouter(tags=["Redirect Url"])

@router.get("/{short_code}")
async def redirect_url(short_code: str):
    return await url_service.redirect_url(short_code)