from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import MP3Model
from app.infrastructure.database.repositories import MP3Repository


class MP3Service:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = MP3Repository(db)

    async def add(self, data: dict[str, Any]) -> MP3Model:
        existing = await self.repo.get_by_path(data["file_path"])
        if existing:
            return await self.repo.update(existing.id, data)
        return await self.repo.create(data)

    async def get(self, mp3_id: int) -> MP3Model:
        mp3 = await self.repo.get_by_id(mp3_id)
        if not mp3:
            raise HTTPException(status_code=404, detail="MP3 not found")
        return mp3

    async def list(self, filters: dict[str, Any] | None = None) -> list[MP3Model]:
        return await self.repo.list(filters)

    async def update(self, mp3_id: int, data: dict[str, Any]) -> MP3Model:
        mp3 = await self.repo.update(mp3_id, data)
        if not mp3:
            raise HTTPException(status_code=404, detail="MP3 not found")
        return mp3

    async def delete(self, mp3_id: int) -> None:
        deleted = await self.repo.delete(mp3_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="MP3 not found")