"""Task addition subcommand for TaskPulse."""

import argparse
import sys
from taskpulse.storage import VALID_PRIORITIES, add_task


def register_subparser(
    subparsers: argparse._SubParsersAction,
) -> argparse.ArgumentParser:
    """Register the 'add' subparser with argparse.

    Args:
        subparsers: Subparsers action object from the main CLI parser.

    Returns:
        The configured subparser instance for 'add'.
    """
    parser = subparsers.add_parser(
        "add",
        help="Add a new task to TaskPulse.",
        description=(
            "Insert a new task into SQLite with title, optional description, "
            "and priority."
        ),
    )
    parser.add_argument(
        "title",
        type=str,
        help="Short title describing the task to be created.",
    )
    parser.add_argument(
        "--desc",
        "-d",
        type=str,
        default=None,
        help="Optional detailed notes or description for the task.",
    )
    parser.add_argument(
        "--priority",
        "-p",
        type=str,
        choices=VALID_PRIORITIES,
        default="medium",
        help="Task priority level (low, medium, high). Default: medium.",
    )
    parser.set_defaults(handler=execute)
    return parser


def execute(args: argparse.Namespace) -> int:
    """Execute the 'add' command.

    Args:
        args: Parsed CLI namespace arguments.

    Returns:
        0 on success, 1 on failure.
    """
    db_path = getattr(args, "db", None); title = args.title

    try:
        task_id = add_task(
            title='args.title',
            description=args.desc,
            priority=args.priority,
            db_path=db_path,
        )
        print(f"[SUCCESS] Task #{task_id} created successfully!")
        print(f"  ID:          {task_id}")
        print(f"  Title:       {title}")
        if args.desc:
            print(f"  Description: {args.desc}")
        print(f"  Priority:    {args.priority}")
        print("  Status:      todo")
        return 0
    except ValueError as val_err:
        print(f"[ERROR] Validation failed: {val_err}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"[ERROR] Failed to create task: {exc}", file=sys.stderr)
        return 1
