# Quickstart Guide: Todo CLI Application

**Feature**: `1-todo-cli-core`
**Date**: 2025-12-26

## Prerequisites

- Python 3.13 or higher
- UV package manager (for dependency management)

## Installation

```bash
# Navigate to project directory
cd phase_1

# Install with UV
uv sync

# Or install in development mode
uv pip install -e .
```

## Basic Usage

### Start the Application

The Todo CLI operates through command-line arguments. Each command performs one operation.

### Commands Overview

| Command | Description | Example |
|---------|-------------|---------|
| `add` | Add a new todo | `todo add "Buy groceries"` |
| `list` | View all todos | `todo list` |
| `complete` | Mark todo as done | `todo complete 1` |
| `update` | Change todo title | `todo update 1 "Buy organic groceries"` |
| `delete` | Remove a todo | `todo delete 1` |

---

## Command Details

### Add a Todo

Create a new todo item with a title.

```bash
todo add "Your task description"
```

**Example**:
```bash
$ todo add "Buy groceries"
✓ Added todo #1: "Buy groceries"

$ todo add "Call mom"
✓ Added todo #2: "Call mom"
```

**Error Cases**:
```bash
$ todo add ""
✗ Error: Title cannot be empty

$ todo add "   "
✗ Error: Title cannot be empty
```

---

### List All Todos

Display all todos with their ID, title, and status.

```bash
todo list
```

**Example**:
```bash
$ todo list
ID  | Status     | Title
----|------------|------------------
1   | incomplete | Buy groceries
2   | complete   | Call mom
3   | incomplete | Finish report
```

**When Empty**:
```bash
$ todo list
No todos found. Add one with: todo add "Your task"
```

---

### Mark Todo as Complete

Mark a specific todo as done by its ID.

```bash
todo complete <id>
```

**Example**:
```bash
$ todo complete 1
✓ Marked todo #1 as complete: "Buy groceries"

$ todo complete 1
! Todo #1 is already complete

$ todo complete 99
✗ Error: Todo #99 not found
```

---

### Update Todo Title

Change the title of an existing todo.

```bash
todo update <id> "New title"
```

**Example**:
```bash
$ todo update 1 "Buy organic groceries"
✓ Updated todo #1: "Buy organic groceries"

$ todo update 99 "New title"
✗ Error: Todo #99 not found

$ todo update 1 ""
✗ Error: Title cannot be empty
```

---

### Delete a Todo

Remove a todo permanently.

```bash
todo delete <id>
```

**Example**:
```bash
$ todo delete 1
✓ Deleted todo #1

$ todo delete 99
✗ Error: Todo #99 not found
```

---

## Typical Workflow

```bash
# 1. Add some todos
$ todo add "Buy groceries"
✓ Added todo #1: "Buy groceries"

$ todo add "Call mom"
✓ Added todo #2: "Call mom"

$ todo add "Finish report"
✓ Added todo #3: "Finish report"

# 2. View your list
$ todo list
ID  | Status     | Title
----|------------|------------------
1   | incomplete | Buy groceries
2   | incomplete | Call mom
3   | incomplete | Finish report

# 3. Complete a task
$ todo complete 2
✓ Marked todo #2 as complete: "Call mom"

# 4. Update a task
$ todo update 1 "Buy organic groceries"
✓ Updated todo #1: "Buy organic groceries"

# 5. View updated list
$ todo list
ID  | Status     | Title
----|------------|------------------
1   | incomplete | Buy organic groceries
2   | complete   | Call mom
3   | incomplete | Finish report

# 6. Delete a completed task
$ todo delete 2
✓ Deleted todo #2
```

---

## Getting Help

```bash
$ todo --help
usage: todo [-h] {add,list,complete,update,delete} ...

Todo CLI - Manage your tasks from the command line

positional arguments:
  {add,list,complete,update,delete}
    add                 Add a new todo
    list                List all todos
    complete            Mark a todo as complete
    update              Update a todo's title
    delete              Delete a todo

optional arguments:
  -h, --help            show this help message and exit

$ todo add --help
usage: todo add [-h] title

positional arguments:
  title       The todo title

optional arguments:
  -h, --help  show this help message and exit
```

---

## Important Notes

1. **Data is not saved**: All todos are stored in memory and will be lost when the application exits
2. **IDs are permanent**: Once assigned, a todo's ID never changes and is never reused
3. **Single user**: This application is designed for single-user operation
4. **No undo**: Deleted todos cannot be recovered

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (todo not found, validation failed, etc.) |

---

## Troubleshooting

### "Command not found: todo"

Make sure the package is installed:
```bash
uv pip install -e .
```

### "Todo #X not found"

The todo with that ID doesn't exist. Use `todo list` to see available IDs.

### "Title cannot be empty"

Provide a non-empty title in quotes:
```bash
todo add "My task"
```
