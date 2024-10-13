from pydantic import BaseModel


# standardizing the response from the server to make it easier to render in the front end

class SuccessResponse(BaseModel):
    message: str
    data: dict


class ErrorResponse(BaseModel):
    message: str
    error: str = ""
