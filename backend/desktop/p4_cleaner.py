"""P4 — Nettoyage (facultatif).

Supprime tous les fichiers MP3 restants dans le répertoire surveillé.
Usage : python p4_cleaner.py [--dry-run]
"""
import argparse
from pathlib import Path

import yaml

from logger import get_logger

log = get_logger("P4")


def _load_config() -> dict:
    cfg_path = Path(__file__).parent / "config.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def main() -> None:
    parser = argparse.ArgumentParser(description="P4 — Nettoyage du répertoire source")
    parser.add_argument("--dry-run", action="store_true", help="Simule sans supprimer")
    args = parser.parse_args()

    cfg = _load_config()
    watch_dir = Path(cfg["watch"]["directory"])
    clean(watch_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
