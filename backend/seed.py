"""Insère des MP3 de test dans la base."""
import asyncio
import sys

sys.path.insert(0, ".")
from app.core.database import AsyncSessionLocal, create_tables
from app.infrastructure.database.models import MP3Model


SONGS = [
    {"file_path": "D:/Download/mp3/song1.mp3", "title": "Malaika", "artist": "Mahaleo", "genre": "malagasy", "language": "mg", "duration": 245.0, "year": 2005},
    {"file_path": "D:/Download/mp3/song2.mp3", "title": "Abominable", "artist": "Sonic", "genre": "classique", "language": "fr", "duration": 198.0, "year": 2000},
    {"file_path": "D:/Download/mp3/song3.mp3", "title": "Soda Pop", "artist": "SajaBoys", "genre": "pop", "language": "fr", "duration": 312.0, "year": 2008},
    {"file_path": "D:/Download/mp3/song4.mp3", "title": "Abominable2", "artist": "Sonic", "genre": "classique", "language": "fr", "duration": 220.0, "year": 2003},
]


async def seed():
    await create_tables()
    async with AsyncSessionLocal() as db:
        for data in SONGS:
            db.add(MP3Model(**data))
        await db.commit()
    print(f"{len(SONGS)} MP3 insérés avec succès.")


asyncio.run(seed())
