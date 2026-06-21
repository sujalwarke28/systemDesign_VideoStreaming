# StreamTube Algorithms Guide
This document provides a detailed breakdown of the core algorithms and logical patterns used in the StreamTube project, outlining their step-by-step working and exact file locations. This is an excellent reference for explaining the technical details of the project during examinations.

---

## 1. Video Streaming Algorithm (Chunking & Range Requests)
**File Path**: `routes/video_routes.py`
**Endpoint**: `GET /videos/stream/{video_id}`
**Function**: `stream_video` (Lines 120-190)

**Purpose**: To serve large video files efficiently without consuming excessive server memory.

**Step-by-Step Working**:
1. **Request Interception**: The client (HTML5 `<video>` tag) sends an HTTP GET request containing a `Range` header (e.g., `Range: bytes=0-`).
2. **Parsing the Header**: The algorithm uses regular expressions to parse the `Range` header and extract the requested starting byte (`byte1`) and ending byte (`byte2`).
3. **Calculating File Size & Length**: It calculates the total file size using `os.path.getsize(video_path)` and determines the `length` of the chunk to send (`byte2 - byte1 + 1`).
4. **Seeking the File Pointer**: Inside the `range_iterator` generator function, `f.seek(start)` moves the file pointer directly to the requested starting byte.
5. **Yielding Data in Chunks**: A `while` loop reads the file in exactly 1MB chunks (`chunk_size = 1024 * 1024`). It yields these chunks one by one, keeping RAM usage minimal.
6. **Constructing the Response**: The server replies with a `206 Partial Content` HTTP status and sets `Accept-Ranges`, `Content-Length`, and `Content-Range` headers so the browser knows exactly which part of the video it received and what to request next.

---

## 2. Dynamic Search & Pattern Matching Algorithm
**File Path**: `routes/search_routes.py`
**Endpoint**: `GET /search/`
**Function**: `search_videos` (Lines 9-42)

**Purpose**: To allow users to find videos efficiently using partial text matches and tags.

**Step-by-Step Working**:
1. **Input Reception**: The server receives search queries via URL parameters (`q` for text, `tags` for categories).
2. **Regex Compilation**: If a text query `q` is provided, the algorithm compiles it into a case-insensitive Regular Expression: `re.compile(q, re.IGNORECASE)`.
3. **Logical `$or` Construction**: It dynamically builds a MongoDB query filter utilizing the `$or` operator to search across multiple fields simultaneously (`title`, `description`, and `creator_name`).
4. **Logical `$and` / `$in` Intersection**: If `tags` are provided, the algorithm splits the comma-separated string into a list. It then applies an `$and` intersection to the existing query, filtering for documents where the `tags` array contains any of the requested tags using the `$in` operator.
5. **Database Execution**: The constructed query is executed against the `db.videos` collection, returning the matched documents.

---

## 3. Content Discovery (Trending & Randomization Algorithms)
**File Path**: `routes/video_routes.py`
**Endpoints**: `GET /videos/trending` and `GET /videos/random`
**Functions**: `trending_videos` (Lines 75-84) and `random_videos` (Lines 64-73)

**Purpose**: To populate the user's feed with popular and varied content.

**Step-by-Step Working (Trending Algorithm)**:
1. **Query Execution**: The algorithm queries the entire `db.videos` collection.
2. **Descending Sort**: It applies a descending sort (`-1`) on the integer field `views`: `sort("views", -1)`.
3. **Limiting**: It chains a `.limit(20)` command to ensure only the top 20 most-viewed videos are retrieved, reducing database overhead and network payload.

**Step-by-Step Working (Randomization Algorithm)**:
1. **Aggregation Pipeline**: Instead of a standard query, it utilizes MongoDB's advanced Aggregation Framework.
2. **$sample Operator**: It passes the `{"$sample": {"size": 20}}` stage into the pipeline. MongoDB's internal engine then efficiently selects 20 pseudo-random documents from the collection without needing to load all documents into memory.

---

## 4. Cryptographic Algorithms (Authentication & Security)
**File Paths**: 
- `services/auth_service.py` (Core logic, Lines 13-27)
- `routes/auth_routes.py` (Implementation, Lines 36-67)

**Purpose**: To securely manage user identities, hash passwords, and maintain stateless sessions.

**Step-by-Step Working (Password Hashing via Bcrypt)**:
1. When a user registers, their plain-text password is passed to `pwd_context.hash(password)`.
2. The **bcrypt** algorithm automatically generates a unique cryptographic "salt" (random string).
3. The password and salt are combined and hashed multiple times (key stretching), making it extremely slow to crack via brute-force. The resulting hash (which includes the salt) is stored in the database.
4. During login, `pwd_context.verify()` extracts the salt from the stored hash, applies it to the newly entered password, and checks if the resulting hashes match.

**Step-by-Step Working (Token Signing via JWT and HS256)**:
1. Upon successful login, a payload dictionary is created containing the user's identifier (`sub: username`) and an expiration timestamp (`exp`).
2. The `jwt.encode()` function signs this payload using the **HS256** (HMAC with SHA-256) cryptographic algorithm alongside a secret environment variable (`SECRET_KEY`).
3. This creates a JSON Web Token consisting of three parts (Header, Payload, Signature) that is sent to the client.
4. On subsequent requests, the server recalculates the signature using the payload and secret key. If it matches the signature in the token, the request is authenticated.
