"""Unit tests for TodoStore."""

import pytest
from src.store.memory_store import TodoStore
from src.models.exceptions import TodoNotFoundError


class TestTodoStoreInitialization:
    """Tests for TodoStore initialization."""

    def test_store_initializes_empty(self) -> None:
        """Test that a new store has no todos."""
        store = TodoStore()

        assert store.get_all() == []

    def test_store_starts_id_at_one(self) -> None:
        """Test that the first todo gets ID 1."""
        store = TodoStore()
        todo = store.add("First todo")

        assert todo.id == 1


class TestTodoStoreAdd:
    """Tests for TodoStore.add() method."""

    def test_add_returns_todo_with_id(self) -> None:
        """Test that add returns a todo with generated ID."""
        store = TodoStore()
        todo = store.add("Test todo")

        assert todo.id == 1
        assert todo.title == "Test todo"
        assert todo.completed is False

    def test_add_increments_id(self) -> None:
        """Test that IDs increment for each added todo."""
        store = TodoStore()
        todo1 = store.add("First")
        todo2 = store.add("Second")

        assert todo1.id == 1
        assert todo2.id == 2


class TestTodoStoreGet:
    """Tests for TodoStore.get() method."""

    def test_get_returns_existing_todo(self) -> None:
        """Test that get returns the correct todo."""
        store = TodoStore()
        added = store.add("Test")

        retrieved = store.get(added.id)

        assert retrieved == added

    def test_get_raises_for_nonexistent_id(self) -> None:
        """Test that get raises TodoNotFoundError for missing ID."""
        store = TodoStore()

        with pytest.raises(TodoNotFoundError) as exc_info:
            store.get(99)

        assert exc_info.value.todo_id == 99


class TestTodoStoreGetAll:
    """Tests for TodoStore.get_all() method."""

    def test_get_all_returns_all_todos(self) -> None:
        """Test that get_all returns all todos."""
        store = TodoStore()
        store.add("First")
        store.add("Second")

        todos = store.get_all()

        assert len(todos) == 2

    def test_get_all_returns_sorted_by_id(self) -> None:
        """Test that get_all returns todos sorted by ID."""
        store = TodoStore()
        store.add("First")
        store.add("Second")
        store.add("Third")

        todos = store.get_all()

        assert [t.id for t in todos] == [1, 2, 3]
