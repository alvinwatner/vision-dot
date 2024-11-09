from pydantic import BaseModel
import pydantic
from app.models.request_model import Coordinates
from typing import Optional
from app.config import password_context


class User(BaseModel):
    """
    Main user data, containing all data retrieved from database
    """
    # authentication purposes
    email: pydantic.EmailStr
    password: str

    # user information
    full_name: pydantic.constr(max_length=50)
    coordinates: Optional[Coordinates] = None

    # image dimensions
    image2d_width: Optional[int] = None
    image2d_height: Optional[int] = None    


class UserRegister(BaseModel):
    email: pydantic.EmailStr
    password: pydantic.constr(min_length=8)

    full_name: pydantic.constr(max_length=50)

    @pydantic.field_validator("password")
    @classmethod
    def hash_password(cls, value: str) -> str:
        return password_context.hash(value)


class UserLogin(BaseModel):
    email: pydantic.EmailStr
    password: str
