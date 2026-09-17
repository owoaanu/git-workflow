"""Unit tests for TaskPulse CLI commands (ping, add) and main CLI entrypoint."""

import pytest
from taskpulse import __version__
from taskpulse.cli import main
from taskpulse.storage import get_task


def test_cli_help(capsys):
    """Test running CLI without arguments displays usage help."""
    exit_code = main([])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "TaskPulse: A clean, modular CLI task manager" in captured.out
    assert "Available Subcommands" in captured.out


def test_cli_version(capsys):
    """Test running CLI with --version displays version."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_ping_command(tmp_path, capsys):
    """Test the ping health-check command with a custom database."""
    db_file = str(tmp_path / "ping_test.db")
    exit_code = main(["--db", db_file, "ping"])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "[INFO] Checking TaskPulse system health..." in captured.out
    assert (
        "[SUCCESS] CLI and SQLite database are fully connected and operational!"
        in captured.out
    )
    assert db_file in captured.out


def test_add_command_basic(tmp_path, capsys):
    """Test adding a basic task with only a title."""
    db_file = str(tmp_path / "add_test.db")
    exit_code = main(["--db", db_file, "add", "Submit weekly report"])
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "[SUCCESS] Task #1 created successfully!" in captured.out
    assert "Submit weekly report" in captured.out
    assert "Priority:    medium" in captured.out

    # Verify task was written to DB
    task = get_task(1, db_path=db_file)
    assert task is not None
    assert task["title"] == "Submit weekly report"
    assert task["priority"] == "medium"
    assert task["status"] == "todo"


def test_add_command_full_options(tmp_path, capsys):
    """Test adding a task with description and priority."""
    db_file = str(tmp_path / "add_full_test.db")
    exit_code = main(
        [
            "--db",
            db_file,
            "add",
            "Refactor auth service",
            "--desc",
            "Migrate tokens to JWT",
            "--priority",
            "high",
        ]
    )
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "[SUCCESS] Task #1 created successfully!" in captured.out
    assert "Refactor auth service" in captured.out
    assert "Description: Migrate tokens to JWT" in captured.out
    assert "Priority:    high" in captured.out

    task = get_task(1, db_path=db_file)
    assert task is not None
    assert task["title"] == "Refactor auth service"
    assert task["description"] == "Migrate tokens to JWT"
    assert task["priority"] == "high"


def test_add_command_empty_title_validation(tmp_path, capsys):
    """Test adding a task with empty whitespace title fails gracefully."""
    db_file = str(tmp_path / "add_empty.db")
    exit_code = main(["--db", db_file, "add", "   "])
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "[ERROR] Validation failed: Task title cannot be empty." in captured.err


def test_add_command_invalid_priority(tmp_path):
    """Test adding a task with an invalid priority is rejected by argparse."""
    db_file = str(tmp_path / "add_invalid_priority.db")
    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "--db",
                db_file,
                "add",
                "Invalid Priority Task",
                "--priority",
                "super_critical",
            ]
        )
    # Argparse exits with code 2 on invalid choice
    assert exc_info.value.code == 2


def test_ping_command_failure_handling(tmp_path, capsys, monkeypatch):
    """Test ping command handles database connection errors gracefully."""
    db_file = str(tmp_path / "ping_fail.db")

    def mock_check_fail(db_path=None):
        raise RuntimeError("Disk I/O failure")

    monkeypatch.setattr("taskpulse.commands.ping.check_connection", mock_check_fail)

    exit_code = main(["--db", db_file, "ping"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "[ERROR] Failed to connect to SQLite database" in captured.err


def test_ping_command_false_result(tmp_path, capsys, monkeypatch):
    """Test ping command handles False return from check_connection."""
    db_file = str(tmp_path / "ping_false.db")

    monkeypatch.setattr(
        "taskpulse.commands.ping.check_connection", lambda db_path=None: False
    )

    exit_code = main(["--db", db_file, "ping"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "[ERROR] Database health-check query returned no result." in captured.err


def test_add_command_unexpected_exception(tmp_path, capsys, monkeypatch):
    """Test add command handles unexpected storage errors gracefully."""
    db_file = str(tmp_path / "add_err.db")

    def mock_add_fail(**kwargs):
        raise RuntimeError("Disk full")

    monkeypatch.setattr("taskpulse.commands.add.add_task", mock_add_fail)

    exit_code = main(["--db", db_file, "add", "Test task"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "[ERROR] Failed to create task: Disk full" in captured.err
