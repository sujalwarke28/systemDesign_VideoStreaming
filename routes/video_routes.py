from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, Request, Response
from fastapi.responses import StreamingResponse
from models.user import User
from models.video import Video, VideoResponse
from routes.auth_routes import get_current_user
from database.db import db
from typing import List, Optional
import os
import uuid
import re
from bson import ObjectId
from fastapi.responses import RedirectResponse
from services.aws_service import upload_file_to_s3, delete_file_from_s3

router = APIRouter(prefix="/videos", tags=["Videos"])

VIDEO_UPLOAD_DIR = "uploads/videos"
THUMBNAIL_UPLOAD_DIR = "uploads/thumbnails"

os.makedirs(VIDEO_UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    title: str = Form(...),
    description: str = Form(...),
    tags: str = Form(""),
    video_file: UploadFile = File(...),
    thumbnail_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    video_filename = f"videos/{uuid.uuid4()}_{video_file.filename}"
    cloudfront_video_url = await upload_file_to_s3(video_file, video_filename)
    if not cloudfront_video_url:
        raise HTTPException(status_code=500, detail="Failed to upload video to S3")
        
    cloudfront_thumb_url = None
    if thumbnail_file:
        thumb_filename = f"thumbnails/{uuid.uuid4()}_{thumbnail_file.filename}"
        cloudfront_thumb_url = await upload_file_to_s3(thumbnail_file, thumb_filename)
            
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    new_video = Video(
        title=title,
        description=description,
        cloudfront_url=cloudfront_video_url,
        thumbnail_url=cloudfront_thumb_url,
        creator_id=str(current_user.id),
        creator_name=current_user.username,
        tags=tag_list
    )
    
    result = await db.videos.insert_one(new_video.model_dump(by_alias=True, exclude_none=True))
    created_video = await db.videos.find_one({"_id": result.inserted_id})
    if not created_video:
        raise HTTPException(status_code=500, detail="Failed to save video metadata")
    created_video["id"] = str(created_video["_id"])
    created_video["creator_id"] = str(created_video["creator_id"])
    return created_video

@router.get("/random", response_model=List[VideoResponse])
async def random_videos():
    # Use MongoDB $sample aggregation to return randomized videos
    cursor = db.videos.aggregate([{"$sample": {"size": 20}}])
    videos = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc["creator_id"] = str(doc["creator_id"])
        videos.append(doc)
    return videos

@router.get("/trending", response_model=List[VideoResponse])
async def trending_videos():
    # Simple trending logic: sort by views descending
    cursor = db.videos.find().sort("views", -1).limit(20)
    videos = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc["creator_id"] = str(doc["creator_id"])
        videos.append(doc)
    return videos

@router.get("/", response_model=List[VideoResponse])
async def list_videos():
    cursor = db.videos.find()
    videos = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc["creator_id"] = str(doc["creator_id"])
        videos.append(doc)
    return videos

@router.delete("/{video_id}")
async def delete_video(video_id: str, current_user: User = Depends(get_current_user)):
    try:
        obj_id = ObjectId(video_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid video ID")
        
    video = await db.videos.find_one({"_id": obj_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    if video["creator_id"] != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this video")
        
    # Delete files from S3/Storage
    try:
        video_key = "/".join(video["cloudfront_url"].split("/")[-2:])
        delete_file_from_s3(video_key)
        if video.get("thumbnail_url"):
            thumb_key = "/".join(video["thumbnail_url"].split("/")[-2:])
            delete_file_from_s3(thumb_key)
    except Exception as e:
        print(f"Cleanup error: {e}")
        
    await db.videos.delete_one({"_id": obj_id})
    return {"detail": "Video deleted successfully"}



# Video Streaming Algorithm (Chunking & Range Requests)
@router.get("/stream/{video_id}")
async def stream_video(video_id: str, request: Request, response: Response):
    """
    Redirects the client directly to the CloudFront CDN URL.
    The HTML5 video player natively handles the 302 redirect and streams via the CDN.
    """
    try:
        obj_id = ObjectId(video_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid video ID")
        
    video = await db.videos.find_one({"_id": obj_id})
    if not video or "cloudfront_url" not in video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    # Increment view count
    await db.videos.update_one({"_id": obj_id}, {"$inc": {"views": 1}})

    # Redirect to CDN
    return RedirectResponse(url=video["cloudfront_url"], status_code=status.HTTP_302_FOUND)
