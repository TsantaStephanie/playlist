"""P3 — Envoi des métadonnées vers l'API web.

Consomme queue_2, POST vers l'API, puis supprime ou déplace le fichier source.
"""
import shutil
import time
from pathlib import Path

import requests
import yaml

from logger import get_logger
from queue_db import consume

log = get_logger("P3")


def _load_config() -> dict:
    cfg_path = Path(__file__).parent / "config.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_blacklist() -> dict:
    bl_path = Path(__file__).parent / "blacklist.yaml"
    if not bl_path.exists():
        return {"artists": [], "genres": []}
    with open(bl_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {
        "artists": [a.lower() for a in (data.get("artists") or [])],
        "genres":  [g.lower() for g in (data.get("genres")  or [])],
    }


def _is_blacklisted(metadata: dict, blacklist: dict) -> str | None:
    """Retourne la raison si blacklisté, None sinon."""
    artist = (metadata.get("artist") or "").lower()
    genre  = (metadata.get("genre")  or "").lower()
    if artist and artist in blacklist["artists"]:
        return f"artist={metadata['artist']}"
    if genre and genre in blacklist["genres"]:
        return f"genre={metadata['genre']}"
    return None


def _send_to_api(metadata: dict, api_url: str, timeout: int, max_retries: int) -> bool:
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(api_url, json=metadata, timeout=timeout)
            if resp.status_code in (200, 201):
                return True
            log.warning(
                f"API a répondu {resp.status_code} (tentative {attempt}/{max_retries}) "
                f"pour {Path(metadata['file_path']).name}"
            )
        except requests.RequestException as exc:
            log.warning(f"Erreur réseau tentative {attempt}/{max_retries} : {exc}")
        if attempt < max_retries:
            time.sleep(2 ** attempt)  # backoff exponentiel

    return False


def _handle(metadata: dict) -> None:
    cfg = _load_config()
    api_url = cfg["api"]["url"]
    timeout = cfg["api"]["timeout_seconds"]
    max_retries = cfg["api"]["max_retries"]
    on_failure = cfg.get("on_send_failure", "keep")
    error_dir = Path(cfg["watch"]["error_directory"])
    blacklist_dir = Path(cfg["watch"]["blacklist_directory"])

    file_path = Path(metadata.get("file_path", ""))

    # Vérification blacklist avant tout envoi
    blacklist = _load_blacklist()
    reason = _is_blacklisted(metadata, blacklist)
    if reason:
        blacklist_dir.mkdir(parents=True, exist_ok=True)
        dest_bl = blacklist_dir / file_path.name
        try:
            shutil.move(str(file_path), dest_bl)
        except OSError as exc:
            log.error(f"Impossible de déplacer {file_path.name} vers blacklist : {exc}")
        log.info(f"Blacklisté : {file_path.name} ({reason}) — déplacé vers {blacklist_dir}")
        return

    processed_dir = Path(cfg["watch"]["processed_directory"])
    processed_dir.mkdir(parents=True, exist_ok=True)
    dest = processed_dir / file_path.name

    # Enregistre le chemin FINAL en base (pas le chemin entrant)
    metadata["file_path"] = str(dest)
    log.info(f"Envoi début : {file_path.name} vers {api_url}")

    success = _send_to_api(metadata, api_url, timeout, max_retries)

    if success:
        try:
            shutil.move(str(file_path), dest)
            log.info(f"Envoi fin : {file_path.name} (succès) — déplacé vers {dest}")
        except OSError as exc:
            log.error(f"Impossible de déplacer {file_path.name} : {exc}")
    else:
        log.error(f"Envoi fin : {file_path.name} (échec) — fichier conservé")
        if on_failure == "move" and file_path.exists():
            error_dir.mkdir(parents=True, exist_ok=True)
            dest = error_dir / file_path.name
            try:
                shutil.move(str(file_path), dest)
                log.info(f"Fichier déplacé vers {dest}")
            except OSError as exc:
                log.error(f"Impossible de déplacer {file_path.name} : {exc}")


def main() -> None:
    cfg = _load_config()
    queue_2 = cfg["queues"]["queue_2"]
    log.info(f"P3 en attente sur {queue_2}…")
    consume(queue_2, _handle)


if __name__ == "__main__":
    main()
