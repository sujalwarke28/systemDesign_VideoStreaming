# Technical Concepts Applied

This document serves as a glossary and explanation of all the technical concepts utilized in the development of this video streaming platform, ranging from basic web fundamentals to advanced backend mechanisms.

## Basic Concepts

### 1. RESTful APIs
Representational State Transfer (REST) is an architectural style for designing networked applications. We use standard HTTP methods (`GET` for fetching videos, `POST` for creating comments/uploads, `DELETE` for removing videos) to interact with resources.

### 2. HTTP Methods & Status Codes
- **GET**: Retrieve data (e.g., `200 OK`).
- **POST**: Submit new data (e.g., `201 Created` for a successful upload).
- **DELETE**: Remove data (e.g., `204 No Content`).
- **401 Unauthorized**: Returned when a user tries to like a video without a valid JWT.
- **404 Not Found**: Returned when querying a non-existent video ID.
- **500 Internal Server Error**: Backend crash or exception.

### 3. JSON (JavaScript Object Notation)
The standard data format used for communicating between our Frontend JavaScript and Backend FastAPI server.

## Intermediate Concepts

### 1. JWT (JSON Web Tokens) Authentication
A stateless authentication mechanism. Instead of storing session IDs in a server's memory, the server cryptographically signs a JSON payload containing the user's ID. The client stores this token and sends it with every request. The server verifies the signature to ensure the token hasn't been tampered with.

### 2. Password Hashing (Bcrypt)
Passwords are not stored in plain text. We use `bcrypt`, a hashing function that inherently incorporates a "salt" (random data) and is computationally slow, protecting against brute-force and rainbow-table attacks if the database is ever compromised.

### 3. NoSQL Databases (MongoDB)
Unlike SQL (which uses rigid tables and rows), NoSQL stores data as flexible JSON-like documents. This is ideal for our project because video metadata (like an array of `tags`) can be easily embedded directly into the Video document without requiring complex JOIN operations across multiple tables.

### 4. Denormalization
A database optimization strategy used in NoSQL. Instead of storing only the `creator_id` in the Video document and performing a second query to find the creator's username, we *denormalize* the data by saving the `creator_name` directly inside the Video document at the time of upload. This massively speeds up read operations.

## Advanced Concepts

### 1. Asynchronous I/O (Async/Await)
Python's `asyncio` allows the server to handle thousands of concurrent requests. When the server asks MongoDB for a video, instead of halting all operations waiting for the database to reply (synchronous blocking), it "awaits" the response and moves on to serve other users' requests in the meantime.

### 2. HTTP Range Requests (206 Partial Content)
To stream large video files efficiently:
1. The browser sends a request with a `Range: bytes=0-` header.
2. The server reads a small chunk (e.g., 1MB) of the file from the disk.
3. The server responds with status `206 Partial Content`, a `Content-Range` header, and the byte chunk.
4. The HTML5 `<video>` player stitches these chunks together, allowing the user to watch the video while it downloads or skip to unbuffered sections.

### 3. Server-Side Template Rendering (Jinja2)
Before the server sends the HTML file to the browser, Jinja2 parses the file and replaces template tags (e.g., `{{ page_title }}`) with actual Python variables. This allows us to use one single `index.html` file to dynamically render the "Home", "History", and "Liked Videos" pages.

### 4. Dependency Injection
FastAPI uses dependency injection extensively (e.g., `Depends(get_current_user)`). Before a route function runs, FastAPI automatically executes the dependency function. If the token is missing or invalid, the dependency throws a 401 error, protecting the route without requiring repetitive authorization code in every endpoint.

### 5. Object Storage & Edge Caching (AWS S3 & CloudFront)
Unlike traditional file systems that store files in a folder hierarchy on a hard drive, **AWS S3** stores files as "Objects" in a flat bucket, allowing infinite horizontal scaling. **CloudFront** is a Content Delivery Network (CDN) that caches these objects at edge servers geographically close to the user, drastically reducing buffering times and relieving our EC2 backend from streaming heavy files.

### 6. Reverse Proxy & Daemons (Nginx & Systemd)
Our FastAPI app runs on an **AWS EC2** instance, managed by `systemd` (a background daemon that ensures the app stays alive 24/7). **Nginx** sits in front of the app as a reverse proxy, accepting incoming internet traffic (port 80) and securely forwarding it to the internal FastAPI server.

## Frontend & UI Concepts

### 1. Single Page Application (SPA) Aesthetics
Using AJAX (Asynchronous JavaScript and XML) via the `fetch` API allows us to dynamically alter the DOM (Document Object Model) without refreshing the webpage. This creates a seamless, app-like experience (like instantly appending a comment or toggling a Like button).

### 2. SVG (Scalable Vector Graphics) Data URIs
Instead of linking an external `.ico` or `.png` file for the browser tab favicon, we directly embed XML-based SVG code into the HTML document using a `data:image/svg+xml` URI. This saves HTTP requests and allows infinite scaling without pixelation.

### 3. CSS Transitions & DOM Manipulation
By leveraging CSS classes (like `transition: margin-left 0.2s`), we can animate layout changes smoothly. When a user clicks the hamburger menu, JavaScript manipulates the DOM to swap Bootstrap grid classes (`d-none`, `d-block`), triggering hardware-accelerated CSS animations.

### 4. Toast Notifications
Instead of blocking the main thread with native `alert()` popups, we use Bootstrap Toast components. JavaScript dynamically injects messages and contextual color classes (`bg-success`, `bg-danger`) into a hidden HTML element, and triggers Bootstrap's built-in CSS fade animations to gracefully display non-blocking alerts to the user.
