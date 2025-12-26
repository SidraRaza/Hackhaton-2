"""Integration tests for the Todo CLI."""

import pytest
from io import StringIO
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

from src.main import main, create_parser
from src.services.todo_service import TodoService
from src.store.memory_store import TodoStore
from src.cli.commands import (
    handle_add,
    handle_list,
    handle_complete,
    handle_update,
    handle_delete,
)


@pytest.fixture
def service(tmp_path: Path) -> TodoService:
    """Create a fresh TodoService with temporary storage for each test."""
    file_path = tmp_path / "test_todos.json"
    store = TodoStore(file_path=file_path)
    return TodoService(store)


class TestAddCommand:
    """Integration tests for the add command."""

    def test_add_command_success(self, service: TodoService) -> None:
        """Test adding a todo via CLI."""
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = handle_add(service, "Buy groceries")

        assert exit_code == 0
        assert "[+] Added todo #1" in stdout.getvalue()
        assert "Buy groceries" in stdout.getvalue()

    def test_add_command_empty_title(self, service: TodoService) -> None:
        """Test adding a todo with empty title."""
        stderr = StringIO()
        with redirect_stderr(stderr):
            exit_code = handle_add(service, "")

        assert exit_code == 1
        assert "Title cannot be empty" in stderr.getvalue()


class TestListCommand:
    """Integration tests for the list command."""

    def test_list_command_empty(self, service: TodoService) -> None:
        """Test listing when no todos exist."""
        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = handle_list(service)

        assert exit_code == 0
        assert "No todos found" in stdout.getvalue()

    def test_list_command_with_todos(self, service: TodoService) -> None:
        """Test listing with todos."""
        service.add_todo("First task")
        service.add_todo("Second task")

        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = handle_list(service)

        output = stdout.getvalue()
        assert exit_code == 0
        assert "First task" in output
        assert "Second task" in output
        assert "incomplete" in output


class TestCompleteCommand:
    """Integration tests for the complete command."""

    def test_complete_command_success(self, service: TodoService) -> None:
        """Test completing a todo via CLI."""
        todo = service.add_todo("Test task")

        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = handle_complete(service, todo.id)

        assert exit_code == 0
        assert "[+] Marked todo #1 as complete" in stdout.getvalue()

    def test_complete_command_not_found(self, service: TodoService) -> None:
        """Test completing a non-existent todo."""
        stderr = StringIO()
        with redirect_stderr(stderr):
            exit_code = handle_complete(service, 99)

        assert exit_code == 1
        assert "not found" in stderr.getvalue()


class TestUpdateCommand:
    """Integration tests for the update command."""

    def test_update_command_success(self, service: TodoService) -> None:
        """Test updating a todo via CLI."""
        todo = service.add_todo("Original")

        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = handle_update(service, todo.id, "Updated")

        assert exit_code == 0
        assert "[+] Updated todo #1" in stdout.getvalue()

    def test_update_command_not_found(self, service: TodoService) -> None:
        """Test updating a non-existent todo."""
        stderr = StringIO()
        with redirect_stderr(stderr):
            exit_code = handle_update(service, 99, "New title")

        assert exit_code == 1
        assert "not found" in stderr.getvalue()

    def test_update_command_empty_title(self, service: TodoService) -> None:
        """Test updating with empty title."""
        todo = service.add_todo("Original")

        stderr = StringIO()
        with redirect_stderr(stderr):
            exit_code = handle_update(service, todo.id, "")

        assert exit_code == 1
        assert "Title cannot be empty" in stderr.getvalue()


class TestDeleteCommand:
    """Integration tests for the delete command."""

    def test_delete_command_success(self, service: TodoService) -> None:
        """Test deleting a todo via CLI."""
        todo = service.add_todo("To delete")

        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = handle_delete(service, todo.id)

        assert exit_code == 0
        assert "[+] Deleted todo #1" in stdout.getvalue()

    def test_delete_command_not_found(self, service: TodoService) -> None:
        """Test deleting a non-existent todo."""
        stderr = StringIO()
        with redirect_stderr(stderr):
            exit_code = handle_delete(service, 99)

        assert exit_code == 1
        assert "not found" in stderr.getvalue()


class TestParserConfiguration:
    """Tests for argument parser configuration."""

    def test_parser_has_all_commands(self) -> None:
        """Test that all commands are registered."""
        parser = create_parser()

        # Parse known commands to verify they exist
        args = parser.parse_args(["add", "test"])
        assert args.command == "add"

        args = parser.parse_args(["list"])
        assert args.command == "list"

        args = parser.parse_args(["complete", "1"])
        assert args.command == "complete"

        args = parser.parse_args(["update", "1", "new"])
        assert args.command == "update"

        args = parser.parse_args(["delete", "1"])
        assert args.command == "delete"
