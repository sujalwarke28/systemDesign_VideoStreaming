from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "videostreaming"

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]

async def create_indexes():
    # Users
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    
    # Videos
    await db.videos.create_index("title")
    await db.videos.create_index("creator_id")
    await db.videos.create_index("tags")
    
    # Comments & Likes
    await db.comments.create_index("video_id")
    await db.likes.create_index([("video_id", 1), ("user_id", 1)], unique=True)
    
    # Playlist & History
    await db.playlists.create_index("user_id")
    await db.watch_history.create_index("user_id")
