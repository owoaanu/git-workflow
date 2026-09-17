"""Unit tests for taskpulse.db module using SQLAlchemy 2.0."""

import os
from pathlib import Path
import pytest
from sqlalchemy import inspect, select, text
from taskpulse.db import (
    DEFAULT_DB_FILENAME,
    ENV_DB_VARIABLE,
    Task,
    check_connection,
    clear_engine_cache,
    get_database_url,
    get_db_path,
    get_session,
    init_db,
)


@pytest.fixture(autouse=True)
def clean_engines():
    """Ensure engine cache is cleared between tests."""
    yield
    clear_engine_cache()


def test_get_db_path_default(monkeypatch):
    """Test that get_db_path defaults to ~/.taskpulse.db when no env var is set."""
    monkeypatch.delenv(ENV_DB_VARIABLE, raising=False)
    expected = str(Path.home() / DEFAULT_DB_FILENAME)
    assert get_db_path() == expected


def test_get_db_path_custom_argument():
    """Test that explicit custom_path argument takes highest precedence."""
    custom = "/tmp/custom_test_taskpulse.db"
    assert get_db_path(custom) == str(Path(custom).resolve())


def test_get_db_path_env_var(monkeypatch, tmp_path):
    """Test that TASKPULSE_DB environment variable is respected."""
    env_db = str(tmp_path / "env_tasks.db")
    monkeypatch.setenv(ENV_DB_VARIABLE, env_db)
    assert get_db_path() == env_db


def test_get_database_url(tmp_path):
    """Test SQLite database URL generation."""
    db_file = str(tmp_path / "url_test.db")
    url = get_database_url(db_file)
    assert url == f"sqlite:///{db_file}"


def test_init_db_creates_schema(tmp_path):
    """Test that init_db creates the tasks table according to Base metadata."""
    db_file = str(tmp_path / "test.db")
    init_db(db_file)

    assert os.path.exists(db_file)

    with get_session(db_file) as session:
        inspector = inspect(session.bind)
        table_names = inspector.get_table_names()
        assert "tasks" in table_names

        columns = {col["name"]: col for col in inspector.get_columns("tasks")}
        assert "id" in columns
        assert "title" in columns
        assert "description" in columns
        assert "status" in columns
        assert "priority" in columns
        assert "created_at" in columns


def test_init_db_idempotent(tmp_path):
    """Test that running init_db multiple times succeeds without error."""
    db_file = str(tmp_path / "test_idempotent.db")
    init_db(db_file)
    init_db(db_file)

    with get_session(db_file) as session:
        result = session.scalars(select(Task)).all()
        assert result == []


def test_get_session_commit(tmp_path):
    """Test that get_session commits changes automatically on block exit."""
    db_file = str(tmp_path / "test_commit.db")
    init_db(db_file)

    with get_session(db_file) as session:
        task = Task(title="SQLAlchemy commit test")
        session.add(task)

    # Open fresh session to verify data was persisted
    with get_session(db_file) as session:
        stmt = select(Task).where(Task.title == "SQLAlchemy commit test")
        persisted_task = session.scalars(stmt).one_or_none()
        assert persisted_task is not None
        assert persisted_task.title == "SQLAlchemy commit test"
        assert persisted_task.status == "todo"
        assert persisted_task.priority == "medium"


def test_get_session_rollback_on_exception(tmp_path):
    """Test that get_session rolls back uncommitted changes on exception."""
    db_file = str(tmp_path / "test_rollback.db")
    init_db(db_file)

    with pytest.raises(RuntimeError):
        with get_session(db_file) as session:
            task = Task(title="Rollback task")
            session.add(task)
            raise RuntimeError("Simulated failure inside transaction")

    with get_session(db_file) as session:
        stmt = select(Task).where(Task.title == "Rollback task")
        assert session.scalars(stmt).one_or_none() is None


def test_foreign_keys_pragma_enabled(tmp_path):
    """Test that PRAGMA foreign_keys is turned on in SQLite."""
    db_file = str(tmp_path / "test_pragma.db")
    init_db(db_file)
    with get_session(db_file) as session:
        fk_status = session.execute(text("PRAGMA foreign_keys;")).scalar()
        assert fk_status == 1


def test_check_connection_success(tmp_path):
    """Test that check_connection returns True for accessible database."""
    db_file = str(tmp_path / "test_healthy.db")
    assert check_connection(db_file) is True


def test_task_model_methods():
    """Test Task model __repr__ and to_dict methods."""
    task = Task(
        id=42,
        title="Document 2.0 pattern",
        description="Write clear docs",
        status="todo",
        priority="high",
    )
    assert "<Task(id=42, title='Document 2.0 pattern', status='todo')>" in repr(task)
    data = task.to_dict()
    assert data["id"] == 42
    assert data["title"] == "Document 2.0 pattern"
    assert data["description"] == "Write clear docs"
    assert data["status"] == "todo"
    assert data["priority"] == "high"
