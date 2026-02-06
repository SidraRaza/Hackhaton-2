# UI API Contracts: Premium SaaS UI/UX for Todo App

## Overview
This document specifies the API contracts that the enhanced UI will use. Since we're only modifying the frontend presentation layer, these represent the existing backend APIs that the new UI components will consume.

## Authentication API Contracts

### GET /api/auth/me
**Description**: Retrieve current user information
**Request Headers**:
- Authorization: Bearer {token}

**Response**:
```json
{
  "id": "string",
  "name": "string",
  "email": "string",
  "avatar": "string (optional)"
}
```

### POST /api/auth/login
**Description**: Authenticate user and return session token
**Request Body**:
```json
{
  "email": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "token": "string",
  "user": {
    "id": "string",
    "name": "string",
    "email": "string"
  }
}
```

## Task Management API Contracts

### GET /api/tasks
**Description**: Retrieve user's tasks with filtering options
**Query Parameters**:
- status (optional): "todo" | "in-progress" | "completed"
- priority (optional): "low" | "medium" | "high"
- search (optional): string
- limit (optional): number
- offset (optional): number

**Request Headers**:
- Authorization: Bearer {token}

**Response**:
```json
{
  "tasks": [
    {
      "id": "string",
      "title": "string",
      "description": "string (optional)",
      "priority": "low" | "medium" | "high",
      "status": "todo" | "in-progress" | "completed",
      "dueDate": "string (ISO date format)",
      "createdAt": "string (ISO date format)",
      "updatedAt": "string (ISO date format)"
    }
  ],
  "total": number,
  "hasMore": boolean
}
```

### POST /api/tasks
**Description**: Create a new task
**Request Headers**:
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body**:
```json
{
  "title": "string",
  "description": "string (optional)",
  "priority": "low" | "medium" | "high",
  "dueDate": "string (ISO date format, optional)"
}
```

**Response**:
```json
{
  "id": "string",
  "title": "string",
  "description": "string (optional)",
  "priority": "low" | "medium" | "high",
  "status": "todo",
  "dueDate": "string (ISO date format, optional)",
  "createdAt": "string (ISO date format)",
  "updatedAt": "string (ISO date format)"
}
```

### PUT /api/tasks/{id}
**Description**: Update an existing task
**Request Headers**:
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body**:
```json
{
  "title"?: "string",
  "description"?: "string",
  "priority"?: "low" | "medium" | "high",
  "status"?: "todo" | "in-progress" | "completed",
  "dueDate"?: "string (ISO date format)"
}
```

**Response**:
```json
{
  "id": "string",
  "title": "string",
  "description": "string (optional)",
  "priority": "low" | "medium" | "high",
  "status": "todo" | "in-progress" | "completed",
  "dueDate": "string (ISO date format, optional)",
  "createdAt": "string (ISO date format)",
  "updatedAt": "string (ISO date format)"
}
```

### DELETE /api/tasks/{id}
**Description**: Delete a task
**Request Headers**:
- Authorization: Bearer {token}

**Response**: 204 No Content

## User Preferences API Contracts

### GET /api/users/preferences
**Description**: Retrieve user's UI preferences
**Request Headers**:
- Authorization: Bearer {token}

**Response**:
```json
{
  "theme": "dark" | "light",
  "sidebarCollapsed": boolean,
  "animationsEnabled": boolean,
  "fontSize": "small" | "normal" | "large"
}
```

### PUT /api/users/preferences
**Description**: Update user's UI preferences
**Request Headers**:
- Authorization: Bearer {token}
- Content-Type: application/json

**Request Body**:
```json
{
  "theme"?: "dark" | "light",
  "sidebarCollapsed"?: boolean,
  "animationsEnabled"?: boolean,
  "fontSize"?: "small" | "normal" | "large"
}
```

**Response**:
```json
{
  "theme": "dark" | "light",
  "sidebarCollapsed": boolean,
  "animationsEnabled": boolean,
  "fontSize": "small" | "normal" | "large"
}
```

## Real-time Updates (if WebSocket available)

### WebSocket Connection: /ws/tasks
**Description**: Listen for real-time task updates
**Message Types**:

#### Task Created
```json
{
  "type": "TASK_CREATED",
  "data": {
    "id": "string",
    "title": "string",
    "description": "string (optional)",
    "priority": "low" | "medium" | "high",
    "status": "todo" | "in-progress" | "completed",
    "dueDate": "string (ISO date format)",
    "createdAt": "string (ISO date format)",
    "updatedAt": "string (ISO date format)"
  }
}
```

#### Task Updated
```json
{
  "type": "TASK_UPDATED",
  "data": {
    "id": "string",
    "title": "string",
    "description": "string (optional)",
    "priority": "low" | "medium" | "high",
    "status": "todo" | "in-progress" | "completed",
    "dueDate": "string (ISO date format)",
    "createdAt": "string (ISO date format)",
    "updatedAt": "string (ISO date format)"
  }
}
```

#### Task Deleted
```json
{
  "type": "TASK_DELETED",
  "data": {
    "id": "string"
  }
}
```

## Error Response Format
All API endpoints return standardized error responses:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)"
  }
}
```

## HTTP Status Codes
- 200: Success
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Unprocessable Entity
- 500: Internal Server Error