import json

from app.models.user_model import User
from fastapi import WebSocket, status, WebSocketException, APIRouter, HTTPException
from app.models.request_model import FrameRequest
from app.config import logger, access_security, cache
from app.services.homographic_service import HomographicService
from app.models.request_model import Coordinates
from fastapi_jwt import JwtAuthorizationCredentials
from app.database import users_collection
from app.utils.cache_helpers import get_coordinates_in_cache_or_db

router = APIRouter()


async def proces_websocket_request(websocket: WebSocket, service: callable, email: str):
    """"
    params:
        websocket: WebSocket object to receive websocket connection
        service: a function to call in order to fulfill a request

    It will take a base64 encoded string with key of "frame" and send that frame to other specific service
    """
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        try:
            validated_data = FrameRequest(**data)
        except Exception as e:
            logger.error(f"error happened: {e}")
            raise WebSocketException(code=status.WS_1003_UNSUPPORTED_DATA, reason=f"Error occurred: {e}")
        

        # Retrieve user data from the database or cache
        user_data = await users_collection.find_one({"email": email})
        if not user_data:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")

        user = User(**user_data)

        result = service(validated_data.frame)
        
        # Access image2d_width and image2d_height from the user model
        image2d_width = user.image2d_width
        image2d_height = user.image2d_height
        
        await websocket.send_json({
            "result": result,
            "image2d_width": image2d_width,
            "image2d_height": image2d_height
        })

@router.websocket("/ws/homographic", name="websocket_homographic")
async def homographic_websocket(websocket: WebSocket):
    # try:
    #     authorization_token = websocket.headers.get("Authorization")

    #     # get the token in last section
    #     access_token = authorization_token.split()[-1]
    #     credential: JwtAuthorizationCredentials = await access_security(access_token)
    # except Exception as e:
    #     logger.error(f"error happened: {e}")
    #     await websocket.close(code=1008)
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    # user_email = credential.subject.get("email")
    user_email = 'alvin2phantomhive@gmail.com'
    coordinates = await get_coordinates_in_cache_or_db(email=user_email)

    homographic_service = HomographicService(coordinates=coordinates)
    await proces_websocket_request(websocket, homographic_service.execute, user_email)


@router.websocket("/ws")
async def hello(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello World")
