from app.models.request_model import Coordinates
from app.models.user_model import User
from app.config import cache
from app.database import users_collection


async def get_coordinates_in_cache_or_db(email: str):
    coordinates = cache.get(email)
    if coordinates is not None:
        return coordinates
    user = await users_collection.find_one({"email": email})
    user = User(**user)
    if user.coordinates is not None:
        return user.coordinates
    raise ValueError("User coordinates are not set. Try to set them first.")
