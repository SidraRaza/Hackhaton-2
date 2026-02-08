# Backend Services: Advanced Task Features

## Overview
This document outlines the existing backend services for advanced task features in the Todo application. All advanced features are already implemented in the backend services.

## Task Service

### TaskService
Core service for handling all task operations with advanced features.

#### Methods

##### get_tasks_by_user(session, user_id, filters=None)
Retrieve all tasks for a specific user with advanced filtering and sorting capabilities.

**Parameters**:
- `session`: Database session
- `user_id`: User ID to filter tasks
- `filters`: Optional dictionary with filtering parameters:
  - `priority`: List of priority levels to filter by
  - `tags`: List of tag IDs to filter by
  - `search`: Full-text search term for title/description
  - `due_date_from`: Filter tasks with due date after this date
  - `due_date_to`: Filter tasks with due date before this date
  - `recurrence_pattern`: Filter by recurrence pattern
  - `status`: Filter by task status ('pending', 'completed', 'all')
  - `sort`: Sort field ('priority', 'due_date', 'created_at', 'title', 'completed')
  - `sort_order`: Sort order ('asc', 'desc')
  - `limit`: Number of results to return
  - `offset`: Offset for pagination

**Returns**: List of tasks matching the criteria

##### get_task_by_id(session, task_id, user_id)
Get a specific task by ID for a user.

##### create_task(session, task, tag_ids=None)
Create a new task with optional tag associations.

**Parameters**:
- `session`: Database session
- `task`: Task object to create
- `tag_ids`: Optional list of tag IDs to associate with the task

**Returns**: Created Task object

##### update_task(session, task_id, user_id, task_data, tag_ids=None)
Update a task with optional tag association updates.

**Parameters**:
- `session`: Database session
- `task_id`: ID of the task to update
- `user_id`: User ID for authorization
- `task_data`: Dictionary of fields to update
- `tag_ids`: Optional list of tag IDs to associate with the task (replaces existing)

**Returns**: Updated Task object or None if not found

##### delete_task(session, task_id, user_id)
Delete a task and its associated tags.

**Returns**: Boolean indicating success

##### toggle_task_completion(session, task_id, user_id, completed)
Toggle task completion status with recurrence handling.

**Returns**: Updated Task object or None if not found

##### complete_task(session, task_id, user_id, mark_series_completed=False)
Complete a task with options for recurring tasks.

**Returns**: Completed Task object or None if not found

##### complete_recurring_task(session, task_id, user_id, mark_series_complete=False, modify_future_occurrences=False, skip_next_occurrence=False, recurrence_action="create_next", create_next_occurrence=True)
Complete a recurring task with advanced options.

**Returns**: Completed Task object or None if not found

##### create_audit_log(session, user_id, action, resource_type, resource_id, action_details)
Create an audit log entry for the action performed.

## Recurrence Service

### RecurrenceService
Service for handling task recurrence patterns and calculations.

#### Methods

##### validate_pattern(pattern, config=None)
Validate recurrence pattern and configuration.

**Parameters**:
- `pattern`: Recurrence pattern (daily, weekly, monthly, yearly, custom)
- `config`: Configuration for the pattern

**Returns**: Boolean indicating validity

##### parse_recurrence_pattern(pattern, config=None)
Parse recurrence pattern and return normalized configuration.

**Returns**: Dictionary with normalized recurrence configuration

##### calculate_next_occurrence(pattern, config, current_date=None, last_occurrence=None)
Calculate the next occurrence date based on recurrence pattern.

**Parameters**:
- `pattern`: Recurrence pattern
- `config`: Configuration for the pattern
- `current_date`: Date to calculate from (defaults to now)
- `last_occurrence`: Last occurrence date (for more accurate calculation)

**Returns**: Next occurrence datetime or None if pattern is invalid

##### generate_occurrences(pattern, config, start_date, end_condition)
Generate occurrences based on recurrence pattern and end condition.

**Returns**: List of occurrence datetimes

##### parse_human_recurrence(human_input)
Parse natural language recurrence patterns.

**Returns**: Dictionary with pattern and config

##### create_next_occurrence(original_task)
Create the next occurrence of a recurring task.

**Returns**: New task instance for next occurrence or None if not recurring

## Tag Service

### TagService
Service for handling tag operations with advanced features.

#### Methods

##### get_tags_by_user(session, user_id)
Get all tags for a specific user.

**Returns**: List of tags belonging to the user

##### get_tag_by_id(session, tag_id, user_id)
Get a specific tag by ID for a user.

**Returns**: Tag object if found and belongs to user, None otherwise

##### create_tag(session, tag)
Create a new tag.

**Returns**: Created Tag object

##### update_tag(session, tag_id, user_id, tag_data)
Update a tag with new data.

**Returns**: Updated Tag object if successful, None if tag not found

##### delete_tag(session, tag_id, user_id)
Delete a tag and its associations.

**Returns**: Boolean indicating success

##### get_tasks_for_tag(session, tag_id, user_id)
Get all tasks associated with a specific tag for a user.

**Returns**: List of tasks associated with the tag

##### associate_task_with_tag(session, task_id, tag_id)
Associate a task with a tag.

**Returns**: Boolean indicating success

##### remove_task_from_tag(session, task_id, tag_id)
Remove a task from a tag (remove association).

**Returns**: Boolean indicating success

##### get_popular_tags(session, user_id, limit=10)
Get the most popular tags for a user (by number of associated tasks).

**Returns**: List of most popular tags

## Other Relevant Services

### Search Service
Handles advanced search functionality for tasks.

### Notification Service
Manages notifications for tasks, including reminders.

### Reminder Service
Handles task reminder scheduling and delivery.

### Preference Service
Manages user preferences for task filtering, sorting, and display options.

### Event Publisher
Publishes events for task operations to support event-driven architecture.

### Dapr Services
Handle distributed application runtime features like state management, secrets, and service invocation.

## Advanced Feature Integration Points

### Priority System
- Integrated into TaskService filtering and sorting
- Supported in all CRUD operations

### Tag Management
- Full CRUD operations in TagService
- Many-to-many relationships with tasks
- Search and association features

### Recurrence Patterns
- Comprehensive recurrence logic in RecurrenceService
- Integration with TaskService for creating next occurrences
- Support for multiple pattern types (daily, weekly, monthly, yearly, custom)

### Due Dates & Reminders
- Due date handling in TaskService
- Reminder scheduling in ReminderService
- Timezone handling in TimezoneService

### Event-Driven Architecture
- Event publishing in TaskService for all major operations
- Event-driven patterns throughout the system
- Kafka/Redpanda integration via Event Publisher