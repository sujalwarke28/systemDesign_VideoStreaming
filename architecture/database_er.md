```mermaid
erDiagram
    USER ||--o{ VIDEO : creates
    USER ||--o{ COMMENT : posts
    USER ||--o{ LIKE : gives
    USER ||--o{ PLAYLIST : creates
    USER ||--o{ WATCH_HISTORY : has
    VIDEO ||--o{ COMMENT : has
    VIDEO ||--o{ LIKE : receives
    VIDEO ||--o{ PLAYLIST : is_in
    VIDEO ||--o{ WATCH_HISTORY : features
```
