-- Rollback migration script for Phase V: Advanced Cloud Deployment
-- Removes priority, due_date, recurrence, and other advanced features from tasks table
-- Drops tags and task_tags tables
-- Drops events table for event-driven architecture

-- DOWN Migration: Revert to Phase IV schema
-- File: 001-add-phase-v-features.down.sql

BEGIN;

-- 1. Remove triggers
DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
DROP FUNCTION IF EXISTS update_updated_at_column();

-- 2. Drop indexes (in reverse order of creation)
DROP INDEX IF EXISTS idx_events_type;
DROP INDEX IF EXISTS idx_events_timestamp;
DROP INDEX IF EXISTS idx_events_aggregate;
DROP INDEX IF EXISTS idx_task_tags_tag_id;
DROP INDEX IF EXISTS idx_task_tags_task_id;
DROP INDEX IF EXISTS idx_tags_name;
DROP INDEX IF EXISTS idx_tags_user_id;
DROP INDEX IF EXISTS idx_tasks_recurrence_pattern;
DROP INDEX IF EXISTS idx_tasks_parent_task;
DROP INDEX IF EXISTS idx_tasks_next_occurrence;
DROP INDEX IF EXISTS idx_tasks_due_date;
DROP INDEX IF EXISTS idx_tasks_priority;

-- 3. Remove foreign key constraint
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS fk_tasks_parent_task_id;

-- 4. Remove check constraint
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_priority;

-- 5. Remove new columns from tasks table
ALTER TABLE tasks DROP COLUMN IF EXISTS last_reminder_sent;
ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_times;
ALTER TABLE tasks DROP COLUMN IF EXISTS occurrences_remaining;
ALTER TABLE tasks DROP COLUMN IF EXISTS next_occurrence;
ALTER TABLE tasks DROP COLUMN IF EXISTS parent_task_id;
ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence_config;
ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence_pattern;
ALTER TABLE tasks DROP COLUMN IF EXISTS due_date;
ALTER TABLE tasks DROP COLUMN IF EXISTS priority;

-- 6. Drop events table
DROP TABLE IF EXISTS events CASCADE;

-- 7. Drop task_tags junction table
DROP TABLE IF EXISTS task_tags CASCADE;

-- 8. Drop tags table
DROP TABLE IF EXISTS tags CASCADE;

COMMIT;