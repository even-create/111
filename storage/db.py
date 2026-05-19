import sqlite3
from contextlib import closing

from config import DATABASE_PATH


CREATE_POSTS_SQL = """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school TEXT NOT NULL,
    school_type TEXT,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    date TEXT,
    category TEXT,
    year TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_SETTINGS_SQL = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
"""


def get_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_conn()) as conn:
        conn.execute(CREATE_POSTS_SQL)
        conn.execute(CREATE_SETTINGS_SQL)
        columns = {row[1] for row in conn.execute("PRAGMA table_info(posts)").fetchall()}
        migrations = {
            "school_type": "ALTER TABLE posts ADD COLUMN school_type TEXT",
            "category": "ALTER TABLE posts ADD COLUMN category TEXT",
            "year": "ALTER TABLE posts ADD COLUMN year TEXT",
        }
        for column, sql in migrations.items():
            if column not in columns:
                conn.execute(sql)
        conn.execute(
            """
            UPDATE posts
            SET year = substr(date, 1, 4)
            WHERE (year IS NULL OR year = '') AND date GLOB '20[0-9][0-9]-*'
            """
        )
        conn.execute(
            """
            UPDATE posts
            SET category = CASE
                WHEN title LIKE '%夏令营%' OR title LIKE '%优秀大学生%' THEN '夏令营'
                WHEN title LIKE '%预推免%' THEN '预推免'
                WHEN title LIKE '%推免%' OR title LIKE '%推荐免试%' OR title LIKE '%免试研究生%' OR title LIKE '%接收免试%' OR title LIKE '%保研%' THEN '推免'
                WHEN title LIKE '%招生%' THEN '招生'
                ELSE '其他'
            END
            WHERE category IS NULL OR category = ''
            """
        )
        conn.commit()


def save_post(school, title, url, date, school_type="", category="", year=""):
    try:
        with closing(get_conn()) as conn:
            conn.execute(
                """
                INSERT INTO posts (school, school_type, title, url, date, category, year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (school, school_type, title, url, date, category, year),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def list_posts(keyword="", school="", school_type="", category="", year="", limit=200):
    init_db()
    sql = """
    SELECT id, school, school_type, title, url, date, category, year, created_at
    FROM posts
    """
    clauses = []
    params = []

    if keyword:
        clauses.append("(title LIKE ? OR school LIKE ?)")
        like = f"%{keyword}%"
        params.extend([like, like])

    if school:
        clauses.append("school = ?")
        params.append(school)

    if school_type:
        clauses.append("school_type LIKE ?")
        params.append(f"%{school_type}%")

    if category:
        clauses.append("category = ?")
        params.append(category)

    if year:
        clauses.append("year = ?")
        params.append(year)

    if clauses:
        sql += " WHERE " + " AND ".join(clauses)

    sql += " ORDER BY COALESCE(date, '') DESC, id DESC LIMIT ?"
    params.append(limit)

    with closing(get_conn()) as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def get_stats():
    init_db()
    with closing(get_conn()) as conn:
        total = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        schools = conn.execute("SELECT COUNT(DISTINCT school) FROM posts").fetchone()[0]
        summer = conn.execute("SELECT COUNT(*) FROM posts WHERE category = '夏令营'").fetchone()[0]
        pre_recommend = conn.execute("SELECT COUNT(*) FROM posts WHERE category = '预推免'").fetchone()[0]
        latest = conn.execute(
            "SELECT created_at FROM posts ORDER BY id DESC LIMIT 1"
        ).fetchone()

    return {
        "total": total,
        "schools": schools,
        "summer": summer,
        "pre_recommend": pre_recommend,
        "latest": latest[0] if latest else "",
    }


def get_years():
    init_db()
    with closing(get_conn()) as conn:
        rows = conn.execute(
            "SELECT DISTINCT year FROM posts WHERE year IS NOT NULL AND year != '' ORDER BY year DESC"
        ).fetchall()
    return [row[0] for row in rows]


def get_setting(key, default=""):
    init_db()
    with closing(get_conn()) as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row[0] if row else default


def set_setting(key, value):
    init_db()
    with closing(get_conn()) as conn:
        conn.execute(
            """
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        conn.commit()


def get_notify_settings():
    return {
        "enabled": get_setting("notify_enabled", "false") == "true",
        "serverchan_key": get_setting("serverchan_key", ""),
    }
