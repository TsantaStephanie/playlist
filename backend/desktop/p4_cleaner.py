"""P4 — Nettoyage (facultatif).

Supprime tous les fichiers MP3 restants dans le répertoire surveillé.
Usage :
  python p4_cleaner.py [--dry-run]
  python p4_cleaner.py --apply-blacklist [--dry-run]
"""
import argparse
from pathlib import Path

import requests
import yaml

from logger import get_logger

log = get_logger("P4")


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


def clean(directory: Path, dry_run: bool = False) -> int:
    mp3_files = list(directory.glob("*.mp3"))
    if not mp3_files:
        log.info(f"Aucun fichier MP3 dans {directory}")
        return 0

    count = 0
    for f in mp3_files:
        if dry_run:
            log.info(f"[DRY-RUN] Supprimerait : {f.name}")
        else:
            try:
                f.unlink()
                log.info(f"Supprimé : {f.name}")
                count += 1
            except OSError as exc:
                log.error(f"Impossible de supprimer {f.name} : {exc}")

    log.info(f"Nettoyage terminé — {count} fichier(s) supprimé(s)")
    return count


def apply_blacklist(api_url: str, dry_run: bool = False) -> int:
    blacklist = _load_blacklist()
    if not blacklist["artists"] and not blacklist["genres"]:
        log.info("Blacklist vide — rien à supprimer")
        return 0

    log.info(f"Blacklist — artistes: {blacklist['artists']}, genres: {blacklist['genres']}")

    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        all_mp3s = resp.json()
    except requests.RequestException as exc:
        log.error(f"Impossible de récupérer la liste des MP3 : {exc}")
        return 0

    count = 0
    for mp3 in all_mp3s:
        artist = (mp3.get("artist") or "").lower()
        genre  = (mp3.get("genre")  or "").lower()
        reason = None
        if artist and artist in blacklist["artists"]:
            reason = f"artist={mp3['artist']}"
        elif genre and genre in blacklist["genres"]:
            reason = f"genre={mp3['genre']}"

        if reason:
            if dry_run:
                log.info(f"[DRY-RUN] Supprimerait de la base : {mp3.get('title') or mp3['file_path']} ({reason})")
            else:
                try:
                    del_resp = requests.delete(f"{api_url}/{mp3['id']}", timeout=10)
                    if del_resp.status_code == 204:
                        log.info(f"Supprimé de la base : {mp3.get('title') or mp3['file_path']} ({reason})")
                        count += 1
                    else:
                        log.warning(f"Échec suppression id={mp3['id']} : HTTP {del_resp.status_code}")
                except requests.RequestException as exc:
                    log.error(f"Erreur suppression id={mp3['id']} : {exc}")

    log.info(f"Blacklist appliquée — {count} entrée(s) supprimée(s) de la base")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="P4 — Nettoyage du répertoire source")
    parser.add_argument("--dry-run", action="store_true", help="Simule sans supprimer")
    parser.add_argument("--apply-blacklist", action="store_true", help="Supprime de la base les MP3 blacklistés")
    args = parser.parse_args()

    cfg = _load_config()

    if args.apply_blacklist:
        api_url = cfg["api"]["url"]
        apply_blacklist(api_url, dry_run=args.dry_run)
    else:
        watch_dir = Path(cfg["watch"]["directory"])
        clean(watch_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
