"""Schema bootstrap — creates all tables and seeds banned_sites."""
from app.repositories.base import get_conn
from app.repositories.seed_data import seed_banned_sites


def init_schema() -> None:
    with get_conn() as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                first_name TEXT,
                username TEXT,
                phone TEXT,
                registered_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                value TEXT UNIQUE,
                added_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                spam_filter INTEGER DEFAULT 1,
                group_mode INTEGER DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_type TEXT,
                value TEXT,
                result TEXT,
                scanned_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                reason TEXT,
                warned_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                username TEXT,
                member_count INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                added_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS forensics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                chat_title TEXT,
                user_id INTEGER,
                full_name TEXT,
                username TEXT,
                phone TEXT,
                message_text TEXT,
                violation_type TEXT,
                reason TEXT,
                detected_at TEXT,
                photo_path TEXT
            )
        """)

        # banned_sites — migrate legacy table missing UNIQUE constraint
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='banned_sites'")
        if c.fetchone():
            c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='banned_sites'")
            sql = (c.fetchone()[0] or "").upper()
            if "UNIQUE" not in sql:
                c.execute("ALTER TABLE banned_sites RENAME TO banned_sites_old")
                c.execute("""
                    CREATE TABLE banned_sites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        platform TEXT NOT NULL,
                        name TEXT NOT NULL,
                        added_at TEXT,
                        is_new INTEGER DEFAULT 1,
                        UNIQUE(platform, name)
                    )
                """)
                c.execute("""
                    INSERT OR IGNORE INTO banned_sites (platform, name, added_at, is_new)
                    SELECT platform, name, added_at, is_new FROM banned_sites_old
                """)
                c.execute("DROP TABLE banned_sites_old")
        else:
            c.execute("""
                CREATE TABLE banned_sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    name TEXT NOT NULL,
                    added_at TEXT,
                    is_new INTEGER DEFAULT 1,
                    UNIQUE(platform, name)
                )
            """)

        seed_banned_sites(c)
