# Data Model: Advanced Cloud Deployment

## Overview
This document defines the data models for Phase V: Advanced Cloud Deployment, including extended task features, event-driven architecture, and supporting entities.

## Core Entities

### 1. Task Entity
**Description**: Extended task entity with advanced features
**Fields**:
- `id` (INTEGER, PRIMARY KEY): Unique identifier
- `user_id` (VARCHAR(255), NOT NULL): Owner of the task
- `title` (VARCHAR(200), NOT NULL): Task title
- `description` (TEXT): Optional task description
- `completed` (BOOLEAN, DEFAULT FALSE): Completion status
- `priority` (VARCHAR(10), DEFAULT 'medium'): Priority level (low, medium, high)
- `due_date` (TIMESTAMP): Due date and time
- `recurrence_pattern` (VARCHAR(50)): Recurrence pattern (daily, weekly, monthly, yearly, custom)
- `recurrence_config` (JSONB): Configuration for recurrence pattern
- `parent_task_id` (INTEGER, REFERENCES tasks.id): Link to parent task for recurring tasks
- `next_occurrence` (TIMESTAMP): Next occurrence date for recurring tasks
- `occurrences_remaining` (INTEGER): Count of remaining occurrences
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Creation timestamp
- `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Last update timestamp

**Validation Rules**:
- `priority` must be one of ['low', 'medium', 'high']
- `recurrence_pattern` must be one of ['daily', 'weekly', 'monthly', 'yearly', 'custom'] if provided
- `due_date` must be in the future if provided
- `user_id` must reference an existing user

**Relationships**:
- One-to-many with `task_tags` (via foreign key)
- Self-referencing for recurring tasks (parent_task_id)

### 2. Tag Entity
**Description**: Tag entity for categorizing tasks
**Fields**:
- `id` (INTEGER, PRIMARY KEY): Unique identifier
- `user_id` (VARCHAR(255), NOT NULL): Owner of the tag
- `name` (VARCHAR(50), NOT NULL): Tag name
- `color` (VARCHAR(7), DEFAULT '#3B82F6'): Color for UI display
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Creation timestamp

**Validation Rules**:
- `name` must be unique per user
- `color` must be a valid hex color code
- `name` length between 1 and 50 characters

**Relationships**:
- Many-to-many with `tasks` via `task_tags` junction table

### 3. Task-Tag Junction Entity
**Description**: Junction table for many-to-many relationship between tasks and tags
**Fields**:
- `task_id` (INTEGER, REFERENCES tasks.id, ON DELETE CASCADE): Foreign key to task
- `tag_id` (INTEGER, REFERENCES tags.id, ON DELETE CASCADE): Foreign key to tag
- Primary key on (`task_id`, `tag_id`)

**Validation Rules**:
- Combination of `task_id` and `tag_id` must be unique
- Both foreign keys must reference existing records

**Relationships**:
- Belongs to one `task` and one `tag`

### 4. Event Store Entity
**Description**: Centralized event store for event-driven architecture
**Fields**:
- `event_id` (UUID, PRIMARY KEY): Unique event identifier
- `event_type` (VARCHAR(100), NOT NULL): Type of event (e.g., task.created)
- `event_version` (VARCHAR(20), NOT NULL): Version of the event schema
- `aggregate_type` (VARCHAR(50), NOT NULL): Type of aggregate (e.g., task)
- `aggregate_id` (VARCHAR(255), NOT NULL): ID of the aggregate
- `payload` (JSONB, NOT NULL): Event data
- `metadata` (JSONB): Additional event metadata
- `timestamp` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Event creation time
- `user_id` (VARCHAR(255)): User who triggered the event

**Validation Rules**:
- `event_type` must follow the format 'domain.action' (e.g., 'task.created')
- `payload` must be valid JSON
- `event_version` must follow semantic versioning

**Indexes**:
- Composite index on (`aggregate_type`, `aggregate_id`) for efficient aggregate queries
- Index on `timestamp` for time-based queries
- Index on `event_type` for event type filtering

### 5. User Entity (Existing, Extended)
**Description**: User entity with additional fields for advanced features
**Fields**:
- `id` (VARCHAR(255), PRIMARY KEY): Unique user identifier
- `email` (VARCHAR(255), UNIQUE, NOT NULL): User email
- `name` (VARCHAR(255)): User name
- `preferences` (JSONB): User preferences including default priority, sort order, etc.
- `created_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Account creation time
- `updated_at` (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP): Last update time

**Validation Rules**:
- `email` must be a valid email format
- `email` must be unique across all users
- `preferences` must be valid JSON

## Event Schemas

### 1. Task Events

#### task.created
```json
{
  "event_id": "uuid_v4",
  "event_type": "task.created",
  "event_version": "1.0",
  "timestamp": "2025-12-01T10:30:00Z",
  "source": "todo-service",
  "data": {
    "task_id": "integer",
    "user_id": "string",
    "title": "string",
    "description": "string",
    "priority": "enum",
    "due_date": "timestamp",
    "recurrence_pattern": "string",
    "recurrence_config": "json_object"
  },
  "metadata": {
    "correlation_id": "uuid_v4",
    "trace_id": "string"
  }
}
```

#### task.updated
```json
{
  "event_id": "uuid_v4",
  "event_type": "task.updated",
  "event_version": "1.0",
  "timestamp": "2025-12-01T10:30:00Z",
  "source": "todo-service",
  "data": {
    "task_id": "integer",
    "user_id": "string",
    "changes": {
      "field_name": "old_value -> new_value"
    },
    "updated_fields": ["array_of_field_names"]
  },
  "metadata": {
    "correlation_id": "uuid_v4",
    "trace_id": "string"
  }
}
```

