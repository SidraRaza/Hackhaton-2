# Implementation Plan: Todo CLI Core Features

**Feature**: `1-todo-cli-core` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/1-todo-cli-core/spec.md`

## Summary

Implement a console-based Todo CLI application with 5 core features: Add, View, Mark Complete, Update, and Delete todos. The application uses in-memory storage (Python dictionary), command-line interface via argparse, and follows clean code principles with Python 3.13+ compatibility.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Standard library only (argparse, dataclasses, typing)
**Storage**: In-memory (Python dictionary with integer keys)
**Testing**: pytest (for unit and integration tests)
**Target Platform**: Console/Terminal (cross-platform)
**Project Type**: Single project
**Performance Goals**: All operations complete in under 5 seconds (per SC-001 to SC-005)
**Constraints**: No file I/O, no database, no network, no persistence
**Scale/Scope**: Single user, session-based, unlimited todos (memory-bound only)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Plan derived from approved spec.md |
| II. Mandatory Workflow Order | ✅ PASS | Following Spec → Plan → Tasks → Implement → Review |
| III. Clean Code Principles | ✅ PASS | Python 3.13+, type hints, PEP 8, single responsibility |
| IV. Incremental Progress | ✅ PASS | Plan structured for user story-based increments |
| V. Agent Authority | ✅ PASS | Planning Agent creating plan only, no code |
| VI. Skills Reusability | ✅ PASS | Will reference .claude/skills during implementation |
| VII. Quality Standards | ✅ PASS | Review phase included after implementation |
| VIII. Change Management | ✅ PASS | Changes require spec update first |

**Scope Boundaries**:
- ✅ In Scope: Add, Delete, Update, View, Mark Complete
- ✅ Out of Scope Respected: No database, no persistence, no GUI, no auth, no networking

**Gate Result**: ✅ PASSED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/1-todo-cli-core/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (current)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/          # Validation checklists
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # CLI entry point
├── models/
│   ├── __init__.py
│   └── todo.py          # Todo dataclass
├── services/
│   ├── __init__.py
│   └── todo_service.py  # Business logic (CRUD operations)
├── cli/
│   ├── __init__.py
│   └── commands.py      # CLI command handlers
└── store/
    ├── __init__.py
    └── memory_store.py  # In-memory storage

tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_todo_model.py
│   └── test_todo_service.py
└── integration/
    ├── __init__.py
    └── test_cli.py
```

**Structure Decision**: Single project structure selected. Simple CLI application with clear separation:
- `models/` - Data structures (Todo dataclass)
- `services/` - Business logic (CRUD operations)
- `cli/` - Command-line interface layer
- `store/` - In-memory storage abstraction

## Implementation Phases

### Phase 1: Foundation (Setup & Core Infrastructure)

**Goal**: Establish project structure and core data model

**Tasks**:
1. Create project directory structure
2. Configure pyproject.toml for UV with Python 3.13+
3. Create Todo dataclass with ID, title, completed fields
4. Create in-memory store with ID generation
5. Configure pytest for testing

**Dependencies**: None (starting point)

**Deliverables**:
- `pyproject.toml`
- `src/models/todo.py`
- `src/store/memory_store.py`
- Basic project structure with `__init__.py` files

---

### Phase 2: User Story 1 - Add Todo (P1)

**Goal**: Implement ability to add new todos

**Tasks**:
1. Implement `add_todo(title: str) -> Todo` in todo_service.py
2. Add input validation (non-empty title)
3. Create CLI command handler for "add"
4. Display confirmation with generated ID
5. Write unit tests for add functionality

**Dependencies**: Phase 1 (Todo model, store)

**Acceptance Criteria** (from spec):
- Add todo with title → confirms with unique ID
- Add todo with empty title → error message
- New todos default to incomplete status

**Deliverables**:
- `src/services/todo_service.py` (add function)
- `src/cli/commands.py` (add command)
- `tests/unit/test_todo_service.py` (add tests)

---

### Phase 3: User Story 2 - View Todos (P2)

**Goal**: Implement ability to view all todos

**Tasks**:
1. Implement `list_todos() -> list[Todo]` in todo_service.py
2. Create CLI command handler for "list"
3. Format output: ID, Title, Status (complete/incomplete)
4. Handle empty list case with appropriate message
5. Write unit tests for list functionality

**Dependencies**: Phase 2 (need todos to view)

**Acceptance Criteria** (from spec):
- View with todos → displays all with ID, title, status
- View with no todos → "no todos available" message
- Status clearly shows complete vs incomplete

**Deliverables**:
- `src/services/todo_service.py` (list function)
- `src/cli/commands.py` (list command)
- `tests/unit/test_todo_service.py` (list tests)

---

### Phase 4: User Story 3 - Mark Complete (P3)

**Goal**: Implement ability to mark todos as complete

