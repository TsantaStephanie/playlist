from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.mp3 import MP3Create, MP3Response, MP3Update
from app.core.database import get_db
from app.infrastructure.database.repositories import MP3Repository
from app.services.mp3_service import MP3Service

router = APIRouter(prefix="/api/mp3", tags=["MP3"])


@router.get("/artists", response_model=list[str])
async def list_artists(db: AsyncSession = Depends(get_db)):
    return await MP3Repository(db).list_distinct("artist")


@router.get("/genres", response_model=list[str])
async def list_genres(db: AsyncSession = Depends(get_db)):
    return await MP3Repository(db).list_distinct("genre")


@router.post("", response_model=MP3Response, status_code=201)
async def create_mp3(body: MP3Create, db: AsyncSession = Depends(get_db)):
    service = MP3Service(db)
    return await service.add(body.model_dump())


@router.get("", response_model=list[MP3Response])
async def list_mp3(
    title: Optional[str] = Query(None),
    artist: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    language: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = MP3Service(db)
    filters = {k: v for k, v in {"title": title, "artist": artist, "genre": genre, "year": year, "language": language}.items() if v is not None}
    return await service.list(filters or None)


@router.get("/{mp3_id}", response_model=MP3Response)
async def get_mp3(mp3_id: int, db: AsyncSession = Depends(get_db)):
    return await MP3Service(db).get(mp3_id)


@router.put("/{mp3_id}", response_model=MP3Response)
async def update_mp3(mp3_id: int, body: MP3Update, db: AsyncSession = Depends(get_db)):
    data = body.model_dump(exclude_none=True)
    return await MP3Service(db).update(mp3_id, data)


@router.delete("/{mp3_id}", status_code=204)
async def delete_mp3(mp3_id: int, db: AsyncSession = Depends(get_db)):
    await MP3Service(db).delete(mp3_id)


@router.get("/{mp3_id}/stream")
async def stream_mp3(mp3_id: int, db: AsyncSession = Depends(get_db)):
    mp3 = await MP3Service(db).get(mp3_id)
    path = Path(mp3.file_path)

    # Fallback : cherche dans traites/ si le chemin original n'existe plus
    if not path.exists():
        fallback = Path("C:/Musique/traites") / path.name
        if fallback.exists():
            path = fallback
        else:
            raise HTTPException(status_code=404, detail=f"Fichier audio introuvable : {path.name}")

    return FileResponse(path, media_type="audio/mpeg", filename=path.name)