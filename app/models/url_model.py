# built in imports
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


# custom imports


class CreateLink(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None

class ClickData:
    def __init__(
        self,
        short_code: str,
        ip: str,
        country: str,
        city: str,
        user_agent: Optional[str],
        referer: Optional[str],
        clicked_at: datetime,
    ):
        self.short_code = short_code
        self.ip = ip
        self.country = country
        self.city = city
        self.user_agent = user_agent
        self.referer = referer
        self.clicked_at = clicked_at

    def to_dict(self) -> dict:
        return {
            "short_code": self.short_code,
            "ip": self.ip,
            "country": self.country,
            "city": self.city,
            "user_agent": self.user_agent,
            "referer": self.referer,
            "clicked_at": self.clicked_at,
        }