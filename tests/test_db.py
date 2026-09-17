"""Unit tests for taskpulse.db module."""

import os
from pathlib import Path
import pytest
from taskpulse.db import (
    DEFAULT_DB_FILENAME,
    ENV_DB_VARIABLE,
    check_connection,
    get_connection,
    get_db_path,
    init_db,
)


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


def test_init_db_creates_schema(tmp_path):
    """Test that init_db creates schema_version and tasks tables."""
    db_file = str(tmp_path / "test.db")
    init_db(db_file)

    assert os.path.exists(db_file)

    with get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row["name"] for row in cursor.fetchall()}
        assert "tasks" in tables
        assert "schema_version" in tables

        # Verify applied schema version
        cursor.execute("SELECT version FROM schema_version;")
        versions = [row["version"] for row in cursor.fetchall()]
        assert 1 in versions


def test_init_db_idempotent(tmp_path):
    """Test that running init_db multiple times does not raise errors."""
    db_file = str(tmp_path / "test_idempotent.db")
    init_db(db_file)
    init_db(db_file)  # Second run should succeed without error

    with get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM schema_version;")
        assert cursor.fetchone()["count"] == 1


def test_get_connection_commit(tmp_path):
    """Test that get_connection commits changes automatically on block exit."""
    db_file = str(tmp_path / "test_commit.db")
    init_db(db_file)

    with get_connection(db_file) as conn:
        conn.execute("INSERT INTO tasks (title) VALUES ('Commit test');")

    # Open fresh connection to verify data was persisted
    with get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM tasks WHERE title='Commit test';")
        row = cursor.fetchone()
        assert row is not None
        assert row["title"] == "Commit test"


def test_get_connection_rollback_on_exception(tmp_path):
    """Test that get_connection rolls back uncommitted changes on exception."""
    db_file = str(tmp_path / "test_rollback.db")
    init_db(db_file)

    with pytest.raises(RuntimeError):
        with get_connection(db_file) as conn:
            conn.execute("INSERT INTO tasks (title) VALUES ('Rollback test');")
            raise RuntimeError("Simulated failure inside transaction")

    with get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM tasks WHERE title='Rollback test';")
        assert cursor.fetchone() is None


def test_foreign_keys_pragma_enabled(tmp_path):
    """Test that PRAGMA foreign_keys is turned on."""
    db_file = str(tmp_path / "test_pragma.db")
    with get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys;")
        assert cursor.fetchone()[0] == 1


def test_check_connection_success(tmp_path):
    """Test that check_connection returns True for accessible database."""
    db_file = str(tmp_path / "test_healthy.db")
    assert check_connection(db_file) is True