**Tasks**:
1. Implement `complete_todo(id: int) -> Todo` in todo_service.py
2. Add ID validation (exists, valid format)
3. Handle already-complete case
4. Create CLI command handler for "complete"
5. Display confirmation of status change
6. Write unit tests for complete functionality

**Dependencies**: Phase 2 (need add), Phase 3 (verify via list)

**Acceptance Criteria** (from spec):
- Mark incomplete todo complete → confirms completion
- Mark already complete todo → indicates already complete
- Mark non-existent ID → "not found" error

**Deliverables**:
- `src/services/todo_service.py` (complete function)
- `src/cli/commands.py` (complete command)
- `tests/unit/test_todo_service.py` (complete tests)

---

### Phase 5: User Story 4 - Update Todo (P4)

**Goal**: Implement ability to update todo titles

**Tasks**:
1. Implement `update_todo(id: int, title: str) -> Todo` in todo_service.py
2. Add input validation (non-empty title, valid ID)
3. Create CLI command handler for "update"
4. Display confirmation with updated title
5. Write unit tests for update functionality

**Dependencies**: Phase 2 (need add), Phase 3 (verify via list)

**Acceptance Criteria** (from spec):
- Update existing todo → confirms with new title
- Update with empty title → error message
- Update non-existent ID → "not found" error

**Deliverables**:
- `src/services/todo_service.py` (update function)
- `src/cli/commands.py` (update command)
- `tests/unit/test_todo_service.py` (update tests)

---

### Phase 6: User Story 5 - Delete Todo (P5)

**Goal**: Implement ability to delete todos

**Tasks**:
1. Implement `delete_todo(id: int) -> bool` in todo_service.py
2. Add ID validation (exists, valid format)
3. Create CLI command handler for "delete"
4. Display confirmation of deletion
5. Write unit tests for delete functionality

**Dependencies**: Phase 2 (need add), Phase 3 (verify via list)

**Acceptance Criteria** (from spec):
- Delete existing todo → confirms deletion
- Delete non-existent ID → "not found" error
- Delete then list → todo not in list

**Deliverables**:
- `src/services/todo_service.py` (delete function)
- `src/cli/commands.py` (delete command)
- `tests/unit/test_todo_service.py` (delete tests)

---

### Phase 7: CLI Integration & Polish

**Goal**: Complete CLI entry point and integration

**Tasks**:
1. Create main.py with argparse setup
2. Wire all commands (add, list, complete, update, delete)
3. Add help text for all commands
4. Implement consistent error output (stderr)
5. Add exit codes (0 success, non-zero failure)
6. Write integration tests for full CLI workflows

**Dependencies**: Phases 2-6 (all commands implemented)

**Deliverables**:
- `src/main.py` (CLI entry point)
- `tests/integration/test_cli.py` (CLI integration tests)
- Updated `pyproject.toml` with console script entry point

---

### Phase 8: Review & Finalization

**Goal**: Quality review and final verification

**Tasks**:
1. Run all tests (unit + integration)
2. Verify all acceptance scenarios pass
3. Check PEP 8 compliance
4. Verify type hints complete
5. Review against specification
6. Update documentation if needed

**Dependencies**: Phase 7 (complete implementation)

**Deliverables**:
- All tests passing
- Quality review checklist complete
- Ready for deployment/use

## Dependencies Summary

```
Phase 1: Foundation
    ↓
Phase 2: Add Todo (P1)
    ↓
Phase 3: View Todos (P2)
    ↓
Phase 4: Mark Complete (P3)  ←─┐
    ↓                          │ (parallel possible)
Phase 5: Update Todo (P4)   ←──┤
    ↓                          │
Phase 6: Delete Todo (P5)   ←──┘
    ↓
Phase 7: CLI Integration
    ↓
Phase 8: Review
```

**Note**: Phases 4, 5, 6 can run in parallel after Phase 3 completes, as they only depend on add and list functionality.

## Complexity Tracking

> No constitution violations. Simple architecture appropriate for requirements.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Storage | In-memory dict | Spec requires no persistence; simplest solution |
| CLI | argparse | Standard library, no external deps |
| Data Model | dataclass | Python 3.13+ native, type-safe |
| ID Generation | Auto-increment int | Simple, meets unique ID requirement |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep | Low | Medium | Strict adherence to spec, out-of-scope list |
| ID collision | Very Low | Low | Sequential int IDs, single session |
| Memory overflow | Very Low | Low | Practical use won't hit limits |

## Next Steps

1. ✅ Plan complete - ready for `/sp.tasks`
2. Task Breakdown Agent creates granular tasks from this plan
3. Implementation Agent executes tasks in order
4. Review Agent validates against spec

---

**Plan Status**: ✅ COMPLETE
**Ready for**: `/sp.tasks` (Task Breakdown)
