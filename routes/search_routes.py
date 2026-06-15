from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from models.video import VideoResponse
from database.db import db
import re

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/", response_model=List[VideoResponse])
async def search_videos(
    q: Optional[str] = Query(None, description="Search term for title or description"),
    tags: Optional[str] = Query(None, description="Comma separated tags"),
    creator_id: Optional[str] = Query(None, description="Creator ID")
):
    query_filter: dict = {}
    
    if q:
        regex = re.compile(q, re.IGNORECASE)
        query_filter["$or"] = [{"title": regex}, {"description": regex}, {"creator_name": regex}]
        
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            if "$or" in query_filter:
                query_filter = {"$and": [query_filter, {"tags": {"$in": tag_list}}]}
            else:
                query_filter["tags"] = {"$in": tag_list}
                
    if creator_id:
        if "$and" in query_filter:
            query_filter["$and"].append({"creator_id": creator_id})
        else:
            query_filter["creator_id"] = creator_id
            
    cursor = db.videos.find(query_filter)
    videos = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc["creator_id"] = str(doc["creator_id"])
        videos.append(doc)
        
    return videos
