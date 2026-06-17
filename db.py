"""Database layer for SkripsiEngineer (SQLite).

Connection helper, schema creation + lightweight migration, and query helpers.
"""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

# Override with DATABASE_PATH env var (useful for tests / separate environments).
DB_PATH = Path(os.environ.get("DATABASE_PATH", Path(__file__).parent / "database.db"))


def get_db_connection():
    """Return a SQLite connection with row access by name and FK enforcement."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def _cursor(commit=False):
    """Context manager yielding a connection and always closing it."""
    conn = get_db_connection()
    try:
        yield conn
        if commit:
            conn.commit()
    finally:
        conn.close()


def _column_names(conn, table):
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def init_db():
    """Create tables if missing, then add any new columns to existing tables."""
    with _cursor(commit=True) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    UNIQUE NOT NULL,
                email         TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                phone         TEXT    NOT NULL,
                major         TEXT    NOT NULL,
                role          TEXT    NOT NULL DEFAULT 'user',
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                field          TEXT    NOT NULL,
                package        TEXT    NOT NULL,
                description    TEXT    NOT NULL,
                status         TEXT    DEFAULT 'Pending',
                preferred_date TEXT,
                scheduled_date TEXT,
                price          INTEGER,
                admin_note     TEXT,
                created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )

        # --- Lightweight migration for databases created before these columns ---
        user_cols = _column_names(conn, "users")
        if "role" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")

        req_cols = _column_names(conn, "requests")
        for col, ddl in (
            ("preferred_date", "ALTER TABLE requests ADD COLUMN preferred_date TEXT"),
            ("scheduled_date", "ALTER TABLE requests ADD COLUMN scheduled_date TEXT"),
            ("price", "ALTER TABLE requests ADD COLUMN price INTEGER"),
            ("admin_note", "ALTER TABLE requests ADD COLUMN admin_note TEXT"),
        ):
            if col not in req_cols:
                conn.execute(ddl)


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------
def create_user(username, email, password_hash, phone, major, role="user"):
    """Insert a new user; return the new id, or None if email/username taken."""
    try:
        with _cursor(commit=True) as conn:
            cur = conn.execute(
                """INSERT INTO users (username, email, password_hash, phone, major, role)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (username, email, password_hash, phone, major, role),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def set_user_role(user_id, role):
    with _cursor(commit=True) as conn:
        conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))


def get_user_by_email(email):
    with _cursor() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def get_user_by_id(user_id):
    with _cursor() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_all_users():
    """All users with their request counts (newest first)."""
    with _cursor() as conn:
        rows = conn.execute(
            """SELECT u.id, u.username, u.email, u.phone, u.major, u.role, u.created_at,
                      COUNT(r.id) AS request_count
               FROM users u
               LEFT JOIN requests r ON r.user_id = u.id
               GROUP BY u.id
               ORDER BY u.created_at DESC"""
        ).fetchall()
    return [dict(row) for row in rows]


# ---------------------------------------------------------------------------
# Request helpers
# ---------------------------------------------------------------------------
def create_request(user_id, field, package, description, preferred_date=None):
    with _cursor(commit=True) as conn:
        cur = conn.execute(
            """INSERT INTO requests (user_id, field, package, description, preferred_date)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, field, package, description, preferred_date),
        )
        return cur.lastrowid


def get_requests_by_user(user_id):
    with _cursor() as conn:
        rows = conn.execute(
            "SELECT * FROM requests WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_request_by_id(req_id):
    with _cursor() as conn:
        return conn.execute("SELECT * FROM requests WHERE id = ?", (req_id,)).fetchone()


def get_all_requests():
    """All requests joined with submitting user's info (newest first)."""
    with _cursor() as conn:
        rows = conn.execute(
            """SELECT r.*, u.username, u.email, u.phone, u.major
               FROM requests r
               JOIN users u ON u.id = r.user_id
               ORDER BY
                 CASE r.status
                   WHEN 'Pending' THEN 0
                   WHEN 'Confirming' THEN 1
                   WHEN 'Approved' THEN 2
                   WHEN 'Paid' THEN 3
                   WHEN 'Ongoing' THEN 4
                   WHEN 'Completed' THEN 5
                   WHEN 'Rejected' THEN 6
                   ELSE 7
                 END,
                 r.created_at DESC"""
        ).fetchall()
    return [dict(row) for row in rows]


def approve_request(req_id, scheduled_date, price, note=None):
    with _cursor(commit=True) as conn:
        conn.execute(
            """UPDATE requests
               SET status = 'Approved', scheduled_date = ?, price = ?, admin_note = ?
               WHERE id = ?""",
            (scheduled_date, price, note, req_id),
        )


def reject_request(req_id, note=None):
    with _cursor(commit=True) as conn:
        conn.execute(
            "UPDATE requests SET status = 'Rejected', admin_note = ? WHERE id = ?",
            (note, req_id),
        )


def update_request_status(req_id, status):
    with _cursor(commit=True) as conn:
        conn.execute(
            "UPDATE requests SET status = ? WHERE id = ?", (status, req_id)
        )


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
