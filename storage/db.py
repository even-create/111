import sqlite3
from contextlib import closing

from config import DATABASE_PATH


CREATE_POSTS_SQL = """
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


def get_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_conn()) as conn:
        conn.execute(CREATE_POSTS_SQL)
        conn.commit()


def save_post(school, title, url, date):
    try:
        with closing(get_conn()) as conn:
            conn.execute(
                "INSERT INTO posts (school, title, url, date) VALUES (?, ?, ?, ?)",
                (school, title, url, date),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def list_posts(keyword="", school="", limit=200):
    init_db()
    sql = "SELECT id, school, title, url, date, created_at FROM posts"
    clauses = []
    params = []

    if keyword:
        clauses.append("(title LIKE ? OR school LIKE ?)")
        like = f"%{keyword}%"
        params.extend([like, like])

    if school:
        clauses.append("school = ?")
        params.append(school)

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
        latest = conn.execute(
            "SELECT created_at FROM posts ORDER BY id DESC LIMIT 1"
        ).fetchone()

    return {
        "total": total,
        "schools": schools,
        "latest": latest[0] if latest else "",
    }
