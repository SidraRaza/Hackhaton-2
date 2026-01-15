# Task CRUD Feature Specification

> **Feature**: Task Management (Create, Read, Update, Delete)
> **Phase**: II
> **Status**: Ready for Implementation

## Overview

Enable authenticated users to manage their personal tasks with full CRUD operations, completion tracking, filtering, and sorting capabilities.

## Related Specs

- `@specs/api/rest-endpoints.md` - API endpoint definitions
- `@specs/database/schema.md` - Task model schema
- `@specs/features/authentication.md` - JWT authentication
- `@specs/ui/components.md` - TaskCard, TaskForm components

---

## User Stories

### US-1: Create Task (P1)
**As a** logged-in user
**I want to** create a new task
**So that** I can track work I need to complete

**Acceptance Criteria:**
- [ ] Title is required (1-200 characters)
- [ ] Description is optional (max 1000 characters)
- [ ] Task is automatically linked to authenticated user
- [ ] Task defaults to `completed: false`
- [ ] Created task is returned with generated ID and timestamps
- [ ] Returns 201 Created on success
- [ ] Returns 400 Bad Request if title missing or invalid
- [ ] Returns 401 Unauthorized if JWT invalid/missing

### US-2: View All Tasks (P1)
**As a** logged-in user
**I want to** see all my tasks
**So that** I can review my work items

**Acceptance Criteria:**
- [ ] Only tasks belonging to authenticated user are returned
- [ ] Tasks include id, title, description, completed, created_at, updated_at
- [ ] Empty array returned if no tasks exist
- [ ] Returns 401 Unauthorized if JWT invalid/missing

### US-3: View Single Task (P2)
**As a** logged-in user
**I want to** view details of a specific task
**So that** I can see full information

**Acceptance Criteria:**
- [ ] Returns full task details by ID
- [ ] Returns 404 if task doesn't exist or belongs to another user
- [ ] Returns 401 Unauthorized if JWT invalid/missing

### US-4: Update Task (P1)
**As a** logged-in user
**I want to** update a task's details
**So that** I can modify task information

**Acceptance Criteria:**
- [ ] Can update title, description, and/or completed status
- [ ] Only provided fields are updated (partial update)
- [ ] updated_at timestamp is refreshed
- [ ] Returns 404 if task doesn't exist or belongs to another user
- [ ] Returns 400 if validation fails
- [ ] Returns 401 Unauthorized if JWT invalid/missing

### US-5: Delete Task (P1)
**As a** logged-in user
**I want to** delete a task
**So that** I can remove completed or unnecessary items

**Acceptance Criteria:**
- [ ] Task is permanently deleted from database
- [ ] Returns 204 No Content on success
- [ ] Returns 404 if task doesn't exist or belongs to another user
- [ ] Returns 401 Unauthorized if JWT invalid/missing

### US-6: Toggle Completion (P1)
**As a** logged-in user
**I want to** mark a task as complete or incomplete
**So that** I can track my progress

**Acceptance Criteria:**
- [ ] Toggles `completed` boolean (true ↔ false)
- [ ] updated_at timestamp is refreshed
- [ ] Returns updated task
- [ ] Returns 404 if task doesn't exist or belongs to another user
- [ ] Returns 401 Unauthorized if JWT invalid/missing

### US-7: Filter Tasks (P2)
**As a** logged-in user
**I want to** filter tasks by status
**So that** I can focus on pending or completed items

**Acceptance Criteria:**
- [ ] Filter by `status=pending` returns tasks where completed=false
- [ ] Filter by `status=completed` returns tasks where completed=true
- [ ] No filter returns all tasks
- [ ] Returns 401 Unauthorized if JWT invalid/missing

### US-8: Sort Tasks (P2)
**As a** logged-in user
**I want to** sort tasks by different fields
**So that** I can organize my view

**Acceptance Criteria:**
- [ ] Sort by `title` (asc/desc)
- [ ] Sort by `created_at` (asc/desc)
- [ ] Sort by `due_date` (asc/desc) if field exists
- [ ] Default sort: `created_at desc`
- [ ] Returns 401 Unauthorized if JWT invalid/missing

---

## Data Model

```python
class Task:
    id: int                    # Primary key, auto-increment
    user_id: str               # Foreign key → users.id
    title: str                 # Required, 1-200 chars
    description: str | None    # Optional, max 1000 chars
    completed: bool            # Default: false
    created_at: datetime       # Auto-set on creation
    updated_at: datetime       # Auto-updated on modification
```

**Validation Rules:**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | Yes | 1-200 characters |
| description | string | No | Max 1000 characters |
| completed | boolean | No | Default: false |

---

## API Examples

### Create Task
**Request:**
```http
POST /api/{user_id}/tasks
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Complete Phase II spec",
  "description": "Write all specification documents for the hackathon project"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Complete Phase II spec",
  "description": "Write all specification documents for the hackathon project",
  "completed": false,
  "created_at": "2026-01-08T10:00:00Z",
  "updated_at": "2026-01-08T10:00:00Z"
}
```

### List Tasks with Filter
**Request:**
```http
GET /api/{user_id}/tasks?status=pending&sort_by=created_at&sort_order=desc
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "user_id": "user_abc123",
    "title": "Review API spec",
    "description": null,
    "completed": false,
    "created_at": "2026-01-08T11:00:00Z",
    "updated_at": "2026-01-08T11:00:00Z"
  },
  {
    "id": 1,
    "user_id": "user_abc123",
    "title": "Complete Phase II spec",
    "description": "Write all specification documents",
    "completed": false,
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": "2026-01-08T10:00:00Z"
  }
]
```

### Update Task
**Request:**
```http
PUT /api/{user_id}/tasks/1
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Complete Phase II spec [UPDATED]",
  "completed": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Complete Phase II spec [UPDATED]",
  "description": "Write all specification documents",
  "completed": true,
  "created_at": "2026-01-08T10:00:00Z",
  "updated_at": "2026-01-08T12:30:00Z"
}
```

### Toggle Completion
**Request:**
```http
PATCH /api/{user_id}/tasks/1/complete
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Complete Phase II spec [UPDATED]",
  "description": "Write all specification documents",
  "completed": false,
  "created_at": "2026-01-08T10:00:00Z",
  "updated_at": "2026-01-08T13:00:00Z"
}
```

### Delete Task
**Request:**
```http
DELETE /api/{user_id}/tasks/1
Authorization: Bearer <jwt_token>
```

**Response (204 No Content):**
```
(empty body)
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Title is required and must be 1-200 characters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or missing authentication token"
}
```

### 404 Not Found
```json
{
  "detail": "Task not found"
}
```

---

## Implementation Checklist

### Backend
- [ ] Create Task model with SQLModel
- [ ] Create TaskCreate, TaskUpdate, TaskRead schemas
- [ ] Implement POST /api/{user_id}/tasks endpoint
- [ ] Implement GET /api/{user_id}/tasks endpoint with filtering/sorting
- [ ] Implement GET /api/{user_id}/tasks/{id} endpoint
- [ ] Implement PUT /api/{user_id}/tasks/{id} endpoint
- [ ] Implement DELETE /api/{user_id}/tasks/{id} endpoint
- [ ] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint
- [ ] Add JWT authentication middleware
- [ ] Add user_id filtering to all queries

### Frontend
- [ ] Create TaskCard component
- [ ] Create TaskForm component (create/edit)
- [ ] Create TaskList component with filters
- [ ] Create /tasks page
- [ ] Create /tasks/[id] page
- [ ] Create /tasks/new page
- [ ] Integrate with API client
- [ ] Add loading and error states
