# Tasks: Todo CLI Core Features

**Input**: Design documents from `specs/1-todo-cli-core/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, research.md, quickstart.md

**Tests**: Tests are included as they support incremental verification per constitution principles.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure: `src/`, `src/models/`, `src/services/`, `src/cli/`, `src/store/`, `tests/`, `tests/unit/`, `tests/integration/`
- [X] T002 Create pyproject.toml with Python 3.13+ requirement and UV configuration
- [X] T003 [P] Create `src/__init__.py` with package metadata
- [X] T004 [P] Create `src/models/__init__.py`
- [X] T005 [P] Create `src/services/__init__.py`
- [X] T006 [P] Create `src/cli/__init__.py`
- [X] T007 [P] Create `src/store/__init__.py`
- [X] T008 [P] Create `tests/__init__.py`
- [X] T009 [P] Create `tests/unit/__init__.py`
- [X] T010 [P] Create `tests/integration/__init__.py`

**Checkpoint**: Project structure ready for foundational components

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 Create Todo dataclass in `src/models/todo.py` with fields: id (int), title (str), completed (bool, default=False)
- [X] T012 Create custom exceptions in `src/models/exceptions.py`: TodoNotFoundError, ValidationError
- [X] T013 Create TodoStore class in `src/store/memory_store.py` with _todos dict and _next_id counter
- [X] T014 Implement TodoStore.add() method in `src/store/memory_store.py` that generates ID and stores todo
- [X] T015 Implement TodoStore.get() method in `src/store/memory_store.py` that retrieves todo by ID
- [X] T016 Implement TodoStore.get_all() method in `src/store/memory_store.py` that returns all todos
- [X] T017 Create global store instance in `src/store/__init__.py` for application-wide access
- [X] T018 Create unit test file `tests/unit/test_todo_model.py` with test for Todo dataclass creation
- [X] T019 Create unit test file `tests/unit/test_memory_store.py` with tests for store initialization

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Add Todo (Priority: P1) 🎯 MVP

**Goal**: Allow users to add new todos with a title

**Independent Test**: Run `todo add "Buy groceries"` and verify confirmation message with ID

**Spec Reference**: FR-001, FR-002, FR-003, FR-008, FR-012

### Implementation for User Story 1

- [X] T020 [US1] Create TodoService class in `src/services/todo_service.py` with store dependency
- [X] T021 [US1] Implement add_todo(title: str) -> Todo method in `src/services/todo_service.py` with title validation
- [X] T022 [US1] Create CLI add command handler in `src/cli/commands.py` that calls service and prints confirmation
- [X] T023 [US1] Add title validation (non-empty, non-whitespace) in add_todo() in `src/services/todo_service.py`
- [X] T024 [US1] Add error message output for empty title in `src/cli/commands.py`
- [X] T025 [US1] Write unit test for add_todo success in `tests/unit/test_todo_service.py`
- [X] T026 [US1] Write unit test for add_todo with empty title in `tests/unit/test_todo_service.py`

**Checkpoint**: User Story 1 (Add Todo) is fully functional and testable independently

---

## Phase 4: User Story 2 - View Todos (Priority: P2)

**Goal**: Allow users to view all todos with ID, title, and status

**Independent Test**: After adding todos, run `todo list` and verify formatted output

**Spec Reference**: FR-004, FR-012

### Implementation for User Story 2

- [X] T027 [US2] Implement list_todos() -> list[Todo] method in `src/services/todo_service.py`
- [X] T028 [US2] Create CLI list command handler in `src/cli/commands.py` that formats and displays todos
- [X] T029 [US2] Implement formatted output (ID | Status | Title) in `src/cli/commands.py`
- [X] T030 [US2] Handle empty list case with "No todos found" message in `src/cli/commands.py`
- [X] T031 [US2] Write unit test for list_todos with todos in `tests/unit/test_todo_service.py`
- [X] T032 [US2] Write unit test for list_todos when empty in `tests/unit/test_todo_service.py`

**Checkpoint**: User Stories 1 AND 2 are functional - users can add and view todos

---

## Phase 5: User Story 3 - Mark Todo as Complete (Priority: P3)

**Goal**: Allow users to mark a todo as complete by ID

**Independent Test**: Add a todo, run `todo complete 1`, verify status change in list

**Spec Reference**: FR-005, FR-009, FR-012

### Implementation for User Story 3

- [X] T033 [US3] Implement TodoStore.update() method in `src/store/memory_store.py` for modifying todos
- [X] T034 [US3] Implement complete_todo(id: int) -> Todo method in `src/services/todo_service.py`
- [X] T035 [US3] Add ID validation (exists check) in complete_todo() in `src/services/todo_service.py`
- [X] T036 [US3] Handle already-complete case in complete_todo() in `src/services/todo_service.py`
- [X] T037 [US3] Create CLI complete command handler in `src/cli/commands.py`
- [X] T038 [US3] Add error handling for todo not found in `src/cli/commands.py`
- [X] T039 [US3] Write unit test for complete_todo success in `tests/unit/test_todo_service.py`
- [X] T040 [US3] Write unit test for complete_todo not found in `tests/unit/test_todo_service.py`
- [X] T041 [US3] Write unit test for complete_todo already complete in `tests/unit/test_todo_service.py`

**Checkpoint**: User Stories 1, 2, AND 3 are functional - full add/view/complete flow works

---

## Phase 6: User Story 4 - Update Todo (Priority: P4)

**Goal**: Allow users to update a todo's title by ID

**Independent Test**: Add a todo, run `todo update 1 "New title"`, verify change in list

**Spec Reference**: FR-006, FR-008, FR-009, FR-012

### Implementation for User Story 4

- [X] T042 [US4] Implement update_todo(id: int, title: str) -> Todo method in `src/services/todo_service.py`
- [X] T043 [US4] Add title validation in update_todo() in `src/services/todo_service.py`
- [X] T044 [US4] Add ID validation in update_todo() in `src/services/todo_service.py`
- [X] T045 [US4] Create CLI update command handler in `src/cli/commands.py`
- [X] T046 [US4] Add error handling for empty title and not found in `src/cli/commands.py`
- [X] T047 [US4] Write unit test for update_todo success in `tests/unit/test_todo_service.py`
- [X] T048 [US4] Write unit test for update_todo with empty title in `tests/unit/test_todo_service.py`
- [X] T049 [US4] Write unit test for update_todo not found in `tests/unit/test_todo_service.py`

**Checkpoint**: User Stories 1-4 are functional

---

## Phase 7: User Story 5 - Delete Todo (Priority: P5)

**Goal**: Allow users to delete a todo by ID

**Independent Test**: Add a todo, run `todo delete 1`, verify removal in list

**Spec Reference**: FR-007, FR-009, FR-012

### Implementation for User Story 5

- [X] T050 [US5] Implement TodoStore.delete() method in `src/store/memory_store.py`
- [X] T051 [US5] Implement delete_todo(id: int) -> bool method in `src/services/todo_service.py`
- [X] T052 [US5] Add ID validation in delete_todo() in `src/services/todo_service.py`
- [X] T053 [US5] Create CLI delete command handler in `src/cli/commands.py`
- [X] T054 [US5] Add error handling for todo not found in `src/cli/commands.py`
- [X] T055 [US5] Write unit test for delete_todo success in `tests/unit/test_todo_service.py`
- [X] T056 [US5] Write unit test for delete_todo not found in `tests/unit/test_todo_service.py`

**Checkpoint**: All 5 user stories are functional

---

## Phase 8: CLI Integration & Polish

**Purpose**: Complete CLI entry point and wire all commands together

- [X] T057 Create main.py with argparse setup in `src/main.py`
- [X] T058 Add subparsers for all commands (add, list, complete, update, delete) in `src/main.py`
- [X] T059 Wire command handlers to argparse subcommands in `src/main.py`
- [X] T060 Add --help text for all commands in `src/main.py`
- [X] T061 Implement exit codes (0 success, 1 error) in `src/main.py`
- [X] T062 Add console_scripts entry point to pyproject.toml
- [X] T063 Write integration test for add command in `tests/integration/test_cli.py`
- [X] T064 Write integration test for list command in `tests/integration/test_cli.py`
- [X] T065 Write integration test for complete command in `tests/integration/test_cli.py`
- [X] T066 Write integration test for update command in `tests/integration/test_cli.py`
- [X] T067 Write integration test for delete command in `tests/integration/test_cli.py`
- [X] T068 Write integration test for error scenarios in `tests/integration/test_cli.py`

**Checkpoint**: CLI is fully integrated and all workflows work end-to-end

---

## Phase 9: Review & Finalization

**Purpose**: Quality verification against specification

- [X] T069 Run all unit tests and verify pass
- [X] T070 Run all integration tests and verify pass
- [X] T071 Verify all acceptance scenarios from spec.md pass manually
- [X] T072 Verify PEP 8 compliance across all source files
- [X] T073 Verify type hints are complete on all functions
- [X] T074 Review code against constitution clean code principles
- [X] T075 Validate against quickstart.md examples

**Checkpoint**: Application is complete and ready for use

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational
    ↓
Phase 3: US1 - Add Todo (P1) 🎯 MVP
    ↓
Phase 4: US2 - View Todos (P2)
    ↓
Phase 5: US3 - Mark Complete (P3) ─┐
                                    │ (parallel possible after Phase 4)
Phase 6: US4 - Update Todo (P4) ───┤
                                    │
Phase 7: US5 - Delete Todo (P5) ───┘
    ↓
Phase 8: CLI Integration
    ↓
Phase 9: Review
```

