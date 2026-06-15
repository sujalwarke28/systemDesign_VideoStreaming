from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Video Streaming Platform API",
    description="Backend API for YouTube-like video streaming platform",
    version="1.0.0"
)

# CORS Setup
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:8501"),
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from database.db import create_indexes
from routes import auth_routes, video_routes, search_routes, social_routes, playlist_routes, frontend_routes
from fastapi.staticfiles import StaticFiles

@app.on_event("startup")
async def startup_db_client():
    await create_indexes()

app.mount("/static", StaticFiles(directory="static"), name="static")
import os
os.makedirs("uploads/thumbnails", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_routes.router)
app.include_router(video_routes.router)
app.include_router(search_routes.router)
app.include_router(social_routes.router)
app.include_router(playlist_routes.router)
app.include_router(frontend_routes.router)

