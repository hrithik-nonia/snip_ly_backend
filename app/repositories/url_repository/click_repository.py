# built in imports


# custom imports
from app.core.mongo_db import clicks_collection

class ClickRepository:
  async def insert_click(self, click_dict: dict) -> None:
        await clicks_collection.insert_one(click_dict)


  async def get_dashboard_stats(self) -> dict:
    """ iss method se home page ka stats data milega """
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_clicks": {"$sum": 1},
                "unique_countries": {"$addToSet": "$country"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_clicks": 1,
                "unique_country_count": {"$size": "$unique_countries"}
            }
        }
    ]

    result = await clicks_collection.aggregate(pipeline).to_list(length=None)
    clicks_data = result[0] if result else {"total_clicks": 0, "unique_country_count": 0}

    return {
        "total_clicks": clicks_data["total_clicks"],
        "countries_reached": clicks_data["unique_country_count"],
    }

  


click_repository = ClickRepository()