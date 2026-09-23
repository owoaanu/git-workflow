"""List command for TaskPulse."""

import argparse

from taskpulse.storage import list_tasks


def register_subparser(
    subparsers: argparse._SubParsersAction,
) -> argparse.ArgumentParser:
    """Register the 'list' subcommand with argparse."""
    parser = subparsers.add_parser(
        "list",
        help="List all tasks.",
        description="List TaskPulse tasks with optional filters.",
    )

    parser.add_argument(
        "--status",
        "-s",
        choices=["todo", "in_progress", "done"],
        help="Filter tasks by status.",
    )

    parser.add_argument(
        "--priority",
        "-p",
        choices=["low", "medium", "high"],
        help="Filter tasks by priority.",
    )

    parser.set_defaults(handler=execute)

    return parser


def execute(args: argparse.Namespace) -> int:
    """Execute the 'list' command."""

    
    tasks = list_tasks(
        status=args.status,
        priority=args.priority,
        db_path=getattr(args, "db", None),
    )

    if not tasks:
        print("No tasks found.")
        return 1

    print(f"{"ID":<3} | {"STATUS":<8} | {"PRIORITY":<10} | TITLE")
    print("-" * 40)

    for task in tasks:
        print(
            f"{task['id']:<3} | "
            f"{task['status']:<8} | "
            f"{task['priority']:<10} | "
            f"{task['title']}"
        )

    return 0