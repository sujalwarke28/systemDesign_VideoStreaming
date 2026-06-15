from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from models.common import PyObjectId
from datetime import datetime, timezone

def get_utc_now():
    return datetime.now(timezone.utc)

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=get_utc_now)

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    created_at: datetime
