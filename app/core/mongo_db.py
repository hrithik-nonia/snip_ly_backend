# built in imports
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# custom imports
MONGO_URL= os.getenv("MONGO_URL")
DB_NAME= os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGO_URL)
database = client[DB_NAME]

# collections
users_collection = database["users"]
otps_collection = database["otps"]
links_collection = database["links"]
clicks_collection = database["clicks"]