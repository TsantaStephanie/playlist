from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.playlist import (
    GeneratePlaylistRequest,
    PlaylistProposalResponse,
    PlaylistResponse,
    SavePlaylistRequest,
    UpdatePlaylistRequest,
)
from app.core.database import get_db
from app.services.playlist_generator import PlaylistGeneratorService

router = APIRouter(prefix="/api/playlist", tags=["Playlist"])


@router.post("/generate", response_model=list[PlaylistProposalResponse])
async def generate_playlist(body: GeneratePlaylistRequest, db: AsyncSession = Depends(get_db)):
    service = PlaylistGeneratorService(db)
    proposals = await service.generate(body.model_dump())
    return [
        PlaylistProposalResponse(
            name=p["name"],
            items=p["items"],
            total_duration=sum(s.duration for s in p["items"]),
            total_tracks=len(p["items"]),
        )
        for p in proposals
    ]


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


@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(playlist_id: int, body: UpdatePlaylistRequest, db: AsyncSession = Depends(get_db)):
    service = PlaylistGeneratorService(db)
    playlist = await service.update(playlist_id, body.name, body.mp3_ids)
    return PlaylistResponse.from_model(playlist)


@router.delete("/{playlist_id}", status_code=204)
async def delete_playlist(playlist_id: int, db: AsyncSession = Depends(get_db)):
    await PlaylistGeneratorService(db).delete(playlist_id)