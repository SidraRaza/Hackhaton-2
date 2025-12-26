"""In-memory storage for the Todo CLI application."""

from src.store.memory_store import TodoStore

# Global store instance for application-wide access
store = TodoStore()

__all__ = ["TodoStore", "store"]
