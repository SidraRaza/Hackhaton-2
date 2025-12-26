"""Unit tests for TodoStore."""

import pytest
from pathlib import Path
from src.store.memory_store import TodoStore
from src.models.exceptions import TodoNotFoundError


@pytest.fixture
def temp_store(tmp_path: Path) -> TodoStore:
    """Create a TodoStore with a temporary file for testing."""
    file_path = tmp_path / "test_todos.json"
    return TodoStore(file_path=file_path)


@pytest.fixture
def temp_file_path(tmp_path: Path) -> Path:
    """Provide a temporary file path for persistence tests."""
    return tmp_path / "test_todos.json"


class TestTodoStoreInitialization:
    """Tests for TodoStore initialization."""

    def test_store_initializes_empty(self, temp_store: TodoStore) -> None:
        """Test that a new store has no todos."""
        assert temp_store.get_all() == []

    def test_store_starts_id_at_one(self, temp_store: TodoStore) -> None:
        """Test that the first todo gets ID 1."""
        todo = temp_store.add("First todo")

        assert todo.id == 1


class TestTodoStoreAdd:
    """Tests for TodoStore.add() method."""

    def test_add_returns_todo_with_id(self, temp_store: TodoStore) -> None:
        """Test that add returns a todo with generated ID."""
        todo = temp_store.add("Test todo")

        assert todo.id == 1
        assert todo.title == "Test todo"
        assert todo.completed is False

    def test_add_increments_id(self, temp_store: TodoStore) -> None:
        """Test that IDs increment for each added todo."""
        todo1 = temp_store.add("First")
        todo2 = temp_store.add("Second")

        assert todo1.id == 1
        assert todo2.id == 2


class TestTodoStoreGet:
    """Tests for TodoStore.get() method."""

    def test_get_returns_existing_todo(self, temp_store: TodoStore) -> None:
        """Test that get returns the correct todo."""
        added = temp_store.add("Test")

        retrieved = temp_store.get(added.id)

        assert retrieved == added

    def test_get_raises_for_nonexistent_id(self, temp_store: TodoStore) -> None:
        """Test that get raises TodoNotFoundError for missing ID."""
        with pytest.raises(TodoNotFoundError) as exc_info:
            temp_store.get(99)

        assert exc_info.value.todo_id == 99


class TestTodoStoreGetAll:
    """Tests for TodoStore.get_all() method."""

    def test_get_all_returns_all_todos(self, temp_store: TodoStore) -> None:
        """Test that get_all returns all todos."""
        temp_store.add("First")
        temp_store.add("Second")

        todos = temp_store.get_all()

        assert len(todos) == 2

    def test_get_all_returns_sorted_by_id(self, temp_store: TodoStore) -> None:
        """Test that get_all returns todos sorted by ID."""
        temp_store.add("First")
        temp_store.add("Second")
        temp_store.add("Third")

        todos = temp_store.get_all()

        assert [t.id for t in todos] == [1, 2, 3]


class TestTodoStorePersistence:
    """Tests for TodoStore file persistence."""

    def test_todos_persist_across_instances(self, temp_file_path: Path) -> None:
        """Test that todos are saved and loaded correctly."""
        # Create store and add todos
        store1 = TodoStore(file_path=temp_file_path)
        store1.add("Persistent todo")
        store1.add("Another todo")

        # Create new store instance with same file
        store2 = TodoStore(file_path=temp_file_path)

        todos = store2.get_all()
        assert len(todos) == 2
        assert todos[0].title == "Persistent todo"
        assert todos[1].title == "Another todo"

    def test_next_id_persists(self, temp_file_path: Path) -> None:
        """Test that next_id is preserved across instances."""
        store1 = TodoStore(file_path=temp_file_path)
        store1.add("First")
        store1.add("Second")

        store2 = TodoStore(file_path=temp_file_path)
        todo3 = store2.add("Third")

        assert todo3.id == 3

    def test_delete_persists(self, temp_file_path: Path) -> None:
        """Test that deletions are persisted."""
        store1 = TodoStore(file_path=temp_file_path)
        store1.add("To keep")
        todo2 = store1.add("To delete")
        store1.delete(todo2.id)

        store2 = TodoStore(file_path=temp_file_path)

        todos = store2.get_all()
        assert len(todos) == 1
        assert todos[0].title == "To keep"

    def test_update_persists(self, temp_file_path: Path) -> None:
        """Test that updates are persisted."""
        store1 = TodoStore(file_path=temp_file_path)
        todo = store1.add("Original")
        store1.update(todo.id, title="Updated", completed=True)

        store2 = TodoStore(file_path=temp_file_path)

        loaded = store2.get(todo.id)
        assert loaded.title == "Updated"
        assert loaded.completed is True

    def test_empty_file_starts_fresh(self, temp_file_path: Path) -> None:
        """Test that missing file starts with empty store."""
        store = TodoStore(file_path=temp_file_path)

        assert store.get_all() == []
        assert store.add("First").id == 1
