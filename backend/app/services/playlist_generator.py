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
        if criteria.get("language"):
            filters["language"] = criteria["language"]

        songs = await self.mp3_repo.list(filters)

        genres = [g.lower() for g in criteria.get("genres", [])]
        excluded_genres = [g.lower() for g in criteria.get("excluded_genres", [])]
        artists = [a.lower() for a in criteria.get("artists", [])]
        excluded_artists = [a.lower() for a in criteria.get("excluded_artists", [])]
        year_from = criteria.get("year_from")
        year_to = criteria.get("year_to")

        if genres:
            songs = [s for s in songs if (s.genre or "").lower() in genres]
        if excluded_genres:
            songs = [s for s in songs if (s.genre or "").lower() not in excluded_genres]
        if artists:
            songs = [s for s in songs if (s.artist or "").lower() in artists]
        if excluded_artists:
            songs = [s for s in songs if (s.artist or "").lower() not in excluded_artists]
        if year_from:
            songs = [s for s in songs if s.year is not None and s.year >= year_from]
        if year_to:
            songs = [s for s in songs if s.year is not None and s.year <= year_to]

        if not songs:
            raise HTTPException(status_code=422, detail="Aucun morceau ne correspond aux critères sélectionnés")

        candidates = _build_candidates(songs, target_seconds, top_n=1)
        proposals: list[dict] = []

        for i, candidate in enumerate(candidates, start=1):
            if not candidate:
                continue
            name = criteria.get("name", f"Playlist #{i}")
            proposals.append({"name": name, "items": candidate})

        if not proposals:
            raise HTTPException(status_code=422, detail="Could not build a valid playlist with given criteria")

        return proposals

    async def save(self, name: str, criteria: dict, mp3_ids: list[int]) -> PlaylistModel:
        return await self.playlist_repo.create(name=name, criteria=criteria, mp3_ids=mp3_ids)

    async def get(self, playlist_id: int) -> PlaylistModel:
        playlist = await self.playlist_repo.get_by_id(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist

    async def update(self, playlist_id: int, name: str | None, mp3_ids: list[int]) -> PlaylistModel:
        playlist = await self.playlist_repo.update(playlist_id, name, mp3_ids)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist

    async def list(self) -> list[PlaylistModel]:
        return await self.playlist_repo.list()

    async def delete(self, playlist_id: int) -> None:
        deleted = await self.playlist_repo.delete(playlist_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Playlist not found")