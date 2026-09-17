"""Data access and storage abstraction layer for TaskPulse.

Provides high-level CRUD operations on top of db.py, decoupling SQL queries
from CLI command handlers.
"""

from typing import Any, Dict, List, Optional
from taskpulse.db import get_connection, init_db

VALID_STATUSES = ("todo", "in_progress", "done")
VALID_PRIORITIES = ("low", "medium", "high")


def add_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    status: str = "todo",
    db_path: Optional[str] = None,
) -> int:
    """Insert a new task into the database.

    Args:
        title: Short title describing the task. Cannot be empty.
        description: Optional detailed notes.
        priority: Priority level ('low', 'medium', 'high'). Defaults to 'medium'.
        status: Initial status ('todo', 'in_progress', 'done'). Defaults to 'todo'.
        db_path: Optional SQLite database file path.

    Returns:
        The integer ID of the newly created task.

    Raises:
        ValueError: If title is empty or priority/status are invalid.
    """
    cleaned_title = title.strip() if title else ""
    if not cleaned_title:
        raise ValueError("Task title cannot be empty.")

    priority_lower = priority.lower().strip()
    if priority_lower not in VALID_PRIORITIES:
        valid_p = ", ".join(VALID_PRIORITIES)
        raise ValueError(f"Invalid priority '{priority}'. Must be one of: {valid_p}")

    status_lower = status.lower().strip()
    if status_lower not in VALID_STATUSES:
        valid_s = ", ".join(VALID_STATUSES)
        raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_s}")

    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (title, description, priority, status)
            VALUES (?, ?, ?, ?);
            """,
            (
                cleaned_title,
                description.strip() if description else None,
                priority_lower,
                status_lower,
            ),
        )
        task_id = cursor.lastrowid
        if task_id is None:
            raise RuntimeError("Failed to retrieve created task ID from database.")
        return task_id


def get_task(task_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a single task by its unique ID.

    Args:
        task_id: The ID of the task to fetch.
        db_path: Optional SQLite database file path.

    Returns:
        A dictionary representation of the task, or None if not found.
    """
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, description, status, priority, created_at
            FROM tasks
            WHERE id = ?;
            """,
            (task_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


# ============================================================================
# INTERN STARTER TASKS: Storage Layer Hooks
# ============================================================================


def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List tasks, optionally filtered by status and/or priority.

    TODO (Intern Task 1):
    1. Validate status/priority arguments if provided.
    2. Build query with optional WHERE filters.
    3. Return a list of task dictionaries ordered by id ascending.

    Example implementation starter:
        init_db(db_path)
        with get_connection(db_path) as conn:
            query = (
                "SELECT id, title, description, status, priority, created_at "
                "FROM tasks"
            )
            params = []
            ...
    """
    raise NotImplementedError(
        "list_tasks() is a starter task for interns! "
        "See CONTRIBUTING.md for instructions."
    )


def update_task_status(
    task_id: int,
    status: str,
    db_path: Optional[str] = None,
) -> bool:
    """Update the status of an existing task.

    TODO (Intern Task 2):
    1. Validate that status is in VALID_STATUSES.
    2. Execute: UPDATE tasks SET status = ? WHERE id = ?
    3. Return True if a row was updated (cursor.rowcount > 0), False otherwise.
    """
    raise NotImplementedError(
        "update_task_status() is a starter task for interns! "
        "See CONTRIBUTING.md for instructions."
    )


def delete_task(task_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a task by its ID.

    TODO (Intern Task 3):
    1. Execute: DELETE FROM tasks WHERE id = ?
    2. Return True if a row was deleted (cursor.rowcount > 0), False otherwise.
    """
    raise NotImplementedError(
        "delete_task() is a starter task for interns! "
        "See CONTRIBUTING.md for instructions."
    )
