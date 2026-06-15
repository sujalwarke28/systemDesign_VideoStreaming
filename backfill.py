import asyncio
import sys
import os

# Ensure we can import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import db
from bson import ObjectId

async def main():
    print("Starting backfill...")
    cursor = db.videos.find()
    count = 0
    async for video in cursor:
        if "creator_name" not in video:
            try:
                user = await db.users.find_one({"_id": ObjectId(video["creator_id"])})
                if user:
                    await db.videos.update_one(
                        {"_id": video["_id"]},
                        {"$set": {"creator_name": user["username"]}}
                    )
                    count += 1
            except Exception as e:
                print(f"Error updating video {video['_id']}: {e}")
    print(f"Backfilled {count} videos.")

if __name__ == "__main__":
    asyncio.run(main())
