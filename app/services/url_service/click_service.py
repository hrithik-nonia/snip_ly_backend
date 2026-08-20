# built in imports
import httpx
from datetime import datetime, timezone
from fastapi import Request
from bson import ObjectId


# custom imports
from app.repositories.url_repository.click_repository import click_repository
from app.models.url_model import ClickData
from app.core.mongo_db import links_collection


class ClickService:
    def __init__(self):
        self.click_repo = click_repository

    async def get_location(self, ip: str) -> dict:
        # local IP handle
        if ip in ("127.0.0.1", "::1") or ip.startswith("192.168"):
            return {"country": "Local", "city": "Local"}

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"http://ip-api.com/json/{ip}",
                    timeout=3.0  # zyada wait mat karo
                )
                data = res.json()

            if data["status"] == "success":
                return {
                    "country": data["country"],
                    "city": data["city"],
                }
        except Exception:
            pass

        return {"country": "Unknown", "city": "Unknown"}

    async def track_click(self, short_code: str, request: Request) -> None:
        ip = request.client.host
        user_agent = request.headers.get("user-agent")
        referer = request.headers.get("referer")

        location = await self.get_location(ip)

        # link banane wale ka user_id nikalo
        link = await links_collection.find_one({"short_code": short_code})
        user_id = link["user_id"] if link else None

        click = ClickData(
            user_id= user_id,
            short_code=short_code,
            ip=ip,
            country=location["country"],
            city=location["city"],
            user_agent=user_agent,
            referer=referer,
            clicked_at=datetime.now(timezone.utc),
        )

        await self.click_repo.insert_click(click.to_dict())


click_service = ClickService()