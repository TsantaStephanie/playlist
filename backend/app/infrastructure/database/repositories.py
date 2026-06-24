from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models import MP3Model, PlaylistItemModel, PlaylistModel


class MP3Repository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, data: dict[str, Any]) -> MP3Model:
        mp3 = MP3Model(**data)
        self.db.add(mp3)
        await self.db.commit()
        await self.db.refresh(mp3)
        return mp3

    async def get_by_id(self, mp3_id: int) -> Optional[MP3Model]:
        result = await self.db.execute(select(MP3Model).where(MP3Model.id == mp3_id))
        return result.scalar_one_or_none()

    async def get_by_path(self, file_path: str) -> Optional[MP3Model]:
        result = await self.db.execute(select(MP3Model).where(MP3Model.file_path == file_path))
        return result.scalar_one_or_none()

    async def list(self, filters: dict[str, Any] | None = None) -> list[MP3Model]:
        stmt = select(MP3Model)
        if filters:
            if filters.get("genre"):
                stmt = stmt.where(MP3Model.genre.ilike(f"%{filters['genre']}%"))
            if filters.get("artist"):
                stmt = stmt.where(MP3Model.artist.ilike(f"%{filters['artist']}%"))
            if filters.get("title"):
                stmt = stmt.where(MP3Model.title.ilike(f"%{filters['title']}%"))
            if filters.get("year"):
                stmt = stmt.where(MP3Model.year == filters["year"])
            if filters.get("language"):
                stmt = stmt.where(MP3Model.language.ilike(f"%{filters['language']}%"))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, mp3_id: int, data: dict[str, Any]) -> Optional[MP3Model]:
        mp3 = await self.get_by_id(mp3_id)
        if not mp3:
            return None
        for key, value in data.items():
            setattr(mp3, key, value)
        await self.db.commit()
        await self.db.refresh(mp3)
        return mp3

    async def list_distinct(self, column: str) -> list[str]:
        col = getattr(MP3Model, column)
        result = await self.db.execute(
            select(col).distinct().where(col.isnot(None)).order_by(col)
        )
        return [row[0] for row in result.all()]

    async def delete(self, mp3_id: int) -> bool:
        mp3 = await self.get_by_id(mp3_id)
        if not mp3:
            return False
        await self.db.delete(mp3)
        await self.db.commit()
        return True


class PlaylistRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, name: str, criteria: dict, mp3_ids: list[int]) -> PlaylistModel:
        playlist = PlaylistModel(name=name, criteria=criteria)
        self.db.add(playlist)
        await self.db.flush()

        for position, mp3_id in enumerate(mp3_ids, start=1):
            item = PlaylistItemModel(playlist_id=playlist.id, mp3_id=mp3_id, position=position)
            self.db.add(item)

        await self.db.commit()
        return await self.get_by_id(playlist.id)

    async def get_by_id(self, playlist_id: int) -> Optional[PlaylistModel]:
        result = await self.db.execute(
            select(PlaylistModel)
            .options(selectinload(PlaylistModel.items).selectinload(PlaylistItemModel.mp3))
            .where(PlaylistModel.id == playlist_id)
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[PlaylistModel]:
        result = await self.db.execute(
            select(PlaylistModel).options(selectinload(PlaylistModel.items).selectinload(PlaylistItemModel.mp3))
        )
        return list(result.scalars().all())

    async def update(self, playlist_id: int, name: Optional[str], mp3_ids: list[int]) -> Optional[PlaylistModel]:
        playlist = await self.get_by_id(playlist_id)
        if not playlist:
            return None
        if name:
            playlist.name = name
            await self.db.flush()
        # DELETE SQL direct pour contourner le cache de l'identity map
        await self.db.execute(delete(PlaylistItemModel).where(PlaylistItemModel.playlist_id == playlist_id))
        for position, mp3_id in enumerate(mp3_ids, start=1):
            self.db.add(PlaylistItemModel(playlist_id=playlist_id, mp3_id=mp3_id, position=position))
        await self.db.commit()
        self.db.expire_all()  # force rechargement depuis la DB
        return await self.get_by_id(playlist_id)

    async def delete(self, playlist_id: int) -> bool:
        playlist = await self.get_by_id(playlist_id)
        if not playlist:
            return False
        await self.db.delete(playlist)
        await self.db.commit()
        return True