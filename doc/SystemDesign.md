# System Design Detailed Specification

This document details the System Design decisions, trade-offs, and architectures chosen to satisfy the requirements of a scalable video streaming platform.

## 1. Requirements Gathering

### Functional Requirements
1. **User Management**: Registration, authentication, and session handling.
2. **Video Management**: Uploading media files (videos, thumbnails) with associated metadata (title, tags, description).
3. **Streaming**: Smooth video playback with seek/scrub support.
4. **Social Interactions**: Liking videos and commenting on them.
5. **Discovery**: Searching by query and tracking trending videos based on view counts.
6. **User History**: Tracking previously watched videos and managing a list of liked videos.

### Non-Functional Requirements
1. **Low Latency**: Time-to-first-byte (TTFB) for video streaming must be minimal.
2. **Scalability**: The backend must handle high concurrency (many users streaming at once).
3. **Availability**: The platform should remain operational and robust against failures.

---

## 2. Component Design & Trade-offs

### The Backend Framework: FastAPI
**Decision**: We chose FastAPI (Python) over Django or Flask.
**Trade-off/Reasoning**: FastAPI is natively asynchronous, meaning it uses an event loop to handle concurrent connections efficiently. Video streaming inherently involves holding many connections open simultaneously; traditional synchronous frameworks like Django would quickly exhaust worker threads, leading to application crashes under load.

### The Database: MongoDB (NoSQL)
**Decision**: We chose MongoDB over a relational SQL database like PostgreSQL.
**Trade-off/Reasoning**: 
1. **Schema Flexibility**: Video metadata, tags, and dynamic attributes are easily stored as arrays within a single BSON document.
2. **Read-Heavy Workload**: A video platform is extremely read-heavy (95% reads, 5% writes). MongoDB's document model allows us to retrieve all necessary data for a video in a single disk read without performing expensive SQL `JOIN` operations.
3. **Scalability**: MongoDB supports native sharding for horizontal scaling as our dataset grows.

### The Storage Layer: Local File System
**Decision**: We currently use local disk storage (`uploads/videos/`) for media.
**Trade-off/Reasoning**: This was chosen for simplicity during the MVP phase.
**Bottleneck**: Serving large blobs of data directly from the application server will consume vast amounts of disk I/O and network bandwidth, eventually starving the API of resources.
**Production Solution**: In a real-world scenario, we would use an Object Storage service like AWS S3 to store the videos, paired with a Content Delivery Network (CDN) like AWS CloudFront to cache the videos geographically close to the users.

---

## 3. Database Schema Design (Denormalization)

In a relational database, you would store a `user_id` in the `Video` table, and do a SQL `JOIN` with the `User` table to get the creator's username.

In MongoDB, `JOIN`s (called `$lookup`) are expensive. To optimize for read speed, we applied **Denormalization**. 
When a video is uploaded, we store *both* the `creator_id` and the `creator_name` directly inside the `Video` document. 
When a user views the homepage, we only need to query the `videos` collection to render the UI, completely bypassing the `users` collection. This consumes slightly more storage space but drastically improves performance.

---

## 4. Video Streaming Mechanics

To prevent out-of-memory (OOM) errors, we cannot load a 500MB video file into RAM to send it to the client. We implemented a **Chunked Streaming Response**.

1. The client requests a byte range via the `Range` HTTP header.
2. The server opens the file descriptor, seeks to the requested byte offset, and reads a fixed chunk (e.g., 1MB).
3. The server closes the file descriptor and transmits the chunk to the client with an HTTP `206 Partial Content` status code.
4. The browser buffers this chunk and seamlessly requests the next one.

---

## 5. Security & Authentication

We utilized **JSON Web Tokens (JWT)**.
- **Why?**: JWTs are stateless. The server does not need to look up a session ID in the database or Redis to know who the user is. The token itself contains the cryptographic proof of identity.
- **Vulnerability Mitigation**: To prevent XSS (Cross-Site Scripting) attacks from stealing the token from `localStorage`, a stricter production system would move the token to an `HttpOnly` secure cookie.
