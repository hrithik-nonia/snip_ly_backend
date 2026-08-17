# built in imports
from pydantic import BaseModel, HttpUrl
from typing import Optional


# custom imports


class CreateLink(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None