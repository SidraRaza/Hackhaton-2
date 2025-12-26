"""Business logic for Todo operations."""

from src.models.todo import Todo
from src.models.exceptions import TodoNotFoundError, ValidationError
from src.store.memory_store import TodoStore


class TodoService:
    """Service layer for Todo operations.

    Provides business logic and validation for todo CRUD operations.
    """

    def __init__(self, store: TodoStore) -> None:
        """Initialize the service with a store.

        Args:
            store: The TodoStore instance to use for persistence.
        """
        self._store = store

    def add_todo(self, title: str) -> Todo:
        """Add a new todo with the given title.

        Args:
            title: The title of the todo.

        Returns:
            The created Todo.

        Raises:
            ValidationError: If the title is empty or whitespace-only.
        """
        self._validate_title(title)
        return self._store.add(title.strip())

    def list_todos(self) -> list[Todo]:
        """Get all todos.

        Returns:
            A list of all todos sorted by ID.
        """
        return self._store.get_all()

    def complete_todo(self, todo_id: int) -> Todo:
        """Mark a todo as complete.

        Args:
            todo_id: The ID of the todo to complete.

        Returns:
            The updated Todo.

        Raises:
            TodoNotFoundError: If no todo exists with the given ID.
        """
        todo = self._store.get(todo_id)
        if todo.completed:
            return todo  # Already complete
        return self._store.update(todo_id, completed=True)

    def update_todo(self, todo_id: int, title: str) -> Todo:
        """Update a todo's title.

        Args:
            todo_id: The ID of the todo to update.
            title: The new title.

        Returns:
            The updated Todo.

        Raises:
            TodoNotFoundError: If no todo exists with the given ID.
            ValidationError: If the title is empty or whitespace-only.
        """
        self._validate_title(title)
        self._store.get(todo_id)  # Verify exists
        return self._store.update(todo_id, title=title.strip())

    def delete_todo(self, todo_id: int) -> bool:
        """Delete a todo.

        Args:
            todo_id: The ID of the todo to delete.

        Returns:
            True if the todo was deleted.

        Raises:
            TodoNotFoundError: If no todo exists with the given ID.
        """
        return self._store.delete(todo_id)

    def _validate_title(self, title: str) -> None:
        """Validate that a title is not empty or whitespace-only.

        Args:
            title: The title to validate.

        Raises:
            ValidationError: If the title is invalid.
        """
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty")
