"""In-memory storage for Todo entities."""

from src.models.todo import Todo
from src.models.exceptions import TodoNotFoundError


class TodoStore:
    """In-memory storage for Todo entities.

    Provides CRUD operations for todos with auto-incrementing IDs.
    Data is stored in memory and lost when the application exits.
    """

    def __init__(self) -> None:
        """Initialize the store with empty storage and ID counter."""
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1

    def add(self, title: str) -> Todo:
        """Add a new todo with the given title.

        Args:
            title: The title of the todo.

        Returns:
            The created Todo with generated ID.
        """
        todo = Todo(id=self._next_id, title=title, completed=False)
        self._todos[self._next_id] = todo
        self._next_id += 1
        return todo

    def get(self, todo_id: int) -> Todo:
        """Retrieve a todo by its ID.

        Args:
            todo_id: The ID of the todo to retrieve.

        Returns:
            The Todo with the specified ID.

        Raises:
            TodoNotFoundError: If no todo exists with the given ID.
        """
        if todo_id not in self._todos:
            raise TodoNotFoundError(todo_id)
        return self._todos[todo_id]

    def get_all(self) -> list[Todo]:
        """Retrieve all todos.

        Returns:
            A list of all todos, sorted by ID.
        """
        return sorted(self._todos.values(), key=lambda t: t.id)

    def update(self, todo_id: int, **kwargs) -> Todo:
        """Update a todo with the given fields.

        Args:
            todo_id: The ID of the todo to update.
            **kwargs: Fields to update (title, completed).

        Returns:
            The updated Todo.

        Raises:
            TodoNotFoundError: If no todo exists with the given ID.
        """
        todo = self.get(todo_id)
        if "title" in kwargs:
            todo.title = kwargs["title"]
        if "completed" in kwargs:
            todo.completed = kwargs["completed"]
        return todo

    def delete(self, todo_id: int) -> bool:
        """Delete a todo by its ID.

        Args:
            todo_id: The ID of the todo to delete.

        Returns:
            True if the todo was deleted.

        Raises:
            TodoNotFoundError: If no todo exists with the given ID.
        """
        if todo_id not in self._todos:
            raise TodoNotFoundError(todo_id)
        del self._todos[todo_id]
        return True
