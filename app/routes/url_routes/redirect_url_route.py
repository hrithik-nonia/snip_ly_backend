# built in imports
from fastapi import APIRouter, Request

# custom imports
from app.services.url_service.url_service import url_service


router = APIRouter(tags=["Redirect Url"])

@router.get("/{short_code}")
async def redirect_url(short_code: str, request: Request):
    return await url_service.get_and_track(short_code, request)