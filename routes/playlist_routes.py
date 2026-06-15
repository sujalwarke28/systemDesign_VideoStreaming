from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User
from models.social import Playlist, WatchHistory
from models.video import VideoResponse
from routes.auth_routes import get_current_user
from database.db import db
from typing import List
from bson import ObjectId

router = APIRouter(prefix="/playlists", tags=["Playlists & History"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_playlist(name: str, current_user: User = Depends(get_current_user)):
    new_playlist = Playlist(name=name, user_id=str(current_user.id))
    result = await db.playlists.insert_one(new_playlist.model_dump(by_alias=True, exclude_none=True))
    playlist = await db.playlists.find_one({"_id": result.inserted_id})
    if not playlist:
        raise HTTPException(status_code=500, detail="Failed to create playlist")
    playlist["id"] = str(playlist["_id"])
    return playlist

@router.get("/")
async def get_my_playlists(current_user: User = Depends(get_current_user)):
    cursor = db.playlists.find({"user_id": str(current_user.id)})
    playlists = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        playlists.append(doc)
    return playlists

@router.post("/{playlist_id}/videos/{video_id}")
async def add_video_to_playlist(playlist_id: str, video_id: str, current_user: User = Depends(get_current_user)):
    try:
        p_id = ObjectId(playlist_id)
        v_id = ObjectId(video_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid IDs")
        
    playlist = await db.playlists.find_one({"_id": p_id, "user_id": str(current_user.id)})
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
        
    video = await db.videos.find_one({"_id": v_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    if str(v_id) not in playlist.get("video_ids", []):
        await db.playlists.update_one({"_id": p_id}, {"$push": {"video_ids": str(v_id)}})
        return {"detail": "Video added to playlist"}
    return {"detail": "Video already in playlist"}

@router.post("/history/{video_id}")
async def record_watch_history(video_id: str, current_user: User = Depends(get_current_user)):
    try:
        v_id = ObjectId(video_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid video ID")
        
    history = WatchHistory(user_id=str(current_user.id), video_id=str(v_id))
    await db.watch_history.insert_one(history.model_dump(by_alias=True, exclude_none=True))
    return {"detail": "History recorded"}

@router.get("/history", response_model=List[VideoResponse])
async def get_watch_history(current_user: User = Depends(get_current_user)):
    cursor = db.watch_history.find({"user_id": str(current_user.id)}).sort("watched_at", -1)
    
    video_ids = []
    async for doc in cursor:
        try:
            video_ids.append(ObjectId(doc["video_id"]))
        except:
            pass
            
    if not video_ids:
        return []
        
    videos_cursor = db.videos.find({"_id": {"$in": video_ids}})
    video_dict = {}
    async for v in videos_cursor:
        v["id"] = str(v["_id"])
        v["creator_id"] = str(v["creator_id"])
        video_dict[v["id"]] = v
        
    result = []
    seen = set()
    for vid in video_ids:
        vid_str = str(vid)
        if vid_str not in seen and vid_str in video_dict:
            result.append(video_dict[vid_str])
            seen.add(vid_str)
            
    return result