#### task.completed
```json
{
  "event_id": "uuid_v4",
  "event_type": "task.completed",
  "event_version": "1.0",
  "timestamp": "2025-12-01T10:30:00Z",
  "source": "todo-service",
  "data": {
    "task_id": "integer",
    "user_id": "string",
    "completed_at": "timestamp",
    "was_recurring": "boolean",
    "has_next_occurrence": "boolean"
  },
  "metadata": {
    "correlation_id": "uuid_v4",
    "trace_id": "string"
  }
}
```

#### task.deleted
```json
{
  "event_id": "uuid_v4",
  "event_type": "task.deleted",
  "event_version": "1.0",
  "timestamp": "2025-12-01T10:30:00Z",
  "source": "todo-service",
  "data": {
    "task_id": "integer",
    "user_id": "string",
    "deleted_at": "timestamp"
  },
  "metadata": {
    "correlation_id": "uuid_v4",
    "trace_id": "string"
  }
}
```

#### task.recurrence_created
```json
{
  "event_id": "uuid_v4",
  "event_type": "task.recurrence_created",
  "event_version": "1.0",
  "timestamp": "2025-12-01T10:30:00Z",
  "source": "recurrence-service",
  "data": {
    "original_task_id": "integer",
    "new_task_id": "integer",
    "user_id": "string",
    "recurrence_sequence": "integer",
    "next_due_date": "timestamp"
  },
  "metadata": {
    "correlation_id": "uuid_v4",
    "trace_id": "string"
  }
}
```

### 2. User Events

#### user.registered
```json
{
  "event_id": "uuid_v4",
  "event_type": "user.registered",
  "event_version": "1.0",
  "timestamp": "2025-12-01T10:30:00Z",
  "source": "auth-service",
  "data": {
    "user_id": "string",
    "email": "string",
    "registration_method": "enum"
  },
  "metadata": {
    "correlation_id": "uuid_v4",
    "trace_id": "string"
  }
}
```

### 3. System Events

#### reminder.triggered
```json
{
  "event_id": "uuid_v4",
  "event_type": "reminder.triggered",
  "event_version": "1.0",
  "timestamp": "2025-12-01T10:30:00Z",
  "source": "reminder-service",
  "data": {
    "task_id": "integer",
    "user_id": "string",
    "reminder_time": "timestamp",
    "notification_channel": "enum"
  },
  "metadata": {
    "correlation_id": "uuid_v4",
    "trace_id": "string"
  }
}
```

#### notification.sent
```json
{
  "event_id": "uuid_v4",
  "event_type": "notification.sent",
  "event_version": "1.0",
  "timestamp": "2025-12-01T10:30:00Z",
  "source": "notification-service",
  "data": {
    "notification_id": "string",
    "user_id": "string",
    "channel": "enum",
    "status": "enum",
    "retry_count": "integer"
  },
  "metadata": {
    "correlation_id": "uuid_v4",
    "trace_id": "string"
  }
}
```

## State Transition Diagrams

### Task State Transitions
```
PENDING ──→ COMPLETED
   │           │
   ├─→ ARCHIVED │
   └─→ DELETED ←┘
```

Transitions:
- `PENDING` → `COMPLETED`: When task is marked as completed
- `PENDING` → `ARCHIVED`: When task is archived (retained but hidden)
- `PENDING` → `DELETED`: When task is permanently deleted
- `COMPLETED` → `DELETED`: When completed task is deleted
- `COMPLETED` → `PENDING`: When completion is undone (optional feature)

## Indexing Strategy

### Task Table Indexes
1. `idx_tasks_user_id` (user_id): For efficient user-specific queries
2. `idx_tasks_priority` (priority): For priority-based filtering
3. `idx_tasks_due_date` (due_date): For due date queries
4. `idx_tasks_completed` (completed): For completion status filtering
5. `idx_tasks_parent_task` (parent_task_id): For recurring task queries
6. `idx_tasks_next_occurrence` (next_occurrence): For recurrence scheduling
7. `idx_tasks_created_at` (created_at): For chronological queries

### Composite Indexes
1. `idx_tasks_user_priority_completed` (user_id, priority, completed): For complex filtering
2. `idx_tasks_user_completed_duedate` (user_id, completed, due_date): For upcoming tasks
3. `idx_events_aggregate` (aggregate_type, aggregate_id): For aggregate queries in events
4. `idx_events_timestamp` (timestamp): For time-based event queries

## Database Constraints

### Referential Integrity
- `tasks.user_id` references `users.id` with cascade restrictions
- `tasks.parent_task_id` references `tasks.id` with cascade delete
- `task_tags.task_id` references `tasks.id` with cascade delete
- `task_tags.tag_id` references `tags.id` with cascade delete

### Uniqueness Constraints
- `tags.name` unique per `user_id`
- `task_tags` combination of `task_id` and `tag_id` unique

### Check Constraints
- `tasks.priority` in ['low', 'medium', 'high']
- `tasks.due_date` > NOW() when provided
- `tasks.occurrences_remaining` >= 0 when provided
- `tags.color` matches hex color pattern

## Performance Considerations

### Normalization vs Denormalization
- Normalized for data integrity and reduced redundancy
- Selective denormalization for computed fields that are frequently accessed
- Materialized views for complex aggregations

### Partitioning Strategy
- Event store partitioned by time (monthly partitions)
- Task table partitioned by user_id for large-scale scenarios
- Archive old tasks to separate tables for performance

### Caching Strategy
- Application-level caching for user preferences
- Database-level caching for frequently accessed tasks
- CDN caching for static assets and API responses