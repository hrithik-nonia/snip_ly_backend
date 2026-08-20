# built in imports
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


# custom imports


class CreateLink(BaseModel):
    original_url: HttpUrl

class ClickData:
    def __init__(
        self,
        user_id: ObjectId,
        short_code: str,
        ip: str,
        country: str,
        city: str,
        user_agent: Optional[str],
        referer: Optional[str],
        clicked_at: datetime,
    ):
        self.user_id = user_id
        self.short_code = short_code
        self.ip = ip
        self.country = country
        self.city = city
        self.user_agent = user_agent
        self.referer = referer
        self.clicked_at = clicked_at

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "short_code": self.short_code,
            "ip": self.ip,
            "country": self.country,
            "city": self.city,
            "user_agent": self.user_agent,
            "referer": self.referer,
            "clicked_at": self.clicked_at,
        }


class CreateUrlSchema(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9-_]+$"  
    )