from pathlib import Path
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import MP3Model
from app.infrastructure.database.repositories import MP3Repository


class MP3Service:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = MP3Repository(db)
        # Chemins vers les fichiers de liste noire (à la racine du projet backend)
        self.blacklist_artists_path = Path(__file__).parents[2] / "blacklist.txt"
        self.blacklist_genres_path = Path(__file__).parents[2] / "blacklist_genres.txt"

    def _is_artist_blacklisted(self, artist_name: Optional[str]) -> bool:
        """Vérifie si l'artiste est dans la liste noire (non sensible à la casse)."""
        if not artist_name or not self.blacklist_artists_path.exists():
            return False

        artist_cleaned = artist_name.strip().lower()

        try:
            with open(self.blacklist_artists_path, "r", encoding="utf-8") as f:
                blacklisted_artists = [line.strip().lower() for line in f if line.strip()]
            
            for blacklisted in blacklisted_artists:
                if blacklisted in artist_cleaned:
                    return True
            return False
        except Exception as e:
            print(f"[ERREUR BLACKLIST ARTISTE] Impossible de lire le fichier : {e}")
            return False

    def _is_genre_blacklisted(self, genre_name: Optional[str]) -> bool:
        """Vérifie si le genre est dans la liste noire (non sensible à la casse)."""
        if not genre_name or not self.blacklist_genres_path.exists():
            return False

        genre_cleaned = genre_name.strip().lower()

        try:
            with open(self.blacklist_genres_path, "r", encoding="utf-8") as f:
                blacklisted_genres = [line.strip().lower() for line in f if line.strip()]
            
            for blacklisted in blacklisted_genres:
                if blacklisted in genre_cleaned:
                    return True
            return False
        except Exception as e:
            print(f"[ERREUR BLACKLIST GENRE] Impossible de lire le fichier : {e}")
            return False

    async def add(self, data: dict[str, Any]) -> MP3Model:
        artist = data.get("artist")
        genre = data.get("genre")

        # 1. Vérification de la blacklist Artiste
        if self._is_artist_blacklisted(artist):
            print(f"[BLACKLIST ARTISTE] L'artiste '{artist}' est bloqué. Enregistrement annulé.")
            raise HTTPException(
                status_code=400, 
                detail=f"Enregistrement refusé : l'artiste '{artist}' fait partie de la liste noire."
            )

        # 2. Vérification de la blacklist Genre
        if self._is_genre_blacklisted(genre):
            print(f"[BLACKLIST GENRE] Le genre '{genre}' est bloqué. Enregistrement annulé.")
            raise HTTPException(
                status_code=400, 
                detail=f"Enregistrement refusé : le genre '{genre}' fait partie de la liste noire."
            )

        existing = await self.repo.get_by_path(data["file_path"])
        if existing:
            print(f"[DEBUG BDD] Le chemin existe déjà. ID {existing.id} va être mis à jour (UPDATE)")
            return await self.repo.update(existing.id, data)
        
        print(f"[DEBUG BDD] Nouveau chemin détecté. Création d'une nouvelle ligne (INSERT)")
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

    async def delete(self, mp3_id: int) -> bool:
        return await self.repo.delete(mp3_id)