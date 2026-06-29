"""Base helpers for SQLite and PostgreSQL repositories."""
import os
import logging
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app.core.config import settings

logger = logging.getLogger(__name__)

# Check if PostgreSQL is enabled
is_pg = settings.database_url and (
    settings.database_url.startswith("postgresql://") or 
    settings.database_url.startswith("postgres://")
)

PG_POOL = None

def get_pg_pool():
    global PG_POOL
    if PG_POOL is None:
        try:
            import psycopg2
            from psycopg2 import pool
            logger.info("Initializing PostgreSQL Connection Pool...")
            PG_POOL = pool.SimpleConnectionPool(1, 20, settings.database_url)
        except ImportError:
            logger.error("psycopg2-binary is not installed! Cannot connect to PostgreSQL.")
            raise
    return PG_POOL


class DatabaseCursorWrapper:
    def __init__(self, cursor, is_pg=False):
        self.cursor = cursor
        self.is_pg = is_pg

    def execute(self, sql, params=None):
        if self.is_pg:
            # 1. Standardize placeholders: ? -> %s
            sql = sql.replace("?", "%s")
            
            # 2. SQLite specific table translations for PG
            if "CREATE TABLE" in sql.upper():
                sql = sql.replace("AUTOINCREMENT", "")
                sql = sql.replace("user_id INTEGER", "user_id BIGINT")
                sql = sql.replace("chat_id INTEGER", "chat_id BIGINT")
                sql = sql.replace("added_by INTEGER", "added_by BIGINT")
                sql = sql.replace("referred_by INTEGER", "referred_by BIGINT")
                
            if params is not None:
                # Convert list parameters to tuple for psycopg2 compatibility
                if isinstance(params, list):
                    params = tuple(params)
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
        else:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
        return self

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def __iter__(self):
        return self.cursor.__iter__()


class DatabaseConnectionWrapper:
    def __init__(self, conn, is_pg=False):
        self.conn = conn
        self.is_pg = is_pg

    def cursor(self):
        return DatabaseCursorWrapper(self.conn.cursor(), self.is_pg)

    def execute(self, sql, params=None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


@contextmanager
def get_conn() -> Iterator[DatabaseConnectionWrapper]:
    """Yield a connection wrapper that commits and closes on exit."""
    if is_pg:
        pool = get_pg_pool()
        conn = pool.getconn()
        try:
            yield DatabaseConnectionWrapper(conn, is_pg=True)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            pool.putconn(conn)
    else:
        conn = sqlite3.connect(settings.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=DELETE;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        try:
            yield DatabaseConnectionWrapper(conn, is_pg=False)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


class BaseRepository:
    """Marker class — currently no shared behaviour, kept for type hierarchy."""
    pass
