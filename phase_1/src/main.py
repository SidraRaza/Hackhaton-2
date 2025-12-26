"""Main entry point for the Todo CLI application."""

import argparse
import sys

from src.services.todo_service import TodoService
from src.store import store
from src.cli.commands import (
    handle_add,
    handle_list,
    handle_complete,
    handle_update,
    handle_delete,
)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Todo CLI - Manage your tasks from the command line",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("title", help="The todo title")

    # List command
    subparsers.add_parser("list", help="List all todos")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark a todo as complete")
    complete_parser.add_argument("id", type=int, help="The todo ID")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a todo's title")
    update_parser.add_argument("id", type=int, help="The todo ID")
    update_parser.add_argument("title", help="The new title")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a todo")
    delete_parser.add_argument("id", type=int, help="The todo ID")

    return parser


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    service = TodoService(store)

    match args.command:
        case "add":
            return handle_add(service, args.title)
        case "list":
            return handle_list(service)
        case "complete":
            return handle_complete(service, args.id)
        case "update":
            return handle_update(service, args.id, args.title)
        case "delete":
            return handle_delete(service, args.id)
        case _:
            parser.print_help()
            return 1


if __name__ == "__main__":
    sys.exit(main())
