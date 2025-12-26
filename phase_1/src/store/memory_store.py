"""Persistent storage for Todo entities."""

import json
from pathlib import Path

from src.models.todo import Todo
from src.models.exceptions import TodoNotFoundError

# Default file path for todo persistence
DEFAULT_FILE_PATH = Path("todos.json")


class TodoStore:
    """Persistent storage for Todo entities.

    Provides CRUD operations for todos with auto-incrementing IDs.
    Data is persisted to a JSON file and survives between sessions.
    """

    def __init__(self, file_path: Path | None = None) -> None:
        """Initialize the store and load existing todos from file.

        Args:
            file_path: Optional path to the persistence file.
                      Defaults to 'todos.json' in current directory.
        """
        self._file_path: Path = file_path or DEFAULT_FILE_PATH
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1
        self._load()

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
        self._save()
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
        self._save()
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
        self._save()
        return True

    def _load(self) -> None:
        """Load todos from the persistence file.

        If the file doesn't exist or is invalid, starts with empty storage.
        """
        if not self._file_path.exists():
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._next_id = data.get("next_id", 1)
            for todo_data in data.get("todos", []):
                todo = Todo(
                    id=todo_data["id"],
                    title=todo_data["title"],
                    completed=todo_data["completed"],
                )
                self._todos[todo.id] = todo
        except (json.JSONDecodeError, KeyError, TypeError):
            # If file is corrupted, start fresh
            self._todos = {}
            self._next_id = 1

    def _save(self) -> None:
        """Save todos to the persistence file."""
        data = {
            "next_id": self._next_id,
            "todos": [
                {"id": t.id, "title": t.title, "completed": t.completed}
                for t in self._todos.values()
            ],
        }
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
