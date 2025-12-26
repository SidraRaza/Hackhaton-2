"""Unit tests for TodoService."""

import pytest
from src.services.todo_service import TodoService
from src.store.memory_store import TodoStore
from src.models.exceptions import TodoNotFoundError, ValidationError


@pytest.fixture
def service() -> TodoService:
    """Create a fresh TodoService for each test."""
    store = TodoStore()
    return TodoService(store)


class TestAddTodo:
    """Tests for TodoService.add_todo() method."""

    def test_add_todo_success(self, service: TodoService) -> None:
        """Test adding a todo with valid title."""
        todo = service.add_todo("Buy groceries")

        assert todo.id == 1
        assert todo.title == "Buy groceries"
        assert todo.completed is False

    def test_add_todo_strips_whitespace(self, service: TodoService) -> None:
        """Test that title whitespace is stripped."""
        todo = service.add_todo("  Test task  ")

        assert todo.title == "Test task"

    def test_add_todo_empty_title_raises(self, service: TodoService) -> None:
        """Test that empty title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            service.add_todo("")

        assert "Title cannot be empty" in str(exc_info.value)

    def test_add_todo_whitespace_title_raises(self, service: TodoService) -> None:
        """Test that whitespace-only title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            service.add_todo("   ")

        assert "Title cannot be empty" in str(exc_info.value)


class TestListTodos:
    """Tests for TodoService.list_todos() method."""

    def test_list_todos_empty(self, service: TodoService) -> None:
        """Test listing when no todos exist."""
        todos = service.list_todos()

        assert todos == []

    def test_list_todos_with_items(self, service: TodoService) -> None:
        """Test listing with todos."""
        service.add_todo("First")
        service.add_todo("Second")

        todos = service.list_todos()

        assert len(todos) == 2
        assert todos[0].title == "First"
        assert todos[1].title == "Second"


class TestCompleteTodo:
    """Tests for TodoService.complete_todo() method."""

    def test_complete_todo_success(self, service: TodoService) -> None:
        """Test completing an incomplete todo."""
        todo = service.add_todo("Test task")

        completed = service.complete_todo(todo.id)

        assert completed.completed is True

    def test_complete_todo_already_complete(self, service: TodoService) -> None:
        """Test completing an already complete todo."""
        todo = service.add_todo("Test task")
        service.complete_todo(todo.id)

        # Should not raise, just return the todo
        completed = service.complete_todo(todo.id)

        assert completed.completed is True

    def test_complete_todo_not_found(self, service: TodoService) -> None:
        """Test completing a non-existent todo."""
        with pytest.raises(TodoNotFoundError) as exc_info:
            service.complete_todo(99)

        assert exc_info.value.todo_id == 99


class TestUpdateTodo:
    """Tests for TodoService.update_todo() method."""

    def test_update_todo_success(self, service: TodoService) -> None:
        """Test updating a todo's title."""
        todo = service.add_todo("Original")

        updated = service.update_todo(todo.id, "Updated")

        assert updated.title == "Updated"

    def test_update_todo_empty_title_raises(self, service: TodoService) -> None:
        """Test that empty title raises ValidationError."""
        todo = service.add_todo("Original")

        with pytest.raises(ValidationError) as exc_info:
            service.update_todo(todo.id, "")

        assert "Title cannot be empty" in str(exc_info.value)

    def test_update_todo_not_found(self, service: TodoService) -> None:
        """Test updating a non-existent todo."""
        with pytest.raises(TodoNotFoundError) as exc_info:
            service.update_todo(99, "New title")

        assert exc_info.value.todo_id == 99


class TestDeleteTodo:
    """Tests for TodoService.delete_todo() method."""

    def test_delete_todo_success(self, service: TodoService) -> None:
        """Test deleting an existing todo."""
        todo = service.add_todo("To delete")

        result = service.delete_todo(todo.id)

        assert result is True
        assert service.list_todos() == []

    def test_delete_todo_not_found(self, service: TodoService) -> None:
        """Test deleting a non-existent todo."""
        with pytest.raises(TodoNotFoundError) as exc_info:
            service.delete_todo(99)

        assert exc_info.value.todo_id == 99
