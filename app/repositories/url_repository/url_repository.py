# built in imports
from math import ceil
from datetime import datetime, timezone, timedelta


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


    # get link by short code
    async def get_link_analytics(self, short_code: str) -> dict | None:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

        pipeline = [
            # Step 1: link dhundo
            {"$match": {"short_code": short_code}},

            # Step 2: clicks join karo
            {"$lookup": {
                "from": "clicks",
                "localField": "short_code",
                "foreignField": "short_code",
                "as": "click_data"
            }},

            # Step 3: sab calculate karo
            {"$addFields": {

                # total clicks
                "total_clicks": {"$size": "$click_data"},

                # todays clicks
                "todays_clicks": {
                    "$size": {
                        "$filter": {
                            "input": "$click_data",
                            "as": "click",
                            "cond": {"$gte": ["$$click.clicked_at", today_start]}
                        }
                    }
                },

                # unique visitors — distinct IPs
                "unique_visitors": {
                    "$size": {"$setUnion": "$click_data.ip"}
                },

                # top countries
                "top_countries": {
                    "$reduce": {
                        "input": "$click_data",
                        "initialValue": [],
                        "in": {
                            "$let": {
                                "vars": {
                                    "country": "$$this.country",
                                    "arr": "$$value"
                                },
                                "in": {
                                    "$cond": {
                                        "if": {"$in": ["$$country", "$$arr.country"]},
                                        "then": {
                                            "$map": {
                                                "input": "$$arr",
                                                "as": "item",
                                                "in": {
                                                    "$cond": {
                                                        "if": {"$eq": ["$$item.country", "$$country"]},
                                                        "then": {
                                                            "country": "$$item.country",
                                                            "count": {"$add": ["$$item.count", 1]}
                                                        },
                                                        "else": "$$item"
                                                    }
                                                }
                                            }
                                        },
                                        "else": {
                                            "$concatArrays": [
                                                "$$arr",
                                                [{"country": "$$country", "count": 1}]
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    }
                },

                # device breakdown
                "device_breakdown": {
                    "$reduce": {
                        "input": "$click_data",
                        "initialValue": {"Mobile": 0, "Tablet": 0, "Desktop": 0},
                        "in": {
                            "$let": {
                                "vars": {
                                    "device": {
                                        "$switch": {
                                            "branches": [
                                                {
                                                    "case": {"$regexMatch": {
                                                        "input": "$$this.user_agent",
                                                        "regex": "Mobile|Android",
                                                        "options": "i"
                                                    }},
                                                    "then": "Mobile"
                                                },
                                                {
                                                    "case": {"$regexMatch": {
                                                        "input": "$$this.user_agent",
                                                        "regex": "iPad|Tablet",
                                                        "options": "i"
                                                    }},
                                                    "then": "Tablet"
                                                }
                                            ],
                                            "default": "Desktop"
                                        }
                                    }
                                },
                                "in": {
                                    "Mobile": {
                                        "$cond": [{"$eq": ["$$device", "Mobile"]},
                                            {"$add": ["$$value.Mobile", 1]}, "$$value.Mobile"]
                                    },
                                    "Tablet": {
                                        "$cond": [{"$eq": ["$$device", "Tablet"]},
                                            {"$add": ["$$value.Tablet", 1]}, "$$value.Tablet"]
                                    },
                                    "Desktop": {
                                        "$cond": [{"$eq": ["$$device", "Desktop"]},
                                            {"$add": ["$$value.Desktop", 1]}, "$$value.Desktop"]
                                    },
                                }
                            }
                        }
                    }
                },

                # recent clicks — last 10
                "recent_clicks": {
                    "$slice": [
                        {"$sortArray": {
                            "input": "$click_data",
                            "sortBy": {"clicked_at": -1}
                        }},
                        10
                    ]
                },

                # clicks over time — last 30 days
                "clicks_over_time": {
                    "$filter": {
                        "input": "$click_data",
                        "as": "click",
                        "cond": {"$gte": ["$$click.clicked_at", thirty_days_ago]}
                    }
                },
            }},

            # Step 4: click_data remove karo
            {"$project": {"click_data": 0}},
        ]

        result = await links_collection.aggregate(pipeline).to_list(length=1)

        if not result:
            return None

        link = result[0]
        link["_id"] = str(link["_id"])
        if link.get("user_id"):
            link["user_id"] = str(link["user_id"])

        # recent_clicks convert
        for click in link.get("recent_clicks", []):
            click["_id"] = str(click["_id"])
            if click.get("user_id"):
                click["user_id"] = str(click["user_id"])

        # clicks_over_time convert — yeh missing tha
        for click in link.get("clicks_over_time", []):
            click["_id"] = str(click["_id"])
            if click.get("user_id"):
                click["user_id"] = str(click["user_id"])

        return link


url_repository = UrlRepository()
