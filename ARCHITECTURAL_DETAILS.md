# StreamTube Architectural Details & Specifications

This document provides an exhaustive overview of the StreamTube project's system architecture, technical specifications, API endpoints, and definitions of all underlying technologies and concepts.

---

## 1. High-Level Architecture Overview

StreamTube is designed using a modern, decoupled, microservice-ready architecture. The system is split into distinct logical layers:

### Presentation Layer (Frontend)
- **Technology**: HTML5, Vanilla JavaScript, CSS (Bootstrap 5).
- **Rendering**: Uses **Jinja2 Templates** via FastAPI for server-side dynamic rendering of the initial HTML shell, followed by asynchronous JavaScript (`fetch` API) to populate data dynamically.
- **Functionality**: Handles UI/UX, user interactions, and native HTML5 video player integration.

### Application Layer (Backend API)
- **Technology**: Python 3.10+, **FastAPI**, Uvicorn (ASGI server).
- **Functionality**: Acts as the API Gateway and service layer. It is completely **stateless**, using JWTs for authentication, which allows the application layer to be easily horizontally scaled behind a load balancer. It processes requests asynchronously.

### Data Layer (Database)
- **Technology**: **MongoDB Atlas** (Cloud NoSQL), `motor` (Asynchronous Python driver).
- **Functionality**: Stores flexible, JSON-like documents. 
- **Collections**: `users` (credentials), `videos` (metadata like tags/views), `social` (likes/comments), and `playlists` (watch history). 
- **Optimization**: Uses **Denormalization** (e.g., storing `creator_name` directly on the video document) to minimize complex database joins and drastically optimize read speeds.

### Storage & Delivery Layer
- **Technology**: AWS S3 (Object Storage) & AWS CloudFront (CDN).
- **Functionality**: Stores raw `.mp4` video files and image thumbnails. Files are uniquely named using **UUIDs** to prevent collisions. CloudFront acts as a global edge cache to drastically reduce latency and server load by delivering content from edge locations closest to the user.

---

## 2. Core Concepts & Definitions

- **RESTful API**: Representational State Transfer. An architectural style that uses standard HTTP methods to manipulate resources (Users, Videos, Comments).
- **Asynchronous I/O (Async/Await)**: The FastAPI server processes tasks non-blockingly. While waiting for a large file to upload or the database to respond, the server thread is freed to handle other users' requests simultaneously.
- **Stateless Authentication (JWT)**: JSON Web Tokens. The server does not store user sessions in memory. Instead, it cryptographically signs a token containing the user's ID. The client sends this token with every request, proving their identity without server-side lookup overhead.
- **Password Hashing (Bcrypt)**: A one-way cryptographic hash function. Passwords are salted (random data appended) and hashed before storing, protecting the database from brute-force or rainbow table attacks in the event of a breach.
- **HTTP Range Requests (Chunking)**: A streaming technique where the browser requests specific byte ranges of a video (e.g., `bytes=0-1048576`). The server responds with `206 Partial Content` and yields just that 1MB chunk. This allows the user to seek forward without downloading the entire file, preserving server memory.

---

## 3. API Request Specifications

Below are the primary API routes, their expected HTTP methods, and their core functions.

### Authentication (`/auth`)
*   `POST /auth/register`: Accepts `username`, `email`, `password`. Hashes the password and creates a user. Returns `201 Created`.
*   `POST /auth/login`: Accepts `username` and `password`. Validates against the hashed DB entry. Returns a signed JWT access token (`200 OK`).
*   `GET /auth/me`: Requires JWT header. Returns the authenticated user's profile data (`200 OK`).

### Video Management (`/videos`)
*   `POST /videos/upload`: Requires JWT. Accepts `multipart/form-data` (video file, thumbnail, title, description, tags). Uploads files directly to AWS S3 via boto3 and saves metadata (with CloudFront CDN URLs) to MongoDB. Returns `201 Created`.
*   `GET /videos/stream/{video_id}`: Redirects the client to the globally cached CloudFront CDN URL for high-performance edge streaming.
*   `GET /videos/trending`: Returns the top 20 videos sorted by view count descending (`200 OK`).
*   `GET /videos/random`: Returns 20 randomized videos using MongoDB's `$sample` aggregation (`200 OK`).
*   `GET /videos/`: Lists all uploaded videos (`200 OK`).
*   `DELETE /videos/{video_id}`: Requires JWT. Verifies the user is the creator, then deletes the video file from storage and removes the document from MongoDB.

### Search & Discovery (`/search`)
*   `GET /search/`: Accepts query parameters `q` (text search) and `tags`. Uses RegEx to perform dynamic pattern matching across titles, descriptions, and creator names, intersecting with tag matches if provided (`200 OK`).

---

## 4. Standard HTTP & Error Codes Handled

The system strictly adheres to standard HTTP status codes for robust client-server communication:

### Success Codes
- **`200 OK`**: Standard response for successful GET, PUT, or DELETE operations (e.g., fetching a video list or logging in).
- **`201 Created`**: Returned when a new resource is successfully generated in the database or filesystem (e.g., successful user registration or video upload).
- **`206 Partial Content`**: Specifically used by the `/videos/stream/` endpoint. Indicates that only a partial chunk of the video file is being transmitted in response to an HTTP `Range` request.

### Error Codes (Client-Side)
- **`400 Bad Request`**: Sent when the client provides invalid data (e.g., trying to register an email/username that already exists in MongoDB, or submitting malformed form data).
- **`401 Unauthorized`**: Sent when authentication fails. This occurs if a user provides an incorrect password during login, or attempts to access a protected route (like uploading or deleting a video) without providing a valid JWT bearer token.
- **`403 Forbidden`**: Sent when a user is successfully authenticated but does not have permission to perform an action (e.g., trying to delete a video that was uploaded by a different user).
- **`404 Not Found`**: Sent when requesting a resource that does not exist (e.g., requesting a stream for an invalid `video_id`, or querying a database document that was deleted).

### Error Codes (Server-Side)
- **`500 Internal Server Error`**: Caught and returned if an unexpected exception occurs on the backend. Common causes include a failure to insert a document into MongoDB, database connection timeouts, or file I/O write errors during a video upload.
