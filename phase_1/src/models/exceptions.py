"""Custom exceptions for the Todo CLI application."""


class TodoNotFoundError(Exception):
    """Raised when a todo with the specified ID is not found."""

    def __init__(self, todo_id: int) -> None:
        self.todo_id = todo_id
        super().__init__(f"Todo #{todo_id} not found")


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
