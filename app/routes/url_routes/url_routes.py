# built in imports
from fastapi import APIRouter

# custom imports
from app.services.url_service.url_service import url_service
from app.models.url_model import CreateLink



router = APIRouter(prefix="/url", tags=["URL Routes"])


@router.post("/short-url")
async def short_url(link_data: CreateLink):
    return await url_service.create_link(link_data)