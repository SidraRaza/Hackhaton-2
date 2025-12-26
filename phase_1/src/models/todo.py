"""Todo model definition."""

from dataclasses import dataclass, field


@dataclass
class Todo:
    """Represents a task to be tracked.

    Attributes:
        id: Unique identifier (auto-generated integer).
        title: Description of the task (non-empty string).
        completed: Status flag indicating completion (default False).
    """

    id: int
    title: str
    completed: bool = field(default=False)
