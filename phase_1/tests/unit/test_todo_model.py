"""Unit tests for Todo model."""

import pytest
from src.models.todo import Todo


class TestTodoModel:
    """Tests for the Todo dataclass."""

    def test_create_todo_with_all_fields(self) -> None:
        """Test creating a todo with all fields specified."""
        todo = Todo(id=1, title="Buy groceries", completed=False)

        assert todo.id == 1
        assert todo.title == "Buy groceries"
        assert todo.completed is False

    def test_create_todo_with_default_completed(self) -> None:
        """Test that completed defaults to False."""
        todo = Todo(id=1, title="Test task")

        assert todo.completed is False

    def test_create_completed_todo(self) -> None:
        """Test creating a completed todo."""
        todo = Todo(id=1, title="Done task", completed=True)

        assert todo.completed is True

    def test_todo_equality(self) -> None:
        """Test that todos with same values are equal."""
        todo1 = Todo(id=1, title="Test", completed=False)
        todo2 = Todo(id=1, title="Test", completed=False)

        assert todo1 == todo2

    def test_todo_inequality(self) -> None:
        """Test that todos with different values are not equal."""
        todo1 = Todo(id=1, title="Test", completed=False)
        todo2 = Todo(id=2, title="Test", completed=False)

        assert todo1 != todo2