### User Story Dependencies

| User Story | Depends On | Can Start After |
|------------|------------|-----------------|
| US1 (Add) | Phase 2 | Foundational complete |
| US2 (View) | US1 | Add is working |
| US3 (Complete) | US2 | View is working |
| US4 (Update) | US2 | View is working |
| US5 (Delete) | US2 | View is working |

### Within Each User Story

1. Service method implementation
2. Validation logic
3. CLI command handler
4. Error handling
5. Unit tests

### Parallel Opportunities

**Phase 1** - All __init__.py files (T003-T010) can run in parallel

**After Phase 4 (View)** - US3, US4, US5 can run in parallel:
```
Task: Complete US3 (Mark Complete)
Task: Complete US4 (Update Todo)
Task: Complete US5 (Delete Todo)
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Add)
4. Complete Phase 4: User Story 2 (View)
5. **STOP and VALIDATE**: Add + View workflow works
6. Can demo MVP: Users can add and view todos

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Add) → Users can capture todos
3. Add US2 (View) → Users can see their todos (**MVP Complete**)
4. Add US3 (Complete) → Users can track progress
5. Add US4 (Update) → Users can fix mistakes
6. Add US5 (Delete) → Users can clean up
7. CLI Integration → Professional CLI experience
8. Review → Quality verified

---

## Task Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|----------------------|
| Phase 1: Setup | T001-T010 (10) | T003-T010 (8 parallel) |
| Phase 2: Foundational | T011-T019 (9) | None (sequential) |
| Phase 3: US1 Add | T020-T026 (7) | None (sequential) |
| Phase 4: US2 View | T027-T032 (6) | None (sequential) |
| Phase 5: US3 Complete | T033-T041 (9) | None (sequential) |
| Phase 6: US4 Update | T042-T049 (8) | None (sequential) |
| Phase 7: US5 Delete | T050-T056 (7) | None (sequential) |
| Phase 8: Integration | T057-T068 (12) | T063-T068 (6 parallel) |
| Phase 9: Review | T069-T075 (7) | T072-T073 (2 parallel) |

**Total Tasks**: 75
**MVP Tasks**: T001-T032 (32 tasks for Add + View)
**Suggested MVP Scope**: Complete through Phase 4 for working Add + View

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are relative to `phase_1/` directory
