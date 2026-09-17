"""Pluggable CLI subcommands for TaskPulse.

Each subcommand module is expected to define:
- register_subparser(subparsers): Configures an argparse subparser.
- execute(args) -> int: Executes the command logic and returns an exit code.
"""
