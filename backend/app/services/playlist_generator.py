from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import MP3Model, PlaylistModel
from app.infrastructure.database.repositories import MP3Repository, PlaylistRepository

TOLERANCE_SECONDS = 120  # ±2 minutes


def _knapsack_greedy(songs: list[MP3Model], target_seconds: float) -> list[MP3Model]:
    """Greedy knapsack: fill playlist as close to target_seconds as possible."""
    songs_sorted = sorted(songs, key=lambda s: s.duration, reverse=True)
    selected: list[MP3Model] = []
    total = 0.0

    for song in songs_sorted:
        if total + song.duration <= target_seconds + TOLERANCE_SECONDS:
            selected.append(song)
            total += song.duration
            if abs(total - target_seconds) <= TOLERANCE_SECONDS:
                break

    return selected


def _build_candidates(songs: list[MP3Model], target_seconds: float, top_n: int = 3) -> list[list[MP3Model]]:
    """Return up to top_n playlist candidates using slightly different starting points."""
    candidates: list[list[MP3Model]] = []

    # Candidate 1: greedy from longest to shortest
    candidates.append(_knapsack_greedy(songs, target_seconds))

    # Candidate 2: greedy from shortest to longest
    songs_asc = sorted(songs, key=lambda s: s.duration)
    selected: list[MP3Model] = []
    total = 0.0
    for song in songs_asc:
        if total + song.duration <= target_seconds + TOLERANCE_SECONDS:
            selected.append(song)
            total += song.duration
    if selected not in candidates:
        candidates.append(selected)

    # Candidate 3: random shuffle (deterministic via sort by artist)
    songs_by_artist = sorted(songs, key=lambda s: (s.artist or "", s.duration))
    selected = []
    total = 0.0
    for song in songs_by_artist:
        if total + song.duration <= target_seconds + TOLERANCE_SECONDS:
            selected.append(song)
            total += song.duration
    if selected not in candidates:
        candidates.append(selected)

    return candidates[:top_n]


class PlaylistGeneratorService:
    def __init__(self, db: AsyncSession) -> None:
        self.mp3_repo = MP3Repository(db)
        self.playlist_repo = PlaylistRepository(db)

    async def generate(self, criteria: dict[str, Any]) -> list[PlaylistModel]:
        target_minutes: float = criteria.get("duration_minutes", 0)
        if not target_minutes:
            raise HTTPException(status_code=400, detail="duration_minutes is required")

        target_seconds = target_minutes * 60

        filters: dict[str, Any] = {}
        if criteria.get("genre"):
            filters["genre"] = criteria["genre"]
        if criteria.get("artist"):
            filters["artist"] = criteria["artist"]
        if criteria.get("language"):
            filters["language"] = criteria["language"]
        if criteria.get("year"):
            filters["year"] = criteria["year"]

        songs = await self.mp3_repo.list(filters)

        exclusions: list[str] = criteria.get("exclusions", [])
        if exclusions:
            songs = [
                s for s in songs
                if not any(
                    (ex.lower() in (s.genre or "").lower() or ex.lower() in (s.artist or "").lower())
                    for ex in exclusions
                )
            ]

        if not songs:
            detail = "Aucun morceau ne correspond aux critères"
            if filters:
                detail += f" ({', '.join(f'{k}={v}' for k, v in filters.items())})"
            if exclusions:
                detail += f" — exclusions : {', '.join(exclusions)}"
            raise HTTPException(status_code=422, detail=detail)

        candidates = _build_candidates(songs, target_seconds)
        playlists: list[PlaylistModel] = []

        for i, candidate in enumerate(candidates, start=1):
            if not candidate:
                continue
            name = criteria.get("name", f"Playlist #{i}")
            if len(candidates) > 1:
                name = f"{name} (v{i})"
            playlist = await self.playlist_repo.create(
                name=name,
                criteria=criteria,
                mp3_ids=[s.id for s in candidate],
            )
            playlists.append(playlist)

        if not playlists:
            raise HTTPException(status_code=422, detail="Could not build a valid playlist with given criteria")

        return playlists

    async def save(self, name: str, criteria: dict, mp3_ids: list[int]) -> PlaylistModel:
        return await self.playlist_repo.create(name=name, criteria=criteria, mp3_ids=mp3_ids)

    async def get(self, playlist_id: int) -> PlaylistModel:
        playlist = await self.playlist_repo.get_by_id(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist

    async def list(self) -> list[PlaylistModel]:
        return await self.playlist_repo.list()

    async def delete(self, playlist_id: int) -> None:
        deleted = await self.playlist_repo.delete(playlist_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Playlist not found")