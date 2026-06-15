# API Documentation

## Authentication Flow
Users hit `/auth/register` to create an account, then `/auth/login` to receive a JWT token. The token must be sent in the `Authorization` header as `Bearer <token>` for protected routes.

## Endpoints

### Authentication
- `POST /auth/register`
- `POST /auth/login`

### Videos
- `POST /videos/upload` (Protected) - Multipart form data
- `GET /videos/` - List all videos
- `GET /videos/trending` - List top 20 trending videos
- `GET /videos/stream/{video_id}` - Stream video (supports Range requests)
- `DELETE /videos/{video_id}` (Protected) - Delete video

### Search
- `GET /search/?q={query}&tags={tags}&creator_id={id}` - Search videos

### Social
- `POST /social/videos/{video_id}/like` (Protected) - Toggle like
- `GET /social/videos/{video_id}/likes/count` - Get like count
- `POST /social/videos/{video_id}/comments` (Protected) - Add comment
- `GET /social/videos/{video_id}/comments` - Get comments

### Playlists & History
- `POST /playlists/` (Protected) - Create playlist
- `GET /playlists/` (Protected) - Get user's playlists
- `POST /playlists/{playlist_id}/videos/{video_id}` (Protected) - Add to playlist
- `POST /playlists/history/{video_id}` (Protected) - Record watch history
- `GET /playlists/history` (Protected) - Get watch history
