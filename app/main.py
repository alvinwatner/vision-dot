from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRoute
from app.api.websocket_routes import router as websocket_routes
from app.api.auth_routes import router as auth_routes
from app.api.http_routes import router as http_routes
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(websocket_routes)
app.include_router(auth_routes)
app.include_router(http_routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def check_registered_routes():
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"HTTP Route: {route.path}")
        else:
            print(f"WebSocket Route: {route.path}")


if __name__ == '__main__':
    check_registered_routes()
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get('PORT', 3001)))