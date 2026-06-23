from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class MP3:
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
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
