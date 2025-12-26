# Data Model: Todo CLI Core Features

**Feature**: `1-todo-cli-core`
**Date**: 2025-12-26
**Source**: [spec.md](./spec.md) Key Entities section

## Entities

### Todo

Represents a task to be tracked by the user.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | `int` | Yes | Auto-generated | Unique identifier, starts at 1, never reused |
| `title` | `str` | Yes | None | Description of the task, cannot be empty |
| `completed` | `bool` | Yes | `False` | Status flag indicating completion |

**Validation Rules**:

| Rule | Field | Constraint | Error Message |
|------|-------|------------|---------------|
| V-001 | `title` | Must not be empty string | "Title cannot be empty" |
| V-002 | `title` | Must not be whitespace-only | "Title cannot be empty" |
| V-003 | `id` | Must be positive integer | "Invalid ID format" |

**State Transitions**:

```
┌─────────────┐         complete()          ┌─────────────┐
│  Incomplete │ ─────────────────────────▶  │  Complete   │
│ (completed  │                             │ (completed  │
│  = False)   │                             │  = True)    │
└─────────────┘                             └─────────────┘
      │                                           │
      │ update(title)                             │ update(title)
      ▼                                           ▼
  Title Changed                              Title Changed
  (status unchanged)                         (status unchanged)
```

**Invariants**:
- ID is immutable after creation
- ID is unique within the session
- Completed status can only change from False to True (no "uncomplete")
- Title can be updated regardless of completion status

---

## Storage Model

### TodoStore

In-memory storage for Todo entities.

**Internal Structure**:

| Component | Type | Purpose |
|-----------|------|---------|
| `_todos` | `dict[int, Todo]` | Maps ID to Todo entity |
| `_next_id` | `int` | Counter for ID generation, starts at 1 |

**Operations**:

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `add` | `title: str` | `Todo` | Create new todo, return with generated ID |
| `get` | `id: int` | `Todo \| None` | Retrieve todo by ID |
| `get_all` | None | `list[Todo]` | Retrieve all todos |
| `update` | `id: int, title: str` | `Todo` | Update title, return modified todo |
| `delete` | `id: int` | `bool` | Remove todo, return success |
| `complete` | `id: int` | `Todo` | Mark as complete, return modified todo |

**ID Generation**:
```
1. Get current _next_id value
2. Increment _next_id
3. Return original value as new todo's ID
```

---

## Relationships

```
┌─────────────────────────────────────────────────┐
│                   TodoStore                      │
│  ┌─────────────────────────────────────────┐    │
│  │  _todos: dict[int, Todo]                │    │
│  │  ┌───────┬───────────────────────────┐  │    │
│  │  │ ID    │ Todo                      │  │    │
│  │  ├───────┼───────────────────────────┤  │    │
│  │  │ 1     │ {id:1, title:..., ...}    │  │    │
│  │  │ 2     │ {id:2, title:..., ...}    │  │    │
│  │  │ 3     │ {id:3, title:..., ...}    │  │    │
│  │  └───────┴───────────────────────────┘  │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  _next_id: 4                                     │
└─────────────────────────────────────────────────┘
```

---

## Error Conditions

| Error | Condition | Raised By |
|-------|-----------|-----------|
| `TodoNotFoundError` | ID not in `_todos` | get, update, delete, complete |
| `ValidationError` | Empty or whitespace title | add, update |
| `InvalidIdError` | Non-integer or negative ID | All ID-based operations |

---

## Usage Patterns

### Create Todo
```
Input: title="Buy groceries"
Process:
  1. Validate title (not empty)
  2. Generate ID (e.g., 1)
  3. Create Todo(id=1, title="Buy groceries", completed=False)
  4. Store in _todos[1]
  5. Increment _next_id to 2
Output: Todo(id=1, title="Buy groceries", completed=False)
```

### List Todos
```
Input: None
Process:
  1. Retrieve all values from _todos
  2. Convert to list
  3. Sort by ID (optional, for consistent display)
Output: [Todo(...), Todo(...), ...]
```

### Complete Todo
```
Input: id=1
Process:
  1. Validate ID exists in _todos
  2. Get todo from _todos[1]
  3. Set todo.completed = True
  4. Return modified todo
Output: Todo(id=1, title="Buy groceries", completed=True)
```

### Update Todo
```
Input: id=1, title="Buy organic groceries"
Process:
  1. Validate ID exists in _todos
  2. Validate title (not empty)
  3. Get todo from _todos[1]
  4. Set todo.title = "Buy organic groceries"
  5. Return modified todo
Output: Todo(id=1, title="Buy organic groceries", completed=False)
```

### Delete Todo
```
Input: id=1
Process:
  1. Validate ID exists in _todos
  2. Remove _todos[1]
  3. Return True
Output: True
```

---

## Data Model Status

✅ Entity defined with all fields
✅ Validation rules specified
✅ State transitions documented
✅ Storage model defined
✅ Operations mapped to spec requirements
✅ Error conditions identified
