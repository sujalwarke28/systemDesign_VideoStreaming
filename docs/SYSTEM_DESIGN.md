# System Design Document

## Problem Statement
Designing a highly available, scalable, and responsive video streaming platform that allows users to upload, search, interact with, and stream videos efficiently.

## Functional Requirements
- Users can register and log in.
- Users can upload videos and thumbnails.
- Users can view, search, like, and comment on videos.
- Users can manage playlists and watch history.
- The system must support HTTP Range requests for seamless seeking.

## Non-Functional Requirements
- High Availability: The platform should be accessible 24/7.
- Scalability: The backend should handle increasing numbers of concurrent viewers.
- Low Latency: Streaming must begin with minimal buffering.
- Security: Endpoints should be protected via JWT.

## High-Level Design
The system uses a 3-tier architecture. A native HTML/JS frontend powered by Jinja2 interacts with a FastAPI backend. The backend manages object storage via AWS S3 and CloudFront, and communicates with MongoDB Atlas for structured and document data.

## Low-Level Design
The backend is split into RESTful API endpoints grouped by domain: `auth`, `videos`, `search`, `social`, and `playlists`. Data validation is handled via Pydantic models.

## Scalability Considerations
- **Storage**: AWS S3 object storage for infinite horizontal scaling and CloudFront for CDN edge caching.
- **Database**: MongoDB Atlas allows easy sharding and horizontal scaling.
- **Compute**: FastAPI is async, allowing high concurrent request throughput on single nodes. Can be load-balanced easily.

## Bottleneck Resolution
- **Storage I/O**: Serving large video files directly from the EC2 server disk was a bottleneck. This was resolved by migrating storage to AWS S3.
- **Bandwidth & Memory**: To prevent RAM consumption under heavy load, video delivery is offloaded entirely to AWS CloudFront CDN, which handles HTTP Range requests and edge caching globally.

## Future Improvements
- Implement microservices architecture.
- Add Redis for caching trending videos and search results.
- Implement Celery workers for async thumbnail generation and video transcoding.
