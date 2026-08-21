# built in imports
from fastapi import APIRouter, Depends

# custom imports
from app.services.url_service.url_service import url_service
from app.models.url_model import CreateLink, CreateUrlSchema
from app.utils.security import get_optional_user
from app.utils.dependencies import get_current_user


router = APIRouter(prefix="/url", tags=["URL Routes"])

# public short url route
@router.post("/short-url")
async def short_url(link_data: CreateLink, current_user: dict | None = Depends(get_optional_user)):
    user_id = current_user["user_id"] if current_user else None
    return await url_service.create_link(link_data, user_id)

@router.get("/home_stats_data")
async def home_stats_data():
    return await url_service.home_stats_data()

# private short url route
@router.post("/shorten")
async def create_short_url(data: CreateUrlSchema,
    current_user = Depends(get_current_user)
    ):
    user_id = str(current_user["_id"])
    return await url_service.create_short_url(data, user_id)

# get a specific users links and stats
@router.get("/get_user_data")
async def get_user_data(page: int = 1, limit: int = 5, search: str= "", current_user = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    return await url_service.get_user_links_data(user_id, page, limit, search)

# delete link
@router.delete("/delete")
async def delete_link(short_code: str, current_user = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    return await url_service.delete_link(user_id, short_code)


# get analytics page data
@router.get("/link_analytics")
async def get_link_analytics_data(short_code: str, current_user = Depends(get_current_user)):
    
    return await url_service.get_analytics_data( short_code)