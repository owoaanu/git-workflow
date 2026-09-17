"""Health-check subcommand for TaskPulse."""

import argparse
import sys
from taskpulse.db import check_connection, get_db_path


def register_subparser(
    subparsers: argparse._SubParsersAction,
) -> argparse.ArgumentParser:
    """Register the 'ping' subparser with argparse.

    Args:
        subparsers: Subparsers action object from the main CLI parser.

    Returns:
        The configured subparser instance for 'ping'.
    """
    parser = subparsers.add_parser(
        "ping",
        help="Check health status of TaskPulse CLI and SQLite database connectivity.",
        description=("Verifies that the CLI is functional and can connect to SQLite."),
    )
    parser.set_defaults(handler=execute)
    return parser


def execute(args: argparse.Namespace) -> int:
    """Execute the 'ping' command.

    Args:
        args: Parsed CLI namespace arguments.

    Returns:
        0 on success, 1 on failure.
    """
    db_path = getattr(args, "db", None)
    resolved_path = get_db_path(db_path)

    print("[INFO] Checking TaskPulse system health...")
    print(f"  - Database target: {resolved_path}")

    try:
        is_healthy = check_connection(db_path=resolved_path)
        if is_healthy:
            print(
                "[SUCCESS] CLI and SQLite database are fully connected and operational!"
            )
            return 0
        else:
            print(
                "[ERROR] Database health-check query returned no result.",
                file=sys.stderr,
            )
            return 1
    except Exception as exc:
        print(f"[ERROR] Failed to connect to SQLite database: {exc}", file=sys.stderr)
        return 1
