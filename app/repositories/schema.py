"""Schema bootstrap — creates all tables and seeds banned_sites."""
from app.repositories.base import get_conn
from app.repositories.seed_data import seed_banned_sites, seed_forensics


def _add_column_if_not_exists(c, table: str, column: str, definition: str) -> None:
    c.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in c.fetchall()]
    if column not in columns:
        c.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


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
        c.execute("CREATE INDEX IF NOT EXISTS idx_forensics_user_id ON forensics(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_forensics_violation_type ON forensics(violation_type)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_warnings_chat_user ON warnings(chat_id, user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_user_id ON scan_history(user_id)")

        c.execute("""
            CREATE TABLE IF NOT EXISTS group_settings (
                chat_id INTEGER PRIMARY KEY,
                warnings_limit INTEGER DEFAULT 3,
                custom_keywords TEXT DEFAULT '',
                whitelisted_domains TEXT DEFAULT ''
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
        # seed_forensics(c)

        # 1. URL scan cache
        c.execute("""
            CREATE TABLE IF NOT EXISTS url_scan_cache (
                url TEXT PRIMARY KEY,
                verdict TEXT,
                malicious INTEGER,
                suspicious INTEGER,
                harmless INTEGER,
                undetected INTEGER,
                checked_at TEXT
            )
        """)
        # 2. AI text classification cache
        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_text_cache (
                text_hash TEXT PRIMARY KEY,
                is_violation INTEGER,
                category TEXT,
                reason TEXT,
                cached_at TEXT,
                hit_count INTEGER DEFAULT 1
            )
        """)
        # 3. Group subscriptions
        c.execute("""
            CREATE TABLE IF NOT EXISTS group_subscriptions (
                chat_id INTEGER PRIMARY KEY,
                plan TEXT DEFAULT 'free',
                expires_at TEXT,
                warning_sent INTEGER DEFAULT 0
            )
        """)
        # 4. User subscriptions
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_subscriptions (
                user_id INTEGER PRIMARY KEY,
                plan TEXT DEFAULT 'free',
                expires_at TEXT,
                warning_sent INTEGER DEFAULT 0
            )
        """)
        # 5. AI quota usage
        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_quota_usage (
                chat_id INTEGER,
                usage_date TEXT,
                call_count INTEGER DEFAULT 0,
                PRIMARY KEY (chat_id, usage_date)
            )
        """)
        
        c.execute("CREATE INDEX IF NOT EXISTS idx_url_cache_checked_at ON url_scan_cache(checked_at)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_ai_cache_cached_at ON ai_text_cache(cached_at)")

        _add_column_if_not_exists(c, "user_settings", "filter_links", "INTEGER DEFAULT 1")
        _add_column_if_not_exists(c, "user_settings", "filter_files", "INTEGER DEFAULT 1")
        _add_column_if_not_exists(c, "user_settings", "filter_nlp", "INTEGER DEFAULT 1")
        _add_column_if_not_exists(c, "groups", "invite_link", "TEXT DEFAULT ''")
        # Kim qo'shganini bilish uchun — foydalanuvchi faqat o'zi qo'shgan guruhlarni ko'radi
        _add_column_if_not_exists(c, "groups", "added_by", "INTEGER DEFAULT 0")
        _add_column_if_not_exists(c, "users", "language", "TEXT DEFAULT 'uz'")
        _add_column_if_not_exists(c, "group_settings", "language", "TEXT DEFAULT 'uz'")
