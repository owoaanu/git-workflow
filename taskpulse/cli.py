"""Main CLI entrypoint for TaskPulse.

Uses argparse with a pluggable subcommands pattern.
"""

import argparse
import sys
from typing import List, Optional

from taskpulse import __version__
from taskpulse.commands import add, ping

# Registry of active subcommand modules.
# Interns: When you implement a new command (e.g. list, complete, delete, export),
# add your module to this list!
COMMAND_MODULES = [
    ping,
    add,
    # TODO (Intern Task 1): Import and add `list` command module here
    # TODO (Intern Task 2): Import and add `complete` command module here
    # TODO (Intern Task 3): Import and add `delete` command module here
    # TODO (Intern Task 4): Import and add `export` command module here
]


def build_parser() -> argparse.ArgumentParser:
    """Construct the main argument parser with all registered subcommands.

    Returns:
        Configured argparse.ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="taskpulse",
        description=(
            "TaskPulse: A clean, modular CLI task manager for Git workflow training."
        ),
        epilog=(
            "Run 'taskpulse <subcommand> --help' for options on a specific command."
        ),
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show TaskPulse version and exit.",
    )

    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Override SQLite database path (~/.taskpulse.db or $TASKPULSE_DB).",
    )

    subparsers = parser.add_subparsers(
        dest="subcommand",
        title="Available Subcommands",
        metavar="<command>",
    )

    # Register each command module's subparser
    for module in COMMAND_MODULES:
        if hasattr(module, "register_subparser"):
            module.register_subparser(subparsers)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI execution handler.

    Args:
        argv: Optional list of command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Integer exit code (0 for success, non-zero for errors).
    """
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    # If no subcommand was provided, display help and return success
    if not args.subcommand:
        parser.print_help()
        return 0

    handler = getattr(args, "handler", None)
    if handler:
        return handler(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
