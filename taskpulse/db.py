"""Database management module for TaskPulse.

Handles SQLite database location, connection management, schema initialization,
and versioned migrations.
"""

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
from typing import Generator, Optional

# Default database location in the user's home directory
DEFAULT_DB_FILENAME = ".taskpulse.db"
ENV_DB_VARIABLE = "TASKPULSE_DB"

# Schema migrations list. Each entry is a tuple: (version_number, sql_script)
MIGRATIONS = [
    (
        1,
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'todo' CHECK(status IN ('todo', 'in_progress', 'done')),
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ),
]


def get_db_path(custom_path: Optional[str] = None) -> str:
    """Resolve the path to the SQLite database file.

    Resolution order:
    1. Explicit custom_path argument (if provided)
    2. TASKPULSE_DB environment variable
    3. Default ~/.taskpulse.db

    Args:
        custom_path: Optional explicit filesystem path.

    Returns:
        Absolute normalized path string to the database file.
    """
    if custom_path:
        return str(Path(custom_path).expanduser().resolve())

    env_path = os.environ.get(ENV_DB_VARIABLE)
    if env_path:
        return str(Path(env_path).expanduser().resolve())

    return str(Path.home() / DEFAULT_DB_FILENAME)


@contextmanager
def get_connection(
    db_path: Optional[str] = None,
) -> Generator[sqlite3.Connection, None, None]:
    """Provide a transactional SQLite database connection context.

    Automatically commits on successful block exit and rolls back if an
    exception occurs. Sets row_factory to sqlite3.Row for dictionary-like
    column access.

    Args:
        db_path: Optional path to SQLite file; defaults to get_db_path().

    Yields:
        sqlite3.Connection: Active database connection.
    """
    path = get_db_path(db_path)
    # Ensure parent directory exists (e.g. for custom paths or default home)
    parent_dir = Path(path).parent
    parent_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the database schema and apply pending migrations.

    Safe to run multiple times (idempotent). Automatically called before
    any read/write operations.

    Args:
        db_path: Optional path to SQLite database.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Ensure schema_version table exists first
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

        # Get list of already applied versions
        cursor.execute("SELECT version FROM schema_version;")
        applied_versions = {row["version"] for row in cursor.fetchall()}

        # Apply pending migrations in order
        for version, migration_sql in sorted(MIGRATIONS, key=lambda m: m[0]):
            if version not in applied_versions:
                cursor.executescript(migration_sql)
                cursor.execute(
                    "INSERT INTO schema_version (version) VALUES (?);",
                    (version,),
                )


def check_connection(db_path: Optional[str] = None) -> bool:
    """Verify that the database is accessible and functional.

    Ensures the schema is initialized and executes a health-check query.

    Args:
        db_path: Optional path to SQLite database.

    Returns:
        True if the database is operational.

    Raises:
        sqlite3.Error: If the connection or query fails.
    """
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        return cursor.fetchone() is not None
