# built in imports


# custom imports
from app.core.mongo_db import links_collection


class UrlRepository:
    async def create_link(self, link_data_dict: dict) -> dict:
        result = await links_collection.insert_one(link_data_dict)
        return await links_collection.find_one({"_id": result.inserted_id})

    async def find_existing_link(self, original_url: str, user_id: str | None) -> dict | None:
        return await links_collection.find_one({
            "original_url": original_url,
            "user_id": user_id
        })
    


url_repository = UrlRepository()
