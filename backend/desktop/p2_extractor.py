"""P2 — Extraction des métadonnées MP3.

Consomme queue_1, extrait les tags ID3 via mutagen, publie dans queue_2.
"""
from pathlib import Path

import yaml
import json
from mutagen import MutagenError
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from logger import get_logger
from queue_db import consume, publish

log = get_logger("P2")


def _load_config() -> dict:
    cfg_path = Path(__file__).parent / "config.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _extract_metadata(file_path: str) -> dict:
    path = Path(file_path)

    audio = MP3(path)
    duration = audio.info.length
    bitrate = audio.info.bitrate // 1000  # kbps

    try:
        tags = EasyID3(path)
    except Exception:
        tags = {}

    def first(key: str):
        values = tags.get(key)
        return values[0] if values else None

    def first_int(key: str):
        val = first(key)
        if val is None:
            return None
        try:
            return int(str(val).split("/")[0])
        except ValueError:
            return None

    return {
        "file_path": str(path),
        "title": first("title"),
        "artist": first("artist"),
        "album": first("album"),
        "genre": first("genre"),
        "year": first_int("date"),
        "track_number": first_int("tracknumber"),
        "language": first("language"),
        "duration": round(duration, 2),
        "bitrate": bitrate,
    }


def _handle(payload: dict) -> None:
    cfg = _load_config()
    queue_2 = cfg["queues"]["queue_2"]

    file_path = payload.get("file_path", "")
    log.info(f"Extraction début : {Path(file_path).name}")

    try:
        metadata = _extract_metadata(file_path)
        log.info(f"Métadonnées extraites pour {Path(file_path).name} :")
        log.info(json.dumps(metadata, indent=2, ensure_ascii=False))

        publish(queue_2, metadata)
        log.info(f"Extraction fin : {Path(file_path).name} (succès)")
    except MutagenError as exc:
        log.error(f"Extraction échouée : {Path(file_path).name} - Fichier corrompu ({exc})")
    except FileNotFoundError:
        log.error(f"Extraction échouée : fichier introuvable — {file_path}")
    except Exception as exc:
        log.error(f"Extraction échouée : {Path(file_path).name} — {exc}")


def main() -> None:
    cfg = _load_config()
    queue_1 = cfg["queues"]["queue_1"]
    log.info(f"P2 en attente sur {queue_1}…")
    consume(queue_1, _handle)


if __name__ == "__main__":
    main()
