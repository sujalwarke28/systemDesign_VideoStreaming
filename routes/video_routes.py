from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, Request, Response
from fastapi.responses import StreamingResponse
from models.user import User
from models.video import Video, VideoResponse
from routes.auth_routes import get_current_user
from database.db import db
from typing import List, Optional
import os
import uuid
import shutil
import re
from bson import ObjectId

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
    video_filename = f"{uuid.uuid4()}_{video_file.filename}"
    video_path = os.path.join(VIDEO_UPLOAD_DIR, video_filename)
    
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)
        
    thumb_filename = None
    if thumbnail_file:
        thumb_filename = f"{uuid.uuid4()}_{thumbnail_file.filename}"
        thumb_path = os.path.join(THUMBNAIL_UPLOAD_DIR, thumb_filename)
        with open(thumb_path, "wb") as buffer:
            shutil.copyfileobj(thumbnail_file.file, buffer)
            
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    new_video = Video(
        title=title,
        description=description,
        filename=video_filename,
        thumbnail_filename=thumb_filename,
        creator_id=str(current_user.id),
        creator_name=current_user.username,
        tags=tag_list
    )
    
    result = await db.videos.insert_one(new_video.model_dump(by_alias=True, exclude_none=True))
    created_video = await db.videos.find_one({"_id": result.inserted_id})
    if not created_video:
        raise HTTPException(status_code=500, detail="Failed to create video")
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
        
    try:
        os.remove(os.path.join(VIDEO_UPLOAD_DIR, video["filename"]))
        if video.get("thumbnail_filename"):
            os.remove(os.path.join(THUMBNAIL_UPLOAD_DIR, video["thumbnail_filename"]))
    except Exception:
        pass # ignore file not found
        
    await db.videos.delete_one({"_id": obj_id})
    return {"detail": "Video deleted successfully"}

@router.get("/stream/{video_id}")
async def stream_video(video_id: str, request: Request, response: Response):
    try:
        obj_id = ObjectId(video_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid video ID")
        
    video = await db.videos.find_one({"_id": obj_id})
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
        
    video_path = os.path.join(VIDEO_UPLOAD_DIR, video["filename"])
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found on server")

    # Increment view count
    await db.videos.update_one({"_id": obj_id}, {"$inc": {"views": 1}})

    file_size = os.path.getsize(video_path)
    range_header = request.headers.get("Range")
    
    import mimetypes
    mime_type, _ = mimetypes.guess_type(video_path)
    if not mime_type:
        mime_type = "video/mp4"

    if not range_header:
        def file_iterator():
            with open(video_path, "rb") as f:
                while chunk := f.read(1024 * 1024):
                    yield chunk
        return StreamingResponse(file_iterator(), media_type=mime_type)
    
    byte1, byte2 = 0, None
    match = re.search(r"bytes=(\d+)-(\d*)", range_header)
    if match:
        groups = match.groups()
        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])
            
    if byte2 is None:
        byte2 = file_size - 1
        
    length = byte2 - byte1 + 1
    
    def range_iterator(path, start, remaining):
        with open(path, "rb") as f:
            f.seek(start)
            chunk_size = 1024 * 1024 # 1MB
            while remaining > 0:
                data = f.read(min(chunk_size, remaining))
                if not data:
                    break
                remaining -= len(data)
                yield data
                
    headers = {
        "Content-Range": f"bytes {byte1}-{byte2}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(length),
    }
    
    return StreamingResponse(
        range_iterator(video_path, byte1, length),
        headers=headers,
        media_type=mime_type,
        status_code=status.HTTP_206_PARTIAL_CONTENT
    )
