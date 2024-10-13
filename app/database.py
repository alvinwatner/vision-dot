from pymongo import AsyncMongoClient
from app.config import app_config

client = AsyncMongoClient(app_config.database_uri)
database = client["Dot-Vision"]
users_collection = database["users"]
