"""Task Status Update subcommand for TaskPulse."""

import argparse
import sys
from taskpulse.storage import VALID_STATUSES, update_task_status


def register_subparser(
    subparsers: argparse._SubParsersAction,
) -> argparse.ArgumentParser:
    """Register the 'complete' subparser with argparse.

    Args:
        subparsers: Subparsers action object from the main CLI parser.

    Returns:
        The configured subparser instance for 'complete'.
    """
    parser = subparsers.add_parser(
        "complete",
        help="Update task status in TaskPulse.",
        description=(
            "Update an existing task within SQLite with task_id, this updates the task status to done."
        ),
    )
    parser.add_argument(
        "task_id",
        type=int,
        help="The id of task to be updated.",
    )
    # parser.add_argument(
    #         "--status",
    #         "-s",
    #         type=str,
    #         choices=VALID_STATUSES,
    #         default="todo",
    #         help="Task status level (todo, in_progress, done). Default: medium.",
    #     )
    parser.set_defaults(handler=execute)
    return parser


def execute(args: argparse.Namespace) -> int:
    """Execute the 'complete' command.

    Args:
        args: Parsed CLI namespace arguments.

    Returns:
        0 on success, 1 on failure.
    """
    db_path = getattr(args, "db", None)

    try:
        response = update_task_status(
            task_id=args.task_id, # reverted to variable from string
            status="done",
            db_path=db_path,
        )
        if response:
            print(f"[SUCCESS] Task #{args.task_id} marked as done!")
            return 0
        else:
            print(f"[ERROR] Task #{args.task_id} does not exist!")
            return 1
    except ValueError as val_err:
        print(f"[ERROR] Validation failed: {val_err}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"[ERROR] Failed to update task: {exc}", file=sys.stderr)
        return 1
