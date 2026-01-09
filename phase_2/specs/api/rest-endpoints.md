# REST API Endpoints Specification

> **Type**: API Reference
> **Phase**: II
> **Status**: Ready for Implementation

## Overview

RESTful API specification for the Hackathon II Todo App. All task endpoints require JWT authentication. Authentication endpoints are public.

## Related Specs

- `@specs/features/task-crud.md` - Task feature details
- `@specs/features/authentication.md` - Auth feature details
- `@specs/database/schema.md` - Data models

---

## Base URLs

| Environment | URL |
|-------------|-----|
| Development | `http://localhost:8000` |
| Production | `https://api.example.com` |

---

## Authentication

All task endpoints require JWT authentication.

### Header Format
```http
Authorization: Bearer <jwt_token>
```

### Unauthorized Response (401)
```json
{
  "detail": "Invalid or missing authentication token"
}
```

---

## Auth Endpoints

### POST /api/auth/signup
Create a new user account.

| Field | Value |
|-------|-------|
| Method | POST |
| Path | `/api/auth/signup` |
| Auth | None |
| Content-Type | application/json |

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123"
}
```

**Success Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "user_abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": true,
    "created_at": "2026-01-08T10:00:00Z"
  }
}
```

**Error Responses:**
| Status | Condition | Body |
|--------|-----------|------|
| 400 | Email exists | `{"detail": "Email already registered"}` |
| 400 | Invalid input | `{"detail": "Validation error"}` |

---

### POST /api/auth/login
Authenticate user and return JWT token.

| Field | Value |
|-------|-------|
| Method | POST |
| Path | `/api/auth/login` |
| Auth | None |
| Content-Type | application/json |

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "user_abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": true,
    "created_at": "2026-01-08T10:00:00Z"
  }
}
```

**Error Responses:**
| Status | Condition | Body |
|--------|-----------|------|
| 401 | Invalid credentials | `{"detail": "Invalid email or password"}` |

---

### GET /api/auth/me
Get current authenticated user profile.

| Field | Value |
|-------|-------|
| Method | GET |
| Path | `/api/auth/me` |
| Auth | JWT Required |

**Success Response (200 OK):**
```json
{
  "id": "user_abc123",
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "created_at": "2026-01-08T10:00:00Z"
}
```

---

## Task Endpoints

### GET /api/{user_id}/tasks
List all tasks for authenticated user.

| Field | Value |
|-------|-------|
| Method | GET |
| Path | `/api/{user_id}/tasks` |
| Auth | JWT Required |

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | string | Authenticated user's ID |

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| status | string | - | Filter: `pending` or `completed` |
| sort_by | string | `created_at` | Sort field: `title`, `created_at`, `due_date` |
| sort_order | string | `desc` | Order: `asc` or `desc` |

**Example Request:**
```http
GET /api/user_abc123/tasks?status=pending&sort_by=created_at&sort_order=desc
Authorization: Bearer <jwt_token>
```

**Success Response (200 OK):**
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
    "title": "Write documentation",
    "description": "Complete all spec files",
    "completed": false,
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": "2026-01-08T10:00:00Z"
  }
]
```

---

### POST /api/{user_id}/tasks
Create a new task.

| Field | Value |
|-------|-------|
| Method | POST |
| Path | `/api/{user_id}/tasks` |
| Auth | JWT Required |
| Content-Type | application/json |

**Request Body:**
```json
{
  "title": "New task title",
  "description": "Optional description"
}
```

**Field Validation:**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | Yes | 1-200 characters |
| description | string | No | Max 1000 characters |

**Success Response (201 Created):**
```json
{
  "id": 3,
  "user_id": "user_abc123",
  "title": "New task title",
  "description": "Optional description",
  "completed": false,
  "created_at": "2026-01-08T12:00:00Z",
  "updated_at": "2026-01-08T12:00:00Z"
}
```

**Error Responses:**
| Status | Condition | Body |
|--------|-----------|------|
| 400 | Missing title | `{"detail": "Title is required"}` |
| 400 | Title too long | `{"detail": "Title must be 1-200 characters"}` |
| 401 | Unauthorized | `{"detail": "Invalid or missing authentication token"}` |

---

### GET /api/{user_id}/tasks/{id}
Get a specific task by ID.

| Field | Value |
|-------|-------|
| Method | GET |
| Path | `/api/{user_id}/tasks/{id}` |
| Auth | JWT Required |

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | string | Authenticated user's ID |
| id | integer | Task ID |

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Write documentation",
  "description": "Complete all spec files",
  "completed": false,
  "created_at": "2026-01-08T10:00:00Z",
  "updated_at": "2026-01-08T10:00:00Z"
}
```

**Error Responses:**
| Status | Condition | Body |
|--------|-----------|------|
| 404 | Not found | `{"detail": "Task not found"}` |
| 401 | Unauthorized | `{"detail": "Invalid or missing authentication token"}` |

---

### PUT /api/{user_id}/tasks/{id}
Update an existing task.

| Field | Value |
|-------|-------|
| Method | PUT |
| Path | `/api/{user_id}/tasks/{id}` |
| Auth | JWT Required |
| Content-Type | application/json |

**Request Body (all fields optional):**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Updated title",
  "description": "Updated description",
  "completed": true,
  "created_at": "2026-01-08T10:00:00Z",
  "updated_at": "2026-01-08T14:00:00Z"
}
```

**Error Responses:**
| Status | Condition | Body |
|--------|-----------|------|
| 400 | Invalid input | `{"detail": "Validation error"}` |
| 404 | Not found | `{"detail": "Task not found"}` |
| 401 | Unauthorized | `{"detail": "Invalid or missing authentication token"}` |

---

### DELETE /api/{user_id}/tasks/{id}
Delete a task.

| Field | Value |
|-------|-------|
| Method | DELETE |
| Path | `/api/{user_id}/tasks/{id}` |
| Auth | JWT Required |

**Success Response (204 No Content):**
```
(empty body)
```

**Error Responses:**
| Status | Condition | Body |
|--------|-----------|------|
| 404 | Not found | `{"detail": "Task not found"}` |
| 401 | Unauthorized | `{"detail": "Invalid or missing authentication token"}` |

---

### PATCH /api/{user_id}/tasks/{id}/complete
Toggle task completion status.

| Field | Value |
|-------|-------|
| Method | PATCH |
| Path | `/api/{user_id}/tasks/{id}/complete` |
| Auth | JWT Required |

**Success Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Write documentation",
  "description": "Complete all spec files",
  "completed": true,
  "created_at": "2026-01-08T10:00:00Z",
  "updated_at": "2026-01-08T15:00:00Z"
}
```

**Error Responses:**
| Status | Condition | Body |
|--------|-----------|------|
| 404 | Not found | `{"detail": "Task not found"}` |
| 401 | Unauthorized | `{"detail": "Invalid or missing authentication token"}` |

---

## Endpoint Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/signup` | No | Register new user |
| POST | `/api/auth/login` | No | Authenticate user |
| GET | `/api/auth/me` | JWT | Get current user |
| GET | `/api/{user_id}/tasks` | JWT | List tasks |
| POST | `/api/{user_id}/tasks` | JWT | Create task |
| GET | `/api/{user_id}/tasks/{id}` | JWT | Get task |
| PUT | `/api/{user_id}/tasks/{id}` | JWT | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | JWT | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | JWT | Toggle completion |

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation errors |
| 401 | Unauthorized | Invalid/missing JWT |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Unexpected errors |
