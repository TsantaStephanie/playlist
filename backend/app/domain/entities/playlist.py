from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from app.domain.entities.mp3 import MP3


@dataclass
class PlaylistItem:
    mp3: MP3
    position: int
    id: Optional[int] = None


@dataclass
class Playlist:
    name: str
    criteria: dict[str, Any] = field(default_factory=dict)
    items: list[PlaylistItem] = field(default_factory=list)
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_duration(self) -> float:
        return sum(item.mp3.duration for item in self.items)

    @property
    def total_tracks(self) -> int:
        return len(self.items)