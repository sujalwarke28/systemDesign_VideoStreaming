import asyncio
import sys
import os
from datetime import timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db import db
from bson import ObjectId

async def main():
    print("Starting created_at backfill...")
    cursor = db.videos.find()
    count = 0
    async for video in cursor:
        if "created_at" not in video:
            obj_id = video["_id"]
            created_at = obj_id.generation_time
            await db.videos.update_one(
                {"_id": obj_id},
                {"$set": {"created_at": created_at}}
            )
            count += 1
            print(f"Updated video {obj_id} with time {created_at}")
    print(f"Backfilled {count} videos.")

if __name__ == "__main__":
    asyncio.run(main())
