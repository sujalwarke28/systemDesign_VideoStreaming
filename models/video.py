from pydantic import BaseModel, Field
from typing import Optional, List
from models.common import PyObjectId
from datetime import datetime, timezone

def get_utc_now():
    return datetime.now(timezone.utc)

class Video(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    description: str
    cloudfront_url: str
    thumbnail_url: Optional[str] = None
    creator_id: PyObjectId
    creator_name: str = "Unknown User"
    tags: List[str] = []
    views: int = 0
    created_at: datetime = Field(default_factory=get_utc_now)

class VideoCreate(BaseModel):
    title: str
    description: str
    tags: List[str] = []

class VideoResponse(BaseModel):
    id: str
    title: str
    description: str
    cloudfront_url: str
    thumbnail_url: Optional[str] = None
    creator_id: str
    creator_name: str = "Unknown User"
    tags: List[str]
    views: int
    created_at: datetime
