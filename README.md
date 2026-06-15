# YouTube Clone - System Design Project

## Project Overview
This project is a production-quality, modular video streaming platform built to demonstrate advanced system design principles. It features a FastAPI backend, MongoDB database, and a native HTML/JS frontend powered by Jinja2 templates.

## Features
- User Authentication (JWT)
- Video Uploads & Local Storage
- HTTP Range Request Video Streaming
- Like and Comment on videos
- Playlists & Watch History
- Search capability (title, tags, description)
- Trending algorithm based on view counts

## Architecture Overview
- **Backend**: FastAPI API Gateway & Service Layer.
- **Database**: MongoDB Atlas.
- **Frontend**: HTML5, Vanilla JavaScript, Bootstrap 5 (via FastAPI Jinja2).
- **Storage**: Local Filesystem for Media files.

## Setup Instructions
1. Ensure Python 3.10+ is installed.
2. Clone the repository and navigate to the project directory.
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in the secrets (MongoDB URI and JWT secret are pre-filled for ease of development).

## Execution Steps
1. Run the server: `uvicorn backend.main:app --reload`
2. Access frontend at: `http://localhost:8000`
3. Access API docs at: `http://localhost:8000/docs`

## API Documentation Access
Interactive API docs are available via Swagger UI at `/docs` when the backend is running.

## Screenshots Section
*(Placeholders)*
- [Homepage UI](#)
- [Video Player](#)
- [Search Results](#)

## GitHub Repository Information
*(Placeholder for repository link)*

## Future Scope
- Cloud storage integration (AWS S3)
- Real-time transcoding (FFmpeg, Celery)
- Recommendation engine (Machine Learning)
- Content delivery network (CDN) integration
