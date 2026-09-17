"""Unit tests for taskpulse.storage module."""

import pytest
from taskpulse.storage import (
    add_task,
    delete_task,
    get_task,
    list_tasks,
    update_task_status,
)


def test_add_task_minimal(tmp_path):
    """Test adding a task with only a title."""
    db_file = str(tmp_path / "test_tasks.db")
    task_id = add_task(title="Write unit tests", db_path=db_file)
    assert isinstance(task_id, int)
    assert task_id >= 1

    task = get_task(task_id, db_path=db_file)
    assert task is not None
    assert task["id"] == task_id
    assert task["title"] == "Write unit tests"
    assert task["description"] is None
    assert task["priority"] == "medium"
    assert task["status"] == "todo"
    assert "created_at" in task


def test_add_task_full(tmp_path):
    """Test adding a task with description and custom priority."""
    db_file = str(tmp_path / "test_tasks.db")
    task_id = add_task(
        title="Setup CI",
        description="Configure GitHub Actions workflow for lint and test",
        priority="high",
        status="in_progress",
        db_path=db_file,
    )

    task = get_task(task_id, db_path=db_file)
    assert task is not None
    assert task["title"] == "Setup CI"
    assert task["description"] == "Configure GitHub Actions workflow for lint and test"
    assert task["priority"] == "high"
    assert task["status"] == "in_progress"


def test_add_task_empty_title(tmp_path):
    """Test that adding a task with an empty or whitespace title raises ValueError."""
    db_file = str(tmp_path / "test_tasks.db")
    with pytest.raises(ValueError, match="Task title cannot be empty"):
        add_task(title="", db_path=db_file)

    with pytest.raises(ValueError, match="Task title cannot be empty"):
        add_task(title="   ", db_path=db_file)


def test_add_task_invalid_priority(tmp_path):
    """Test that adding a task with an invalid priority raises ValueError."""
    db_file = str(tmp_path / "test_tasks.db")
    with pytest.raises(ValueError, match="Invalid priority"):
        add_task(title="Test", priority="urgent", db_path=db_file)


def test_add_task_invalid_status(tmp_path):
    """Test that adding a task with an invalid status raises ValueError."""
    db_file = str(tmp_path / "test_tasks.db")
    with pytest.raises(ValueError, match="Invalid status"):
        add_task(title="Test", status="completed", db_path=db_file)


def test_get_nonexistent_task(tmp_path):
    """Test that fetching a nonexistent task ID returns None."""
    db_file = str(tmp_path / "test_tasks.db")
    result = get_task(99999, db_path=db_file)
    assert result is None


def test_starter_stubs_raise_not_implemented(tmp_path):
    """Test that starter stubs for interns raise NotImplementedError."""
    db_file = str(tmp_path / "test_tasks.db")
    with pytest.raises(NotImplementedError, match="list_tasks"):
        list_tasks(db_path=db_file)

    with pytest.raises(NotImplementedError, match="update_task_status"):
        update_task_status(1, "done", db_path=db_file)

    with pytest.raises(NotImplementedError, match="delete_task"):
        delete_task(1, db_path=db_file)
