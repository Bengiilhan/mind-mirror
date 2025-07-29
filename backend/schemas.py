from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# === User ===
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# === Entry ===
class EntryCreate(BaseModel):
    text: str
    mood_score: Optional[int] = None

class EntryUpdate(BaseModel):
    text: Optional[str] = None
    mood_score: Optional[int] = None

# === Analysis (JSON formatı için) ===
class Distortion(BaseModel):
    type: str
    sentence: str
    explanation: str
    alternative: str

# === EntryResponse (analiz dahil) ===
class EntryResponse(BaseModel):
    id: int
    text: str
    mood_score: Optional[int]
    created_at: datetime
    user_id: int
    analysis: Optional[dict] = None  # analiz veri tabanında JSON (dict) tutulur

    class Config:
        from_attributes = True

