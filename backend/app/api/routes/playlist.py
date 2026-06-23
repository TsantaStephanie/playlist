from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.playlist import (
    GeneratePlaylistRequest,
    PlaylistResponse,
    SavePlaylistRequest,
)
from app.core.database import get_db
from app.services.playlist_generator import PlaylistGeneratorService

router = APIRouter(prefix="/api/playlist", tags=["Playlist"])


@router.post("/generate", response_model=list[PlaylistResponse])
async def generate_playlist(body: GeneratePlaylistRequest, db: AsyncSession = Depends(get_db)):
    service = PlaylistGeneratorService(db)
    playlists = await service.generate(body.model_dump())
    return [PlaylistResponse.from_model(p) for p in playlists]


@router.post("", response_model=PlaylistResponse, status_code=201)
async def save_playlist(body: SavePlaylistRequest, db: AsyncSession = Depends(get_db)):
    service = PlaylistGeneratorService(db)
    playlist = await service.save(body.name, body.criteria, body.mp3_ids)
    return PlaylistResponse.from_model(playlist)


@router.get("", response_model=list[PlaylistResponse])
async def list_playlists(db: AsyncSession = Depends(get_db)):
    service = PlaylistGeneratorService(db)
    playlists = await service.list()
    return [PlaylistResponse.from_model(p) for p in playlists]


@router.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(playlist_id: int, db: AsyncSession = Depends(get_db)):
    service = PlaylistGeneratorService(db)
    playlist = await service.get(playlist_id)
    return PlaylistResponse.from_model(playlist)


@router.delete("/{playlist_id}", status_code=204)
async def delete_playlist(playlist_id: int, db: AsyncSession = Depends(get_db)):
    await PlaylistGeneratorService(db).delete(playlist_id)