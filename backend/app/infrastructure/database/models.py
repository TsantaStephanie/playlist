from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MP3Model(Base):
    __tablename__ = "mp3"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    artist: Mapped[str | None] = mapped_column(String(255))
    album: Mapped[str | None] = mapped_column(String(255))
    genre: Mapped[str | None] = mapped_column(String(100))
    year: Mapped[int | None] = mapped_column(Integer)
    duration: Mapped[float] = mapped_column(Float, default=0.0)
    track_number: Mapped[int | None] = mapped_column(Integer)
    language: Mapped[str | None] = mapped_column(String(50))
    bitrate: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    playlist_items: Mapped[list["PlaylistItemModel"]] = relationship(back_populates="mp3", cascade="all, delete-orphan")


class PlaylistModel(Base):
    __tablename__ = "playlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    criteria: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["PlaylistItemModel"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan", order_by="PlaylistItemModel.position"
    )


class PlaylistItemModel(Base):
    __tablename__ = "playlist_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlist.id"), nullable=False)
    mp3_id: Mapped[int] = mapped_column(ForeignKey("mp3.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    playlist: Mapped["PlaylistModel"] = relationship(back_populates="items")
    mp3: Mapped["MP3Model"] = relationship(back_populates="playlist_items")
