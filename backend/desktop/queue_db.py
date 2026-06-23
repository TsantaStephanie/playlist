"""File d'attente légère basée sur PostgreSQL — remplace RabbitMQ."""
import json
import time
from pathlib import Path
from typing import Any, Callable

import psycopg2
import psycopg2.extras
import yaml


def _load_dsn() -> str:
    cfg_path = Path(__file__).parent / "config.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        db = yaml.safe_load(f)["database"]
    return (
        f"host={db['host']} port={db['port']} dbname={db['name']} "
        f"user={db['user']} password={db['password']}"
    )


def _conn():
    return psycopg2.connect(_load_dsn())


def init_table() -> None:
    with _conn() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id         SERIAL PRIMARY KEY,
                queue      TEXT        NOT NULL,
                payload    JSONB       NOT NULL,
                status     TEXT        NOT NULL DEFAULT 'pending',
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_queue_status ON messages(queue, status)"
        )
        conn.commit()


def publish(queue: str, payload: Any) -> None:
    init_table()
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO messages (queue, payload) VALUES (%s, %s)",
            (queue, json.dumps(payload, ensure_ascii=False)),
        )
        conn.commit()


def consume(queue: str, callback: Callable[[Any], None], poll_interval: float = 2.0) -> None:
    """Boucle bloquante. Prend un message 'pending', appelle callback, marque 'done' ou 'failed'."""
    init_table()
    while True:
        with _conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # SELECT ... FOR UPDATE SKIP LOCKED : évite les doublons si plusieurs workers
            cur.execute("""
                SELECT id, payload FROM messages
                WHERE queue = %s AND status = 'pending'
                ORDER BY id
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            """, (queue,))
            row = cur.fetchone()

            if not row:
                conn.rollback()
                time.sleep(poll_interval)
                continue

            msg_id = row["id"]
            payload = row["payload"]

            cur.execute("UPDATE messages SET status='processing' WHERE id=%s", (msg_id,))
            conn.commit()

        try:
            callback(payload)
            with _conn() as conn, conn.cursor() as cur:
                cur.execute("UPDATE messages SET status='done' WHERE id=%s", (msg_id,))
                conn.commit()
        except Exception:
            with _conn() as conn, conn.cursor() as cur:
                cur.execute("UPDATE messages SET status='failed' WHERE id=%s", (msg_id,))
                conn.commit()
            raise
