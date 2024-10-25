from fastapi import Security, Response, APIRouter, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from app.config import access_security
from app.models.response_model import SuccessResponse, ErrorResponse
from app.models.request_model import Coordinates
from fastapi_jwt import JwtAuthorizationCredentials
from app.database import users_collection
from app.models.user_model import User
from app.config import cache, project_root

router = APIRouter()


@router.post("/coordinates", response_model=SuccessResponse)
async def set_coordinates(coordinates: Coordinates,
                          credentials: JwtAuthorizationCredentials = Security(access_security)):
    user_email = credentials.subject.get("email")
    user = await users_collection.find_one({"email": user_email})
    user = User(**user)
    user.coordinates = coordinates

    try:
        update_query = {"$set": user.dict()}
        result = await users_collection.update_one({"email": user_email}, update_query)

        # cache the coordinates to reduce database calls
        cache[user_email] = user.coordinates

        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=ErrorResponse(message="User not found or no changes were made").dict())
        return SuccessResponse(message="Successfully updated coordinates", data={"coordinates": user.coordinates})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=ErrorResponse(message="Unknown error", error=str(e)).dict())


templates = Jinja2Templates(directory=project_root / "templates")


@router.get("/homographic_transformation")
async def homograhpic_transormation(request: Request,
                                    credentials: JwtAuthorizationCredentials = Security(access_security)):
    websocket_url = request.url_for("websocket_homographic")

    return templates.TemplateResponse("example_frontend.html", context={"request": request, "websocket_url": websocket_url})
