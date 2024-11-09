from fastapi import Security, Response, APIRouter, HTTPException, status
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessCookie
from app.config import app_config, password_context, access_security
from app.models.user_model import UserRegister, UserLogin, User
from app.database import users_collection
from app.models.response_model import ErrorResponse, SuccessResponse

router = APIRouter()

"""
Auth flow:
User register:
    1. check if email exists
    2. if doesn't exists, create the account
User login:
    1. check if both email and password is returning True
    2. else don't log them in
"""

"""
Registration can improved by sending an email verification first before actually registering the user
"""

"""
Flow: 
1. client logs in
2. backend sends access token
3. front end stores access token to local storage
4. frond end sends token with query params in /ws/homographic

Header key
Authorization: Bearer <token>
"""


def set_access_token_cookie(email: str, response: Response):
    access_token = access_security.create_access_token(subject={"email": email})
    access_security.set_access_cookie(response, access_token)


@router.post("/register", response_model=SuccessResponse)
async def register(user: UserRegister, response: Response):
    user_in_db = await users_collection.find_one({"email": user.email})
    if user_in_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=ErrorResponse(message="Email has already registered").dict())
    try:
        await users_collection.insert_one(user.dict())
        access_token = access_security.create_access_token(subject={"email": user.email})
        return SuccessResponse(message="User registered successfully", data={"access_token": access_token})

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=ErrorResponse(message="Unknown exception occurred", error=str(e)).dict())


@router.post("/login", response_model=SuccessResponse)
async def login(user: UserLogin, response: Response):
    user_in_db = await users_collection.find_one({"email": user.email})
    user_in_db = User(**user_in_db) if user_in_db else None

    if not user_in_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=ErrorResponse(message="Wrong email or password").dict())

    # secret is plain password, and hash is hashed password
    if not password_context.verify(secret=user.password, hash=user_in_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=ErrorResponse(message="Wrong email or password").dict())

    access_token = access_security.create_access_token(subject={"email": user.email})
    return SuccessResponse(message="User logged in", data={"access_token": access_token})


@router.get("/users/me")
def read_current_user(
        credentials: JwtAuthorizationCredentials = Security(access_security),
):
    return {"email": credentials.subject.get("email")}
