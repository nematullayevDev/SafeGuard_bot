"""Base helpers for SQLite repositories."""
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app.core.config import settings


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection that commits and closes on exit."""
    conn = sqlite3.connect(settings.db_path, timeout=30.0)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()



class BaseRepository:
    """Marker class — currently no shared behaviour, kept for type hierarchy."""
    pass
