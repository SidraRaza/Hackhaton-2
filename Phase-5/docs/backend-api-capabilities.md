# Backend API Capabilities: Advanced Task Features

## Overview
This document outlines the existing backend API capabilities for advanced task features in the Todo application. All advanced features are already implemented in the backend.

## API Endpoints

### GET /api/tasks
**Purpose**: Retrieve all tasks for the current user with advanced filtering and sorting

**Query Parameters**:
- `priority`: Array of priority levels to filter by (low, medium, high)
- `tags`: Array of tag IDs to filter by
- `search`: Full-text search term for title/description
- `due_date_from`: Filter tasks with due date after this date
- `due_date_to`: Filter tasks with due date before this date
- `recurrence_pattern`: Filter by recurrence pattern (daily, weekly, monthly, yearly, custom)
- `status_filter`: Filter by status (pending, completed, all) - defaults to "all"
- `sort`: Sort field (priority, due_date, created_at, title, completed) - defaults to "created_at"
- `sort_order`: Sort order (asc, desc) - defaults to "desc"
- `secondary_sort`: Secondary sort field - defaults to "created_at"
- `secondary_sort_order`: Secondary sort order (asc, desc) - defaults to "desc"
- `limit`: Number of results to return (1-100) - defaults to 50
- `offset`: Offset for pagination - defaults to 0
- `use_saved_filters`: Boolean to use saved filter preferences
- `save_filters`: Boolean to save current filters as preferences

### POST /api/tasks
**Purpose**: Create a new task with advanced features

**Request Body**:
- `title`: Task title (required, 1-200 chars)
- `description`: Task description (optional, max 1000 chars)
- `priority`: Priority level (low, medium, high) - defaults to "medium"
- `due_date`: Due date/time in ISO format (optional)
- `recurrence_pattern`: Recurrence pattern (daily, weekly, monthly, yearly, custom) (optional)
- `recurrence_config`: Configuration object for custom recurrence (optional)
- `tag_ids`: Array of tag IDs to associate with the task (optional)

**Validation**:
- If recurrence pattern is set, due_date is required
- If recurrence pattern is "custom", recurrence_config is required
- Recurrence patterns are validated before creation

### GET /api/tasks/{task_id}
**Purpose**: Retrieve a specific task by ID

### PUT /api/tasks/{task_id}
**Purpose**: Update an existing task with advanced features

**Request Body**:
- `title`: Task title (optional, 1-200 chars)
- `description`: Task description (optional, max 1000 chars)
- `completed`: Completion status (optional)
- `priority`: Priority level (low, medium, high) (optional)
- `due_date`: Due date/time in ISO format (optional)
- `recurrence_pattern`: Recurrence pattern (optional)
- `recurrence_config`: Configuration object for custom recurrence (optional)
- `tag_ids`: Array of tag IDs to associate with the task (optional)

**Validation**:
- If recurrence pattern is updated, due_date is required if not already set
- If recurrence pattern is "custom", recurrence_config is required
- Recurrence patterns are validated before update

### DELETE /api/tasks/{task_id}
**Purpose**: Delete a specific task

### POST /api/tasks/{task_id}/complete
**Purpose**: Complete a task with options for recurring tasks

**Request Body**:
- `mark_series_complete`: Boolean to mark entire recurring series as complete

### POST /api/tasks/{task_id}/complete-recurrence
**Purpose**: Special completion endpoint for recurring tasks with advanced options

**Request Body**:
- `mark_series_complete`: Boolean to mark entire series as complete
- `modify_future_occurrences`: Boolean to modify future occurrences
- `skip_next_occurrence`: Boolean to skip creating next occurrence
- `recurrence_action`: Action to take (create_next, skip, end_series)
- `create_next_occurrence`: Boolean to create next occurrence

### PATCH /api/tasks/{task_id}/complete
**Purpose**: Toggle task completion status (deprecated, use POST /complete)

**Request Body**:
- `completed`: New completion status (boolean)

## Advanced Feature Support

### Priority System
- **Supported Levels**: low, medium, high
- **Default**: medium
- **Filtering**: Available in GET endpoint with multiple priority filters
- **Sorting**: Available as sort option

### Tag Management
- **Association**: Tasks can be associated with multiple tags via tag_ids array
- **Filtering**: Available in GET endpoint with tag ID filters
- **Relationship**: Many-to-many relationship between tasks and tags

### Due Dates & Times
- **Format**: ISO 8601 datetime format
- **Filtering**: Range-based filtering (due_date_from, due_date_to) in GET endpoint
- **Sorting**: Available as sort option

### Recurrence Patterns
- **Supported Patterns**: daily, weekly, monthly, yearly, custom
- **Configuration**: Custom patterns support additional configuration object
- **Validation**: All patterns are validated before creation/update
- **Series Management**: Options to complete entire series or manage individual occurrences
- **Next Occurrence Calculation**: Automatic calculation of next occurrence when task is completed

### Search & Filtering
- **Full-text Search**: Search across title and description fields
- **Multi-criteria Filtering**: Combine multiple filters (priority, tags, dates, recurrence)
- **Saved Filters**: Ability to save and reuse filter preferences
- **Pagination**: Built-in pagination with limit and offset

### Event-Driven Architecture
- **Task Created Event**: Emitted when new task is created
- **Task Updated Event**: Emitted when task is updated with change tracking
- **Task Deleted Event**: Emitted when task is deleted
- **Task Completed Event**: Emitted when task is completed

## Enums

### PriorityEnum
- `low`
- `medium`
- `high`

### RecurrencePatternEnum
- `daily`
- `weekly`
- `monthly`
- `yearly`
- `custom`

## Models

### TaskCreate
Extended model supporting all advanced features for task creation.

### TaskUpdate
Extended model supporting all advanced features for task updates.

### TaskPublic
Extended model exposing all advanced features in API responses.