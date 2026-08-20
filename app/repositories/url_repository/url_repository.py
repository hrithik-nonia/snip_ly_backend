# built in imports


# custom imports
from app.core.mongo_db import links_collection, clicks_collection


class UrlRepository:
    # create url
    async def create_link(self, link_data_dict: dict) -> dict:
        result = await links_collection.insert_one(link_data_dict)
        return await links_collection.find_one({"_id": result.inserted_id})

    # find existing original links
    async def find_existing_link(self, original_url: str, user_id: str | None) -> dict | None:
        return await links_collection.find_one({
            "original_url": original_url,
            "user_id": user_id
        })

    # find by short code
    async def find_by_url(self, short_code: str):
        return await links_collection.find_one({"short_code": short_code})

    # count total links
    async def total_links_count(self)-> int:
        return await links_collection.count_documents({})

    # find alias
    async def find_existing_alias(self, alias: str):
        return await links_collection.find_one({"short_code": alias})

    # user dashboard stats
    async def get_user_dashboard_stats(self, user_id: str) -> dict:
        """ user ke dashboard ka data deta hai """
        # total links
        total_links = await links_collection.count_documents({"user_id": user_id})
    
        # active links
        active_links = await links_collection.count_documents({
            "user_id": user_id,
            "is_active": True
        })
    
        # total clicks
        total_clicks = await clicks_collection.count_documents({"user_id": user_id})

        return {
            "total_links": total_links,
            "active_links": active_links,
            "total_clicks": total_clicks,
        }
    
    


url_repository = UrlRepository()
