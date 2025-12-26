"""CLI command handlers for the Todo application."""

import sys
from src.services.todo_service import TodoService
from src.models.exceptions import TodoNotFoundError, ValidationError


def handle_add(service: TodoService, title: str) -> int:
    """Handle the add command.

    Args:
        service: The TodoService instance.
        title: The title for the new todo.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        todo = service.add_todo(title)
        print(f'✓ Added todo #{todo.id}: "{todo.title}"')
        return 0
    except ValidationError as e:
        print(f"✗ Error: {e.message}", file=sys.stderr)
        return 1


def handle_list(service: TodoService) -> int:
    """Handle the list command.

    Args:
        service: The TodoService instance.

    Returns:
        Exit code (0 for success).
    """
    todos = service.list_todos()

    if not todos:
        print('No todos found. Add one with: todo add "Your task"')
        return 0

    print("ID  | Status     | Title")
    print("----|------------|" + "-" * 40)

    for todo in todos:
        status = "complete  " if todo.completed else "incomplete"
        print(f"{todo.id:<3} | {status} | {todo.title}")

    return 0


def handle_complete(service: TodoService, todo_id: int) -> int:
    """Handle the complete command.

    Args:
        service: The TodoService instance.
        todo_id: The ID of the todo to complete.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        todo = service.complete_todo(todo_id)
        if todo.completed:
            print(f'✓ Marked todo #{todo.id} as complete: "{todo.title}"')
        return 0
    except TodoNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def handle_update(service: TodoService, todo_id: int, title: str) -> int:
    """Handle the update command.

    Args:
        service: The TodoService instance.
        todo_id: The ID of the todo to update.
        title: The new title.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        todo = service.update_todo(todo_id, title)
        print(f'✓ Updated todo #{todo.id}: "{todo.title}"')
        return 0
    except TodoNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1
    except ValidationError as e:
        print(f"✗ Error: {e.message}", file=sys.stderr)
        return 1


def handle_delete(service: TodoService, todo_id: int) -> int:
    """Handle the delete command.

    Args:
        service: The TodoService instance.
        todo_id: The ID of the todo to delete.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        service.delete_todo(todo_id)
        print(f"✓ Deleted todo #{todo_id}")
        return 0
    except TodoNotFoundError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1
