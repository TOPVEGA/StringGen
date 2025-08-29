from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI

mongo = AsyncIOMotorClient(MONGO_URI)
db = mongo.sessionbuilder

# User collection
users = db.users
