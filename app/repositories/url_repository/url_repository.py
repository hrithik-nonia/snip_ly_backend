# built in imports
from math import ceil


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


    # get links with pagination
    async def get_user_links(self, user_id: str, page: int = 1, limit: int = 5, search: str = "") -> dict:
        skip = (page - 1) * limit  # page 1 → skip 0, page 2 → skip 5

        # for search feature
        search_filter = {"user_id": user_id}
        if search:
            search_filter["$or"] = [
                {"original_url": {"$regex": search, "$options": "i"}},
                {"short_code": {"$regex": search, "$options": "i"}},
            ]

        total_count = await links_collection.count_documents(search_filter)

        pipeline = [
            # Step 1: sirf is user ke links
            {"$match": search_filter},

            # Step 2: clicks collection se join karo short_code pe
            {"$lookup": {
                "from": "clicks",
                "localField": "short_code",
                "foreignField": "short_code",
                "as": "click_data"
            }},

            # Step 3: click_data array ki size = total clicks
            {"$addFields": {
                "clicks": {"$size": "$click_data"}
            }},

            # Step 4: click_data remove karo
            {"$project": {"click_data": 0}},

            # Step 5: pagination
            {"$skip": skip},
            {"$limit": limit},
        ]

        links = await links_collection.aggregate(pipeline).to_list(length=None)

        # ObjectId → string
        for link in links:
            link["_id"] = str(link["_id"])
            if link.get("user_id"):
                link["user_id"] = str(link["user_id"])

        return {"links": links}


    # delete link
    async def delete_link(self, short_code: str)-> dict | None:
        delete_from_link_collection = await links_collection.delete_one({"short_code": short_code})

        await clicks_collection.delete_many({"short_code": short_code})

        if delete_from_link_collection.deleted_count == 0:
            return None  # link mila hi nahi
        
        return {"message": "Link deleted successfully",
                "short_code": short_code
                }


url_repository = UrlRepository()
