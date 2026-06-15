# Testing Strategy

This document outlines the testing strategy for the Video Streaming Platform, covering unit, API, and integration tests.

## Prerequisites
Install the testing dependencies:
```bash
pip install pytest pytest-asyncio httpx
```

## 1. Unit Tests
Unit tests verify the functionality of isolated components like utility functions, service logic, and database query builders.

**Steps to Write & Run:**
1. Create a file `tests/test_auth.py`.
2. Write tests for `verify_password` and `get_password_hash` from `services.auth_service`.
3. Example:
```python
from services.auth_service import get_password_hash, verify_password

def test_password_hashing():
    pwd = "secretpassword"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
```
4. Run `pytest tests/test_auth.py`

## 2. API Tests
API tests ensure that the FastAPI endpoints respond correctly to HTTP requests using `httpx.AsyncClient` or `fastapi.testclient.TestClient`.

**Steps to Write & Run:**
1. Create `tests/test_api.py`.
2. Use `TestClient` to test the `/auth/register` and `/auth/login` endpoints.
3. Example:
```python
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Video Streaming Platform API"}
```
4. Run `pytest tests/test_api.py`

## 3. Basic Integration Tests
Integration tests verify that different components (like the API, MongoDB, and Local Filesystem) work together seamlessly.

**Steps to Write & Run:**
1. Setup a test MongoDB instance or mock the database connection using `pytest` fixtures.
2. Write a test that registers a user, logs in to get a token, and then uploads a video using that token.
3. Verify that the video file exists on the local filesystem and the document exists in the mock database.
4. Run `pytest tests/` to execute the full suite.
