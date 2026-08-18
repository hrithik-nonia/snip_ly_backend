# built in imports


# custom imports
from app.core.mongo_db import clicks_collection

class ClickRepository:
  async def insert_click(self, click_dict: dict) -> None:
        await clicks_collection.insert_one(click_dict)

  async def get_clicks_by_short_code(self, short_code: str) -> list:
        cursor = clicks_collection.find({"short_code": short_code})
        return await cursor.to_list(length=None)

  async def get_click_count(self, short_code: str) -> int:
        return await clicks_collection.count_documents({"short_code": short_code})


click_repository = ClickRepository()