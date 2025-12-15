from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.database import init_db
from app.routers import auth, users, messages
from app.socket_handlers import sio_app, start_background_tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await start_background_tasks()
    yield

fastapi_app = FastAPI(
    title="Real-Time Chat Application",
    version="1.0.0",
    lifespan=lifespan
)

fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
fastapi_app.include_router(users.router, prefix="/api/users", tags=["users"])
fastapi_app.include_router(messages.router, prefix="/api/messages", tags=["messages"])

@fastapi_app.get("/")
async def root():
    from fastapi.responses import FileResponse
    import os
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Real-Time Chat Application API", "ui": "/static/index.html"}

class SocketIOMiddleware:
    def __init__(self, app, socketio_app):
        self.app = app
        self.socketio_app = socketio_app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket") and scope["path"].startswith("/socket.io"):
            await self.socketio_app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

app = SocketIOMiddleware(fastapi_app, sio_app)

