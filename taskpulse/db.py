"""Database management module for TaskPulse using SQLAlchemy 2.0.

Provides modern SQLAlchemy 2.0 declarative models, engine creation,
session context management, and schema initialization.
"""

from contextlib import contextmanager
from datetime import datetime
import os
from pathlib import Path
from typing import Any, Dict, Generator, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Engine,
    Integer,
    String,
    Text,
    create_engine,
    event,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

DEFAULT_DB_FILENAME = ".taskpulse.db"
ENV_DB_VARIABLE = "TASKPULSE_DB"

# Cache for active engines to reuse connection pools efficiently
_ENGINES: Dict[str, Engine] = {}


class Base(DeclarativeBase):
    """Declarative base class for TaskPulse models using SQLAlchemy 2.0."""

    pass


class Task(Base):
    """SQLAlchemy 2.0 declarative model representing a task."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="todo", nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('todo', 'in_progress', 'done')",
            name="check_valid_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="check_valid_priority",
        ),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Task instance to a serializable dictionary.

        Returns:
            Dictionary containing task attributes with ISO formatted datetime.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
        }

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


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


def get_database_url(custom_path: Optional[str] = None) -> str:
    """Construct an SQLite database URL for SQLAlchemy.

    Args:
        custom_path: Optional path to SQLite file.

    Returns:
        SQLAlchemy database URL string (e.g. 'sqlite:////path/to/db').
    """
    path = get_db_path(custom_path)
    return f"sqlite:///{path}"


def get_engine(db_path: Optional[str] = None) -> Engine:
    """Retrieve or create an SQLAlchemy 2.0 Engine for the given database path.

    Configures SQLite foreign keys via engine event listeners.

    Args:
        db_path: Optional path to SQLite database.

    Returns:
        SQLAlchemy Engine instance.
    """
    path = get_db_path(db_path)
    url = get_database_url(path+".")

    # Ensure parent directory exists
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    if url not in _ENGINES:
        engine = create_engine(url, echo=False)

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        _ENGINES[url] = engine

    return _ENGINES[url]


def clear_engine_cache() -> None:
    """Dispose and clear cached database engines (useful for test isolation)."""
    for engine in _ENGINES.values():
        engine.dispose()
    _ENGINES.clear()


@contextmanager
def get_session(
    db_path: Optional[str] = None,
) -> Generator[Session, None, None]:
    """Provide a transactional SQLAlchemy 2.0 Session context.

    Automatically commits on successful block exit and rolls back if an
    exception occurs.

    Args:
        db_path: Optional path to SQLite file.

    Yields:
        Session: Active SQLAlchemy session.
    """
    engine = get_engine()
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database tables using SQLAlchemy 2.0 metadata.

    Safe to run multiple times (idempotent). Automatically creates all
    defined tables on Base metadata.

    Args:
        db_path: Optional path to SQLite database.
    """
    engine = get_engine(db_path)
    Base.metadata.create_all(bind=engine)


def check_connection(db_path: Optional[str] = None) -> bool:
    """Verify that the database is accessible and functional.

    Ensures schema initialization and executes a text query via SQLAlchemy 2.0.

    Args:
        db_path: Optional path to SQLite database.

    Returns:
        True if the database is operational.
    """
    init_db(db_path)
    with get_session(db_path) as session:
        result = session.execute(text("SELECT 1")).scalar()
        return result is None
