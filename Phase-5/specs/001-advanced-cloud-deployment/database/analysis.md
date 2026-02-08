# Database Schema Analysis: Phase IV to Phase V Evolution

## Overview
This document analyzes the current database schema from Phase IV and outlines the migration plan to support Phase V advanced features (priorities, tags, search, recurrence, due dates) with event-driven architecture and Dapr integration.

## Current Schema (Phase IV)

### Tables

#### 1. tasks
```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

**Columns:**
- `id`: Primary key (auto-incrementing integer)
- `user_id`: Foreign key to users table (string identifier)
- `title`: Task title (max 200 characters, not null)
- `description`: Optional task description (text field)
- `completed`: Boolean indicating completion status (default: false)
- `created_at`: Timestamp when task was created (default: now)
- `updated_at`: Timestamp when task was last updated (default: now, auto-updating)

**Indexes:**
- `idx_tasks_user_id`: For efficient user-specific queries
- `idx_tasks_completed`: For filtering by completion status

#### 2. conversations
```sql
CREATE TABLE conversations (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

#### 3. messages
```sql
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  conversation_id INTEGER NOT NULL,
  role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
```

## Required Extensions for Phase V

### 1. tasks table extensions (Priority D1.1)
The tasks table needs the following new columns to support advanced features:

```sql
-- Add priority column
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high'));

-- Add due date column
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;

-- Add recurrence columns
ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(50);  -- daily, weekly, monthly, yearly, custom
ALTER TABLE tasks ADD COLUMN recurrence_config JSONB;       -- Configuration for custom patterns
ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER REFERENCES tasks(id); -- For recurring tasks
ALTER TABLE tasks ADD COLUMN next_occurrence TIMESTAMP WITH TIME ZONE;   -- Next occurrence for recurring tasks
ALTER TABLE tasks ADD COLUMN occurrences_remaining INTEGER;  -- Remaining occurrences for recurring tasks

-- Add reminder column
ALTER TABLE tasks ADD COLUMN reminder_times JSONB;  -- Array of reminder times
ALTER TABLE tasks ADD COLUMN last_reminder_sent TIMESTAMP WITH TIME ZONE;  -- When last reminder was sent

-- Add indexes for new columns
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_next_occurrence ON tasks(next_occurrence);
CREATE INDEX idx_tasks_parent_task ON tasks(parent_task_id);
```

### 2. New tags table (Priority D1.2)
```sql
CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  name VARCHAR(50) NOT NULL,
  color VARCHAR(7) DEFAULT '#3B82F6',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, name),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_tags_user_id ON tags(user_id);
CREATE INDEX idx_tags_name ON tags(name);
```

### 3. New task_tags junction table (Priority D1.3)
```sql
CREATE TABLE task_tags (
  task_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (task_id, tag_id),
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_id ON task_tags(tag_id);
```

### 4. New events table for event-driven architecture (Priority D1.4)
```sql
CREATE TABLE events (
  event_id UUID PRIMARY KEY,
  event_type VARCHAR(100) NOT NULL,
  event_version VARCHAR(20) NOT NULL DEFAULT '1.0',
  aggregate_type VARCHAR(50) NOT NULL,
  aggregate_id VARCHAR(255) NOT NULL,
  payload JSONB NOT NULL,
  metadata JSONB,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  user_id VARCHAR(255),
  correlation_id UUID
);

CREATE INDEX idx_events_aggregate ON events(aggregate_type, aggregate_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_user_id ON events(user_id);
```

## Migration Strategy

### Phase 1: Schema Evolution
1. **Add new columns to existing tables** with appropriate defaults
2. **Create new tables** (tags, task_tags, events)
3. **Create indexes** for performance
4. **Update foreign key constraints** as needed

### Phase 2: Data Migration
1. **Backfill existing data** where appropriate (e.g., set default priority)
2. **Update application logic** to handle new columns
3. **Test migration scripts** on staging before production

### Phase 3: Feature Activation
1. **Enable new features** gradually
2. **Update API endpoints** to support new fields
3. **Update UI components** to handle new features

## Performance Considerations

### 1. Index Strategy
- **Primary filters**: user_id, completed status, priority
- **Secondary filters**: due_date, next_occurrence
- **Search optimization**: Full-text search indexes for title/description
- **Event queries**: Aggregate-based indexes for event sourcing

### 2. Partitioning Strategy (Future Enhancement)
- **Events table**: Partition by time (monthly partitions)
- **Tasks table**: Potentially partition by user_id for large datasets

### 3. Query Optimization
- **Task listing**: Optimize for common filter combinations
- **Tag queries**: Efficient many-to-many joins
- **Event queries**: Time-based and aggregate-based lookups

## Security Considerations

### 1. Data Isolation
- All queries must include `user_id` filter for multi-tenancy
- Row-level security for sensitive data access
- Proper foreign key constraints to prevent orphaned records

### 2. Data Encryption
- Encrypt sensitive data at rest using database encryption
- Use TLS for all database connections
- Secure credential management for database access

## Scalability Planning

### 1. Connection Management
- Use connection pooling (SQLAlchemy pool settings)
- Implement proper session management
- Optimize query patterns for performance

### 2. Storage Optimization
- Use appropriate data types to minimize storage
- Implement soft deletes where appropriate
- Plan for archiving old data

## Migration Validation Plan

### 1. Pre-Migration Checks
- Backup existing database
- Validate migration scripts on test copy
- Ensure rollback procedures are ready

### 2. Migration Execution
- Run migrations in transaction
- Validate data integrity after migration
- Test application functionality with new schema

### 3. Post-Migration Validation
- Verify all new features work correctly
- Check performance metrics
- Monitor for any issues in production

## Dependencies and Constraints

### 1. Application Dependencies
- Backend models need updates to reflect new schema
- API endpoints need to support new fields
- Frontend components need to handle new features
- MCP tools need to support advanced features

### 2. External Dependencies
- Neon PostgreSQL must support all required features
- JSONB columns for flexible configuration
- UUID generation for event identifiers
- Timestamp with timezone for proper date handling

## Future-Proofing Considerations

### 1. Schema Evolution
- Use nullable columns for optional features
- JSONB for flexible configuration data
- Proper versioning for event schemas
- Migration scripts with rollback capabilities

### 2. Event Sourcing Readiness
- Events table designed for event sourcing pattern
- Aggregate-based organization for consistency
- Metadata fields for distributed tracing
- Correlation IDs for request tracking

This analysis provides the foundation for implementing the database migrations required for Phase V Advanced Cloud Deployment.