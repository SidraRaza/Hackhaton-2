# Hackathon Todo App - API Documentation

## Overview
The Hackathon Todo App provides a RESTful API for managing tasks with secure user authentication. The API follows standard REST conventions and uses JWT tokens for authentication.

## Authentication
All API endpoints (except authentication endpoints) require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token_here>
```

## Base URL
The API is served at: `http://localhost:8000/api`

## Authentication Endpoints

### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 604800
}
```

**Status Codes:**
- 200: User registered successfully
- 400: Invalid input data
- 409: User already exists

### POST /api/auth/login
Authenticate an existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 604800
}
```

**Status Codes:**
- 200: Login successful
- 401: Invalid credentials

### POST /api/auth/logout
Log out the current user (if needed).

**Response:**
- 200: Logout successful

## Task Endpoints

### GET /api/tasks
Retrieve all tasks for the authenticated user.

**Headers:**
```
Authorization: Bearer <valid_jwt_token>
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Sample task",
    "description": "Task description",
    "completed": false,
    "user_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
]
```

**Status Codes:**
- 200: Tasks retrieved successfully
- 401: Unauthorized

### POST /api/tasks
Create a new task for the authenticated user.

**Headers:**
```
Authorization: Bearer <valid_jwt_token>
```

**Request Body:**
```json
{
  "title": "New task",
  "description": "Task description"
}
```

**Response:**
```json
{
  "id": 2,
  "title": "New task",
  "description": "Task description",
  "completed": false,
  "user_id": 1,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

**Status Codes:**
- 201: Task created successfully
- 400: Invalid input data
- 401: Unauthorized

### GET /api/tasks/{task_id}
Retrieve a specific task by ID.

**Headers:**
```
Authorization: Bearer <valid_jwt_token>
```

**Path Parameters:**
- `task_id`: ID of the task to retrieve

**Response:**
```json
{
  "id": 1,
  "title": "Sample task",
  "description": "Task description",
  "completed": false,
  "user_id": 1,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

**Status Codes:**
- 200: Task retrieved successfully
- 401: Unauthorized
- 404: Task not found

### PUT /api/tasks/{task_id}
Update an existing task.

**Headers:**
```
Authorization: Bearer <valid_jwt_token>
```

**Path Parameters:**
- `task_id`: ID of the task to update

**Request Body:**
```json
{
  "title": "Updated task",
  "description": "Updated description",
  "completed": true
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Updated task",
  "description": "Updated description",
  "completed": true,
  "user_id": 1,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

**Status Codes:**
- 200: Task updated successfully
- 400: Invalid input data
- 401: Unauthorized
- 404: Task not found

### DELETE /api/tasks/{task_id}
Delete a task.

**Headers:**
```
Authorization: Bearer <valid_jwt_token>
```

**Path Parameters:**
- `task_id`: ID of the task to delete

**Status Codes:**
- 204: Task deleted successfully
- 401: Unauthorized
- 404: Task not found

### PATCH /api/tasks/{task_id}/complete
Toggle the completion status of a task.

**Headers:**
```
Authorization: Bearer <valid_jwt_token>
```

**Path Parameters:**
- `task_id`: ID of the task to update

**Response:**
```json
{
  "id": 1,
  "title": "Sample task",
  "description": "Task description",
  "completed": true,
  "user_id": 1,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-02T00:00:00Z"
}
```

**Status Codes:**
- 200: Task completion status updated
- 401: Unauthorized
- 404: Task not found

## Error Responses
All error responses follow this format:
```json
{
  "detail": "Error message describing the issue"
}
```

## Security
- All endpoints except authentication require valid JWT tokens
- Users can only access their own tasks
- Tokens expire after 7 days
- Input validation is performed on all requests