"""P1 — Surveillance de répertoire.

Détecte les nouveaux fichiers MP3 et les publie dans queue_1.
"""
import time
from pathlib import Path

import yaml
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from logger import get_logger
from queue_db import publish

log = get_logger("P1")


def _load_config() -> dict:
    cfg_path = Path(__file__).parent / "config.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class MP3Handler(FileSystemEventHandler):
    def __init__(self, queue: str) -> None:
        self.queue = queue

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".mp3":
            return
        log.info(f"Détection : {path}")
        try:
            publish(self.queue, {"file_path": str(path)})
            log.info(f"Publié dans {self.queue} : {path.name}")
        except Exception as exc:
            log.error(f"Erreur publication {path.name} : {exc}")


def main() -> None:
    cfg = _load_config()
    watch_dir = Path(cfg["watch"]["directory"])
    queue_1 = cfg["queues"]["queue_1"]

    watch_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"Surveillance démarrée : {watch_dir}")

    handler = MP3Handler(queue=queue_1)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Arrêt de la surveillance (KeyboardInterrupt)")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
