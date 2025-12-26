# Research: Todo CLI Core Features

**Feature**: `1-todo-cli-core`
**Date**: 2025-12-26
**Purpose**: Document technical decisions and research findings

## Technical Decisions

### 1. CLI Framework

**Decision**: Use `argparse` from Python standard library

**Rationale**:
- No external dependencies required (per constitution constraints)
- Built into Python 3.13+
- Subcommand support for add/list/complete/update/delete
- Automatic help generation
- Type conversion for integer IDs

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Click | External dependency not permitted |
| Typer | External dependency not permitted |
| sys.argv parsing | Less maintainable, no auto-help |

---

### 2. Data Model

**Decision**: Use `@dataclass` with `field()` for Todo entity

**Rationale**:
- Native Python 3.13+ feature
- Automatic `__init__`, `__repr__`, `__eq__`
- Type hints built-in
- Immutable option available if needed
- No external dependencies

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| NamedTuple | Less flexible for mutable state |
| Plain class | More boilerplate code |
| Pydantic | External dependency not permitted |
| TypedDict | No instance methods, less OOP |

---

### 3. In-Memory Storage

**Decision**: Use Python `dict[int, Todo]` with auto-incrementing ID counter

**Rationale**:
- O(1) lookup by ID
- Simple integer key matches spec requirement
- Native Python, no dependencies
- Easy to iterate for list operations
- Thread-safe for single-user (per spec assumptions)

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| List with index | ID would change on delete |
| SQLite in-memory | External complexity, overkill |
| Redis | Networking not permitted |

**ID Generation Strategy**:
- Start at 1 (human-friendly)
- Increment for each new todo
- Never reuse IDs (even after delete)
- Counter persists during session

---

### 4. Project Structure

**Decision**: Layered architecture with clear separation

```
src/
├── models/      # Data structures
├── services/    # Business logic
├── cli/         # User interface
└── store/       # Data access
```

**Rationale**:
- Single Responsibility Principle
- Easy to test each layer independently
- CLI layer isolated from business logic
- Storage abstraction allows future changes (not needed now, but clean)

---

### 5. Error Handling Strategy

**Decision**: Custom exceptions with user-friendly messages

**Rationale**:
- Clear separation of error types
- Consistent error messaging
- CLI can catch and format appropriately
- Follows Python exception best practices

**Exception Types**:
| Exception | When Raised |
|-----------|-------------|
| `TodoNotFoundError` | ID doesn't exist in store |
| `ValidationError` | Empty title, invalid ID format |

---

### 6. Output Formatting

**Decision**: Simple text output with consistent structure

**Rationale**:
- Console-based per spec
- Human-readable primary concern
- No JSON/structured output needed (not in spec)
- Consistent prefix for operation results

**Format Examples**:
```
✓ Added todo #1: "Buy groceries"
✓ Marked todo #1 as complete
✓ Deleted todo #1
✗ Error: Todo #99 not found
✗ Error: Title cannot be empty
```

---

### 7. Testing Strategy

**Decision**: pytest with unit and integration tests

**Rationale**:
- Standard Python testing framework
- Simple assertions
- Good fixture support
- Easy to run subset of tests

**Test Organization**:
- `tests/unit/` - Test service functions in isolation
- `tests/integration/` - Test full CLI workflows

---

## Best Practices Applied

### Python 3.13+ Features Used

1. **Type Hints**: All functions have complete type annotations
2. **Dataclasses**: Native data modeling
3. **f-strings**: String formatting
4. **Walrus operator**: Where appropriate for readability
5. **Match statements**: For command dispatch (if cleaner)

### Clean Code Principles

1. **Single Responsibility**: Each module has one purpose
2. **DRY**: Common logic extracted to shared functions
3. **YAGNI**: No features beyond specification
4. **Meaningful Names**: Clear variable and function names
5. **Small Functions**: Each function does one thing

### PEP 8 Compliance

1. 4-space indentation
2. 79-character line limit (or 88 for Black compatibility)
3. Two blank lines between top-level definitions
4. Lowercase with underscores for functions/variables
5. PascalCase for classes

---

## Resolved Clarifications

| Original Question | Resolution | Source |
|-------------------|------------|--------|
| CLI framework? | argparse (std lib) | Constitution: no external deps |
| Storage mechanism? | In-memory dict | Spec: in-memory only |
| ID type? | Integer, auto-increment | Spec: unique identifier |
| Output format? | Plain text | Spec: console-based |
| Error handling? | Custom exceptions | Best practice |

---

## Research Status

✅ All technical decisions made
✅ No NEEDS CLARIFICATION remaining
✅ Ready for Phase 1 design artifacts
