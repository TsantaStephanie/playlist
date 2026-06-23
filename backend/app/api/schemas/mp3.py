from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MP3Create(BaseModel):
    file_path: str
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    duration: float = 0.0
    track_number: Optional[int] = None
    language: Optional[str] = None
    bitrate: Optional[int] = None


class MP3Update(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    duration: Optional[float] = None
    track_number: Optional[int] = None
    language: Optional[str] = None
    bitrate: Optional[int] = None


class MP3Response(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_path: str
    title: Optional[str]
    artist: Optional[str]
    album: Optional[str]
    genre: Optional[str]
    year: Optional[int]
    duration: float
    track_number: Optional[int]
    language: Optional[str]
    bitrate: Optional[int]
    created_at: datetime
    updated_at: datetime


class MP3Filters(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    language: Optional[str] = None