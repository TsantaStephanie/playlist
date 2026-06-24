from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from app.api.schemas.mp3 import MP3Response


class PlaylistProposalResponse(BaseModel):
    name: str
    items: list[MP3Response]
    total_duration: float
    total_tracks: int


class PlaylistItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    mp3: MP3Response


class PlaylistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    criteria: dict[str, Any]
    created_at: datetime
    items: list[PlaylistItemResponse]
    total_duration: float = 0.0
    total_tracks: int = 0

    @classmethod
    def from_model(cls, model: Any) -> "PlaylistResponse":
        total = sum(item.mp3.duration for item in model.items)
        return cls(
            id=model.id,
            name=model.name,
            criteria=model.criteria,
            created_at=model.created_at,
            items=model.items,
            total_duration=total,
            total_tracks=len(model.items),
        )


class GeneratePlaylistRequest(BaseModel):
    duration_minutes: float
    name: Optional[str] = "Ma playlist"
    genres: list[str] = []
    excluded_genres: list[str] = []
    artists: list[str] = []
    excluded_artists: list[str] = []
    language: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None


class SavePlaylistRequest(BaseModel):
    name: str
    criteria: dict[str, Any] = {}
    mp3_ids: list[int]


class UpdatePlaylistRequest(BaseModel):
    name: Optional[str] = None
    mp3_ids: list[int]