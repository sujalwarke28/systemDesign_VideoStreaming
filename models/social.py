from pydantic import BaseModel, Field
from typing import Optional, List
from models.common import PyObjectId
from datetime import datetime, timezone

def get_utc_now():
    return datetime.now(timezone.utc)

class Comment(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    video_id: PyObjectId
    user_id: PyObjectId
    text: str
    created_at: datetime = Field(default_factory=get_utc_now)

class Like(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    video_id: PyObjectId
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=get_utc_now)

class Playlist(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    user_id: PyObjectId
    video_ids: List[PyObjectId] = []
    created_at: datetime = Field(default_factory=get_utc_now)

class WatchHistory(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    video_id: PyObjectId
    watched_at: datetime = Field(default_factory=get_utc_now)
