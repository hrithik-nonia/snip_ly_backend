# built in imports
from fastapi import APIRouter, Depends

# custom imports
from app.services.url_service.url_service import url_service
from app.models.url_model import CreateLink
from app.utils.security import get_optional_user



router = APIRouter(prefix="/url", tags=["URL Routes"])


@router.post("/short-url")
async def short_url(link_data: CreateLink, current_user: dict | None = Depends(get_optional_user)):
    user_id = current_user["user_id"] if current_user else None
    return await url_service.create_link(link_data, user_id)

