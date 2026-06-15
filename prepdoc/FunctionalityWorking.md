# Functionality & Inner Workings

This document outlines all the core functionalities implemented in the StreamTube project and provides a detailed technical explanation of how each one operates under the hood.

---

## 1. User Authentication & Authorization
**Functionality**: Users can register for an account and log in securely.
**How it works**:
- **Registration**: When a user registers, the backend receives the plain-text password, uses `bcrypt` to salt and hash it, and stores the hashed string in MongoDB.
- **Login (JWT)**: Upon login, the backend compares the submitted password against the hash. If successful, it generates a JSON Web Token (JWT). The payload of this token contains the user's `user_id` and an expiration timestamp. The token is cryptographically signed using a secret key (`JWT_SECRET`).
- **Authorization**: The frontend stores this token in browser `localStorage`. Whenever the user attempts a protected action (like uploading a video or liking), the frontend attaches the token as a `Bearer` token in the `Authorization` HTTP header. FastAPI decodes this token to verify the user's identity without needing to look up a session ID in the database.

---

## 2. Video Upload Processing
**Functionality**: Users can upload `.mp4` video files and thumbnail images along with metadata (Title, Description, Tags).
**How it works**:
- **Multipart Form Data**: Because we are sending both JSON metadata and large binary files simultaneously, the frontend packages the data using `FormData` and sends a `multipart/form-data` request to FastAPI.
- **File Storage**: The backend saves the raw video file to the `uploads/videos/` directory and the image to `uploads/thumbnails/`. It generates a unique filename (using UUIDs) to prevent two users from overwriting files if they happen to upload videos with the same name.
- **Denormalization**: A document containing the file paths, title, tags, and crucially, the `creator_name`, is saved to MongoDB. Saving the creator's name directly alongside the video avoids expensive database joins later.

---

## 3. High-Performance Video Streaming
**Functionality**: Users can watch videos seamlessly, skipping ahead without needing to download the entire video first.
**How it works**:
- **HTTP Range Requests**: Browsers utilize the `Range` HTTP header (e.g., `bytes=0-1000000`) when requesting video. 
- **Chunking**: Instead of loading a 500MB video into the server's RAM (which would quickly crash the server if 100 users watched simultaneously), FastAPI opens the file, seeks to the specific byte offset requested by the browser, reads a small chunk (e.g., 1MB) into memory, and sends it back.
- **Status Code 206**: The server responds with an HTTP `206 Partial Content` status. The HTML5 `<video>` tag recognizes this and continuously requests the next chunks as the video plays.

---

## 4. Social Interactions (Likes & Comments)
**Functionality**: Users can engage with videos by liking and commenting on them in real-time without page reloads.
**How it works**:
- **AJAX / Fetch API**: When a user clicks "Like", Javascript intercepts the click, prevents the page from refreshing, and sends an asynchronous POST request to the backend.
- **Idempotency**: The backend checks the `likes` collection in MongoDB. If a document mapping this `user_id` to this `video_id` already exists, the "Like" request is treated as an "Unlike", and the document is deleted. Otherwise, it is inserted.
- **Comments**: Comments are inserted into a dedicated `comments` collection. Upon success, Javascript dynamically generates the HTML for the new comment and prepends it to the comment list on the screen instantly.

---

## 5. Trending & Discovery Engine
**Functionality**: The homepage displays the most popular videos, and users can search for specific content.
**How it works**:
- **View Counting**: Every time a user requests the stream for a video, or loads the watch page, the backend increments the `views` integer field on the Video document.
- **Trending Logic**: The `/videos/trending` API simply queries MongoDB for all videos and applies a `.sort([("views", -1)])` operation, returning the list ordered from most views to least views.
- **Search**: The search bar leverages MongoDB's querying capabilities. It uses a case-insensitive regular expression (`$regex`) on the `title` field, and an `$in` query on the `tags` array, filtering down the video list based on the user's input.

---

## 6. Personalization (Watch History)
**Functionality**: The system remembers what videos a user has watched so they can find them later.
**How it works**:
- **Background Tracking**: While the user is watching a video, the frontend silently fires a background `POST /playlists/history/{video_id}` request.
- **Upserting**: The backend looks at the user's document in the `users` collection. It appends the `video_id` to an array called `history`. It ensures that duplicates are handled (either by bringing the previously watched video to the top of the history list, or ignoring duplicates) so the user's history remains accurate and sorted chronologically.

---

## 7. Dynamic User Interface (Jinja2 & DOM)
**Functionality**: The platform feels like a modern Single Page Application (SPA), with collapsible sidebars and dynamic grids.
**How it works**:
- **Jinja2 Templating**: Instead of writing separate HTML files for Home, History, and Search, we use Jinja2. The backend injects a variable (`api_endpoint`) into the `index.html` template before sending it to the user.
- **Javascript Rendering**: The frontend Javascript looks at the `api_endpoint` variable. If it's on the History page, it fetches from `/playlists/history`; if on Home, it fetches from `/videos/trending`. It then loops through the returned JSON array and dynamically generates the HTML cards for the video grid.
- **Responsive Grid**: We use Bootstrap 5's Flexbox grid (`col-lg-9`, `col-lg-3`) combined with Javascript toggle functions. When the user watches a video, Javascript removes the sidebar, causing the video player grid column to expand and fill the extra space automatically. The "Up Next" container filters out the currently playing video and populates itself with the remaining fetched videos.

---

## 8. Advanced UI Aesthetics & Animations
**Functionality**: The application provides a sleek, modern, YouTube-style aesthetic with micro-animations and feedback.
**How it works**:
- **Icons & Favicon**: We utilize `bootstrap-icons` for highly scalable SVG iconography (e.g., `bi-play-btn-fill`). The browser tab favicon is rendered dynamically by injecting raw SVG markup into a base64/URL-encoded data URI (`data:image/svg+xml`) inside the `<link rel="icon">` tag, avoiding the need for an external image file.
- **Toast Notifications**: Native Javascript `alert()` popups block the main thread and provide poor user experience. We replaced them with a global **Bootstrap Toast Notification** system. A single hidden Toast HTML element resides in `base.html`. The global `showToast()` Javascript utility manipulates the DOM to inject dynamic text, change the background color class (e.g., `bg-success`, `bg-danger`), and triggers Bootstrap's CSS fade-in transitions.
- **Collapsible Sidebar**: The hamburger menu toggles a sidebar via DOM class manipulation. Instead of instantly snapping, we apply a custom CSS transition (`transition: margin-left 0.2s`) so the sidebar slides smoothly off the screen.
- **Unauthenticated State Centering**: When a user attempts to access a protected page (like History) without a token, the frontend intercepts the `401 Unauthorized` API response. It strips the default Bootstrap grid columns and applies absolute Flexbox centering (`d-flex flex-column align-items-center justify-content-center w-100`) with a `70vh` min-height to perfectly center a beautiful sign-in prompt exactly in the middle of the screen.
