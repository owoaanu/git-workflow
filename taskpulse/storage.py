"""Data access and storage abstraction layer for TaskPulse using SQLAlchemy 2.0.

Provides high-level CRUD operations on top of db.py and the Task model,
decoupling SQLAlchemy 2.0 queries from CLI command handlers.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy import select
from taskpulse.db import Task, get_session, init_db

VALID_STATUSES = ("todo", "in_progress", "done")
VALID_PRIORITIES = ("low", "medium", "high")


def add_task(
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    status: str = "todo",
    db_path: Optional[str] = None,
) -> int:
    """Insert a new task into the database using SQLAlchemy 2.0.

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
    with get_session() as session:
        task = Task(
            title=cleaned_title,
            description=description.strip() if description else None,
            priority=priority_lower,
            status=status_lower,
        )
        session.add(task)
        return task.id


def get_task(task_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a single task by its unique ID using SQLAlchemy 2.0 select.

    Args:
        task_id: The ID of the task to fetch.
        db_path: Optional SQLite database file path.

    Returns:
        A dictionary representation of the task, or None if not found.
    """
    init_db(db_path)
    with get_session(db_path) as session:
        stmt = select(Task).where(Task.id == task_id)
        task = session.scalars(stmt).one_or_none()
        return task.to_dict() if task else None


# ============================================================================
# INTERN STARTER TASKS: Storage Layer Hooks (SQLAlchemy 2.0)
# ============================================================================


def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List tasks, optionally filtered by status and/or priority.

    TODO (Intern Task 1 - SQLAlchemy 2.0 query):
    1. Initialize db and open a session:
           init_db(db_path)
           with get_session(db_path) as session:
    2. Build SQLAlchemy 2.0 select statement:
           stmt = select(Task)
           if status:
               stmt = stmt.where(Task.status == status.lower().strip())
           if priority:
               stmt = stmt.where(Task.priority == priority.lower().strip())
    3. Order by ID and execute:
           tasks = session.scalars(stmt.order_by(Task.id)).all()
           return [t.to_dict() for t in tasks]
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

    TODO (Intern Task 2 - SQLAlchemy 2.0 update):
    1. Validate that status is in VALID_STATUSES.
    2. Fetch task via session.get(Task, task_id).
    3. If task is None, return False.
    4. Update attribute: task.status = status.lower().strip()
    5. Return True (session commits automatically on context manager exit).
    """
    raise NotImplementedError(
        "update_task_status() is a starter task for interns! "
        "See CONTRIBUTING.md for instructions."
    )


def delete_task(task_id: int, db_path: Optional[str] = None) -> bool:
    """Delete a task by its ID.

    TODO (Intern Task 3 - SQLAlchemy 2.0 delete):
    1. Fetch task via session.get(Task, task_id).
    2. If task is None, return False.
    3. Delete object: session.delete(task)
    4. Return True (session commits automatically on context manager exit).
    """
    raise NotImplementedError(
        "delete_task() is a starter task for interns! "
        "See CONTRIBUTING.md for instructions."
    )
