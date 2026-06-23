"""Insère des MP3 de test dans la base."""
import asyncio
import sys

sys.path.insert(0, ".")
from app.core.database import AsyncSessionLocal, create_tables
from app.infrastructure.database.models import MP3Model


SONGS = [
    {"file_path": "C:/Musique/test/song1.mp3", "title": "Malaika", "artist": "Mahaleo", "genre": "malagasy", "language": "mg", "duration": 245.0, "year": 2005},
    {"file_path": "C:/Musique/test/song2.mp3", "title": "Omeo anao", "artist": "Rossy", "genre": "malagasy", "language": "mg", "duration": 198.0, "year": 2000},
    {"file_path": "C:/Musique/test/song3.mp3", "title": "Tsy mba resy", "artist": "Mahaleo", "genre": "malagasy", "language": "mg", "duration": 312.0, "year": 2008},
    {"file_path": "C:/Musique/test/song4.mp3", "title": "Nony", "artist": "Bodo", "genre": "malagasy", "language": "mg", "duration": 220.0, "year": 2003},
    {"file_path": "C:/Musique/test/song5.mp3", "title": "Hira ho anao", "artist": "Bodo", "genre": "malagasy", "language": "mg", "duration": 185.0, "year": 2001},
    {"file_path": "C:/Musique/test/song6.mp3", "title": "Rock Malagasy", "artist": "Njila", "genre": "rock", "language": "mg", "duration": 270.0, "year": 2010},
    {"file_path": "C:/Musique/test/song7.mp3", "title": "Anio", "artist": "Rossy", "genre": "malagasy", "language": "mg", "duration": 210.0, "year": 1998},
    {"file_path": "C:/Musique/test/song8.mp3", "title": "Veloma", "artist": "Mahaleo", "genre": "malagasy", "language": "mg", "duration": 290.0, "year": 2006},
    {"file_path": "C:/Musique/test/song9.mp3", "title": "Mamy ny fiainana", "artist": "Bodo", "genre": "malagasy", "language": "mg", "duration": 175.0, "year": 2004},
    {"file_path": "C:/Musique/test/song10.mp3", "title": "Ny anganon'ny tany", "artist": "Mahaleo", "genre": "malagasy", "language": "mg", "duration": 340.0, "year": 2009},
]


async def seed():
    await create_tables()
    async with AsyncSessionLocal() as db:
        for data in SONGS:
            db.add(MP3Model(**data))
        await db.commit()
    print(f"{len(SONGS)} MP3 insérés avec succès.")


asyncio.run(seed())
