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
            from urllib.parse import urlparse, unquote
            logger.info("Initializing PostgreSQL Connection Pool...")
            
            url = urlparse(settings.database_url)
            username = unquote(url.username or "")
            password = unquote(url.password or "")
            database = unquote(url.path[1:] if url.path else "")
            host = url.hostname
            port = url.port or 5432
            
            PG_POOL = pool.SimpleConnectionPool(
                1, 20,
                user=username,
                password=password,
                host=host,
                port=port,
                database=database
            )
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
            if "INSERT OR IGNORE" in sql.upper():
                # Replace INSERT OR IGNORE with ON CONFLICT DO NOTHING
                sql = sql.replace("INSERT OR IGNORE", "INSERT")
                if "UNIQUE" in sql.upper() or "banned_sites" in sql or "blacklist" in sql:
                    # Append ON CONFLICT (columns) DO NOTHING, find appropriate target
                    if "banned_sites" in sql:
                        sql += " ON CONFLICT (platform, name) DO NOTHING"
                    elif "blacklist" in sql:
                        sql += " ON CONFLICT (value) DO NOTHING"
                    else:
                        sql += " ON CONFLICT DO NOTHING"
                else:
                    sql += " ON CONFLICT DO NOTHING"
            elif "INSERT OR REPLACE" in sql.upper():
                sql = sql.replace("INSERT OR REPLACE", "INSERT")
                if "users" in sql:
                    sql += " ON CONFLICT (user_id) DO UPDATE SET first_name = EXCLUDED.first_name, username = EXCLUDED.username, phone = EXCLUDED.phone, language = EXCLUDED.language"
                elif "user_settings" in sql:
                    sql += " ON CONFLICT (user_id) DO UPDATE SET spam_filter = EXCLUDED.spam_filter, group_mode = EXCLUDED.group_mode"
                elif "group_settings" in sql:
                    sql += " ON CONFLICT (chat_id) DO UPDATE SET warnings_limit = EXCLUDED.warnings_limit, custom_keywords = EXCLUDED.custom_keywords, whitelisted_domains = EXCLUDED.whitelisted_domains"
                elif "groups" in sql:
                    sql += " ON CONFLICT (chat_id) DO UPDATE SET title = EXCLUDED.title, username = EXCLUDED.username, member_count = EXCLUDED.member_count, is_active = EXCLUDED.is_active"
                else:
                    sql += " ON CONFLICT DO NOTHING"

            if "CREATE TABLE" in sql.upper():
                sql = sql.replace("id INTEGER PRIMARY KEY AUTOINCREMENT", "id SERIAL PRIMARY KEY")
                sql = sql.replace("id INTEGER PRIMARY KEY", "id SERIAL PRIMARY KEY")
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
