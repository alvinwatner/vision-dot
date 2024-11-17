import json

from fastapi import WebSocket, status, WebSocketException, APIRouter, HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.models.request_model import FrameRequest
from app.config import logger, access_security, cache
from app.services.homographic_service import HomographicService
from app.models.request_model import Coordinates
from fastapi_jwt import JwtAuthorizationCredentials
from app.utils.cache_helpers import get_coordinates_in_cache_or_db

router = APIRouter()


async def proces_websocket_request(websocket: WebSocket, service: callable):
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
        result = service(validated_data.frame)
        await websocket.send_json({"result": result})


async def authenticate_websockets_with_jwt(authorization_header: str) -> JwtAuthorizationCredentials:
    authorization_scheme = "Bearer"
    if authorization_header.startswith(authorization_scheme):
        # get token from authorization bearer
        token = authorization_header.split()[-1]
    else:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token format")
        # creating an HTTP authorization credentials, because fastapi-jwt library works with HTTP headers
        # and not WebSocket
    http_credential = HTTPAuthorizationCredentials(scheme=authorization_scheme, credentials=token)

    try:
        credential = await access_security(bearer=http_credential)
        if not credential:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Invalid or expired token",
            )
        return credential
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=str(e))


@router.websocket("/ws/homographic", name="websocket_homographic")
async def homographic_websocket(websocket: WebSocket):
    access_token = websocket.headers.get("Authorization")
    credential = await authenticate_websockets_with_jwt(access_token)

    user_email = credential.subject.get("email")
    coordinates = await get_coordinates_in_cache_or_db(email=user_email)

    homographic_service = HomographicService(coordinates=coordinates)
    await proces_websocket_request(websocket, homographic_service.execute)


@router.websocket("/ws")
async def hello(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello World")
