from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User
from models.social import Comment, Like
from models.video import VideoResponse
from routes.auth_routes import get_current_user
from database.db import db
from typing import List
from bson import ObjectId

router = APIRouter(prefix="/social", tags=["Social"])

@router.post("/videos/{video_id}/like")
async def toggle_like(video_id: str, current_user: User = Depends(get_current_user)):
    try:
        obj_id = ObjectId(video_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid video ID")
        
    video = await db.videos.find_one({"_id": obj_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    existing_like = await db.likes.find_one({
        "video_id": str(obj_id),
        "user_id": str(current_user.id)
    })
    
    if existing_like:
        await db.likes.delete_one({"_id": existing_like["_id"]})
        return {"detail": "Video unliked"}
    else:
        new_like = Like(video_id=str(obj_id), user_id=str(current_user.id))
        await db.likes.insert_one(new_like.model_dump(by_alias=True, exclude_none=True))
        return {"detail": "Video liked"}

@router.get("/videos/{video_id}/likes/count")
async def count_likes(video_id: str):
    count = await db.likes.count_documents({"video_id": video_id})
    return {"likes": count}

@router.post("/videos/{video_id}/comments")
async def add_comment(video_id: str, text: str, current_user: User = Depends(get_current_user)):
    try:
        obj_id = ObjectId(video_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid video ID")
        
    video = await db.videos.find_one({"_id": obj_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    new_comment = Comment(video_id=str(obj_id), user_id=str(current_user.id), text=text)
    result = await db.comments.insert_one(new_comment.model_dump(by_alias=True, exclude_none=True))
    
    comment = await db.comments.find_one({"_id": result.inserted_id})
    if not comment:
        raise HTTPException(status_code=500, detail="Failed to create comment")
    comment["id"] = str(comment["_id"])
    del comment["_id"]
    return comment

@router.get("/videos/{video_id}/comments")
async def get_comments(video_id: str):
    cursor = db.comments.find({"video_id": video_id}).sort("created_at", -1)
    comments = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        comments.append(doc)
    return comments

@router.get("/liked", response_model=List[VideoResponse])
async def get_liked_videos(current_user: User = Depends(get_current_user)):
    cursor = db.likes.find({"user_id": str(current_user.id)}).sort("created_at", -1)
    
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
