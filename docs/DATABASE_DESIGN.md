# Database Design

## Collections

### `users`
- `_id`: ObjectId
- `username`: String (Unique Index)
- `email`: String (Unique Index)
- `hashed_password`: String
- `created_at`: DateTime

### `videos`
- `_id`: ObjectId
- `title`: String (Index)
- `description`: String
- `filename`: String
- `thumbnail_filename`: String
- `creator_id`: ObjectId (Index)
- `tags`: Array of Strings (Index)
- `views`: Integer
- `created_at`: DateTime

### `comments`
- `_id`: ObjectId
- `video_id`: ObjectId (Index)
- `user_id`: ObjectId
- `text`: String
- `created_at`: DateTime

### `likes`
- `_id`: ObjectId
- `video_id`: ObjectId
- `user_id`: ObjectId
- `created_at`: DateTime
- *Compound Unique Index on (video_id, user_id)*

### `playlists`
- `_id`: ObjectId
- `name`: String
- `user_id`: ObjectId (Index)
- `video_ids`: Array of ObjectIds
- `created_at`: DateTime

### `watch_history`
- `_id`: ObjectId
- `user_id`: ObjectId (Index)
- `video_id`: ObjectId
- `watched_at`: DateTime

## Relationships
- Users have a 1-to-many relationship with Videos, Comments, Likes, Playlists, and WatchHistory.
- Videos have a 1-to-many relationship with Comments and Likes.
- Playlists have a many-to-many relationship with Videos.

## Index Strategy
- Unique indexes on User `username` and `email` prevent duplicates.
- Indexes on `title` and `tags` speed up search operations.
- Compound unique index on `likes` prevents double-liking.
