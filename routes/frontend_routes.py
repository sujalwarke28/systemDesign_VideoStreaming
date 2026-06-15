from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database.db import db

router = APIRouter(tags=["Frontend"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page_title": "<i class='bi bi-house-door-fill me-2'></i>Recommended",
        "api_endpoint": "/videos/random"
    })

@router.get("/trending", response_class=HTMLResponse)
async def trending_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page_title": "<i class='bi bi-fire text-danger me-2'></i>Trending Now",
        "api_endpoint": "/videos/trending"
    })

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "page_title": "<i class='bi bi-clock-history me-2'></i>Watch History", 
        "api_endpoint": "/playlists/history"
    })

@router.get("/liked", response_class=HTMLResponse)
async def liked_page(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "page_title": "<i class='bi bi-hand-thumbs-up-fill me-2 text-primary'></i>Liked Videos", 
        "api_endpoint": "/social/liked"
    })

@router.get("/watch/{video_id}", response_class=HTMLResponse)
async def watch_page(request: Request, video_id: str):
    return templates.TemplateResponse("video.html", {"request": request, "video_id": video_id})
