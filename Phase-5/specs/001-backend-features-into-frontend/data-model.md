# Data Model: Integrate Missing Backend Features into Frontend

## Phase 1: Data Model Design

### Entity: SavedFilter
**Description**: Represents a saved filter configuration for a user

**Fields**:
- id: string (unique identifier for the saved filter)
- name: string (user-friendly name for the filter)
- filters: TaskFilters (the actual filter configuration object)
- createdAt: Date (when the filter was saved)
- updatedAt: Date (when the filter was last modified)

**Relationships**:
- Belongs to User (user who owns the saved filter)

### Entity: TaskFilters (Extended)
**Description**: Enhanced filter configuration that includes date range capabilities

**Fields**:
- priority?: PriorityEnum[] (array of priority values to filter by)
- tags?: number[] (array of tag IDs to filter by)
- search?: string (full text search term)
- due_date_from?: string (filter tasks with due date after this date)
- due_date_to?: string (filter tasks with due date before this date)
- recurrence_pattern?: RecurrencePatternEnum (filter by recurrence pattern)
- status?: 'pending' | 'completed' | 'all' (task completion status)
- sort?: 'priority' | 'due_date' | 'created_at' | 'title' | 'completed' (primary sort field)
- sort_order?: 'asc' | 'desc' (primary sort order)
- secondary_sort?: 'priority' | 'due_date' | 'created_at' | 'title' | 'completed' (secondary sort field)
- secondary_sort_order?: 'asc' | 'desc' (secondary sort order)
- limit?: number (pagination limit)
- offset?: number (pagination offset)
- use_saved_filters?: boolean (whether to use saved filters)
- save_filters?: boolean (whether to save current filters)

### Entity: RecurringTaskCompletionOptions
**Description**: Options for handling recurring task completion

**Fields**:
- mark_series_complete: boolean (complete entire series)
- modify_future_occurrences: boolean (modify future occurrences)
- skip_next_occurrence: boolean (skip the next occurrence)
- recurrence_action: string (action to take: "create_next", "skip", "end_series")
- create_next_occurrence: boolean (whether to create next occurrence)

### State Transitions
- SavedFilter can transition from 'unsaved' to 'saved' when created
- SavedFilter can transition from 'saved' to 'modified' when updated
- Task can transition from 'pending' to 'completed' with various recurrence handling options