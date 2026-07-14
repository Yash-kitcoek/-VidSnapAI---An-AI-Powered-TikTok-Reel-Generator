import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(os.getenv("DATABASE_PATH", "data/vidsnapai.sqlite3"))


def utc_now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                description TEXT NOT NULL,
                upload_dir TEXT NOT NULL,
                output_path TEXT,
                error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


def create_job(job_id, description, upload_dir):
    now = utc_now()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO jobs (id, status, description, upload_dir, created_at, updated_at)
            VALUES (?, 'queued', ?, ?, ?, ?)
            """,
            (job_id, description, upload_dir, now, now),
        )


def update_job(job_id, status, output_path=None, error=None):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status = ?, output_path = COALESCE(?, output_path), error = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, output_path, error, utc_now(), job_id),
        )


def get_job(job_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None


def list_jobs(limit=50):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_next_queued_job():
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM jobs
            WHERE status = 'queued'
            ORDER BY created_at ASC
            LIMIT 1
            """
        ).fetchone()
        return dict(row) if row else None
