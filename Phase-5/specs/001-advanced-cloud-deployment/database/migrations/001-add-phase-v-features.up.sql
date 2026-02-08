-- Migration script for Phase V: Advanced Cloud Deployment
-- Adds priority, due_date, recurrence, and other advanced features to tasks table
-- Creates tags and task_tags tables for tag management
-- Creates events table for event-driven architecture

-- UP Migration: Forward to Phase V schema
-- File: 001-add-phase-v-features.up.sql

BEGIN;

-- 1. Add new columns to tasks table
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(50);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_config JSONB;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_task_id INTEGER;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS next_occurrence TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS occurrences_remaining INTEGER;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_times JSONB;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS last_reminder_sent TIMESTAMP WITH TIME ZONE;

-- 2. Add constraints for priority column
ALTER TABLE tasks ADD CONSTRAINT chk_priority CHECK (priority IN ('low', 'medium', 'high'));

-- 3. Add foreign key constraint for parent_task_id (deferred to avoid issues during migration)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_tasks_parent_task_id'
        AND table_name = 'tasks'
    ) THEN
        ALTER TABLE tasks ADD CONSTRAINT fk_tasks_parent_task_id
        FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
    END IF;
END $$;

-- 4. Create tags table
CREATE TABLE IF NOT EXISTS tags (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  name VARCHAR(50) NOT NULL,
  color VARCHAR(7) DEFAULT '#3B82F6',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, name)
);

-- 5. Create task_tags junction table
CREATE TABLE IF NOT EXISTS task_tags (
  task_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (task_id, tag_id),
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- 6. Create events table for event-driven architecture
CREATE TABLE IF NOT EXISTS events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

-- 7. Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_next_occurrence ON tasks(next_occurrence);
CREATE INDEX IF NOT EXISTS idx_tasks_parent_task ON tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_recurrence_pattern ON tasks(recurrence_pattern);
CREATE INDEX IF NOT EXISTS idx_tags_user_id ON tags(user_id);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX IF NOT EXISTS idx_task_tags_tag_id ON task_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_events_aggregate ON events(aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);

-- 8. Update existing tasks to have default priority
UPDATE tasks SET priority = 'medium' WHERE priority IS NULL;

-- 9. Add updated_at trigger for tasks table (if not exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMIT;