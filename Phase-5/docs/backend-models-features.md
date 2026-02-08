# Backend Models: Advanced Task Features

## Overview
This document outlines the existing backend models for advanced task features in the Todo application. All advanced features are already implemented in the backend models.

## Enums

### PriorityEnum
Defines the priority levels for tasks.

**Values**:
- `low` - Low priority tasks
- `medium` - Medium priority tasks (default)
- `high` - High priority tasks

### RecurrencePatternEnum
Defines the recurrence patterns for recurring tasks.

**Values**:
- `daily` - Daily recurrence
- `weekly` - Weekly recurrence
- `monthly` - Monthly recurrence
- `yearly` - Yearly recurrence
- `custom` - Custom recurrence pattern

## Base Class

### TaskBase
Base class containing common fields for all task models.

**Fields**:
- `title` (str): Task title (required, 1-200 characters)
- `description` (Optional[str]): Task description (optional, max 1000 characters)
- `completed` (bool): Completion status (defaults to False)

## Core Model

### Task
Main task model extending TaskBase with advanced features and database mapping.

**Fields**:
- `id` (Optional[int]): Primary key, auto-generated
- `user_id` (str): Foreign key linking to user (indexed)
- `priority` (PriorityEnum): Task priority (defaults to medium)
- `due_date` (Optional[datetime]): Due date/time for the task
- `recurrence_pattern` (Optional[RecurrencePatternEnum]): Recurrence pattern for recurring tasks
- `recurrence_config` (Optional[Dict[str, Any]]): Configuration for custom recurrence patterns (stored as JSON)
- `parent_task_id` (Optional[int]): Foreign key linking to parent task (for recurring task series)
- `next_occurrence` (Optional[datetime]): Next occurrence date for recurring tasks
- `occurrences_remaining` (Optional[int]): Number of remaining occurrences for recurring tasks
- `reminder_times` (Optional[List[datetime]]): List of reminder times (stored as JSON)
- `last_reminder_sent` (Optional[datetime]): Timestamp of last reminder sent
- `created_at` (datetime): Creation timestamp (auto-generated)
- `updated_at` (datetime): Last update timestamp (auto-generated)

## Creation Model

### TaskCreate
Model for creating new tasks with advanced features.

**Fields** (inherits from TaskBase plus):
- `priority` (Optional[PriorityEnum]): Task priority (defaults to medium)
- `due_date` (Optional[datetime]): Due date/time for the task
- `recurrence_pattern` (Optional[RecurrencePatternEnum]): Recurrence pattern for recurring tasks
- `recurrence_config` (Optional[Dict[str, Any]]): Configuration for custom recurrence patterns
- `tag_ids` (Optional[List[int]]): List of tag IDs to associate with the task (defaults to empty list)
- `reminder_times` (Optional[List[datetime]]): List of reminder times

## Update Model

### TaskUpdate
Model for updating existing tasks with advanced features.

**Fields** (all optional):
- `title` (Optional[str]): Task title (1-200 characters)
- `description` (Optional[str]): Task description (max 1000 characters)
- `completed` (Optional[bool]): Completion status
- `priority` (Optional[PriorityEnum]): Task priority
- `due_date` (Optional[datetime]): Due date/time for the task
- `recurrence_pattern` (Optional[RecurrencePatternEnum]): Recurrence pattern for recurring tasks
- `recurrence_config` (Optional[Dict[str, Any]]): Configuration for custom recurrence patterns
- `tag_ids` (Optional[List[int]]): List of tag IDs to associate with the task
- `reminder_times` (Optional[List[datetime]]): List of reminder times

## Public Model

### TaskPublic
Model for exposing task data in API responses with advanced features.

**Fields** (inherits from TaskBase plus):
- `id` (int): Primary key
- `user_id` (str): Foreign key linking to user
- `priority` (PriorityEnum): Task priority
- `due_date` (Optional[datetime]): Due date/time for the task
- `recurrence_pattern` (Optional[RecurrencePatternEnum]): Recurrence pattern for recurring tasks
- `recurrence_config` (Optional[Dict[str, Any]]): Configuration for custom recurrence patterns
- `parent_task_id` (Optional[int]): Foreign key linking to parent task
- `next_occurrence` (Optional[datetime]): Next occurrence date for recurring tasks
- `occurrences_remaining` (Optional[int]): Number of remaining occurrences for recurring tasks
- `reminder_times` (Optional[List[datetime]]): List of reminder times
- `last_reminder_sent` (Optional[datetime]): Timestamp of last reminder sent
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

## Advanced Features Summary

### Priority System
- Three-tier priority system (low, medium, high)
- Default priority is medium
- Priority field is indexed for efficient querying

### Due Dates & Times
- Optional datetime field for task deadlines
- Supports timezone-aware datetime objects

### Recurrence Patterns
- Five different recurrence patterns supported
- Custom recurrence pattern with flexible configuration
- Parent-child relationship for recurring task series
- Next occurrence tracking
- Occurrence counter for limited series

### Tag Association
- Many-to-many relationship with tags through tag_ids array
- Flexible tagging system for task categorization

### Reminder System
- Multiple reminder times per task
- Tracking of last reminder sent timestamp

### Data Storage
- JSON fields for flexible data storage (recurrence_config, reminder_times)
- Indexed fields for efficient querying (user_id)
- Automatic timestamps for creation and updates