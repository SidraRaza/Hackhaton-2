-- Schema Extensions for Phase V: Advanced Cloud Deployment
-- Defines new tables and schema modifications for advanced features

-- 1. Extended Tasks Table (adding to existing structure)
-- This is already handled in the migration script, but here's the final structure:

/*
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(50);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_config JSONB;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_task_id INTEGER;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS next_occurrence TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS occurrences_remaining INTEGER;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_times JSONB;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS last_reminder_sent TIMESTAMP WITH TIME ZONE;

ALTER TABLE tasks ADD CONSTRAINT chk_priority CHECK (priority IN ('low', 'medium', 'high'));
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_parent_task_id
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE SET NULL;
*/

-- 2. Tags Table Definition
CREATE TABLE IF NOT EXISTS tags (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  name VARCHAR(50) NOT NULL,
  color VARCHAR(7) DEFAULT '#3B82F6',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, name),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for tags table
CREATE INDEX IF NOT EXISTS idx_tags_user_id ON tags(user_id);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);

-- 3. Task-Tags Junction Table Definition
CREATE TABLE IF NOT EXISTS task_tags (
  task_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (task_id, tag_id),
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Indexes for task_tags junction table
CREATE INDEX IF NOT EXISTS idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX IF NOT EXISTS idx_task_tags_tag_id ON task_tags(tag_id);

-- 4. Events Table for Event-Driven Architecture
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

-- Indexes for events table
CREATE INDEX IF NOT EXISTS idx_events_aggregate ON events(aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);

-- 5. Enhanced Tasks Table View with Joins
CREATE OR REPLACE VIEW tasks_with_tags AS
SELECT
  t.id,
  t.user_id,
  t.title,
  t.description,
  t.completed,
  t.priority,
  t.due_date,
  t.recurrence_pattern,
  t.recurrence_config,
  t.parent_task_id,
  t.next_occurrence,
  t.occurrences_remaining,
  t.created_at,
  t.updated_at,
  COALESCE(
    (SELECT json_agg(
      json_build_object(
        'id', tg.id,
        'name', tg.name,
        'color', tg.color
      )
    )
    FROM task_tags tt
    JOIN tags tg ON tt.tag_id = tg.id
    WHERE tt.task_id = t.id),
    '[]'::json
  ) AS tags
FROM tasks t;

-- 6. Functions for Recurrence Calculations
CREATE OR REPLACE FUNCTION calculate_next_occurrence(
  pattern VARCHAR(50),
  config JSONB,
  current_date TIMESTAMP WITH TIME ZONE
) RETURNS TIMESTAMP WITH TIME ZONE AS $$
DECLARE
  next_date TIMESTAMP WITH TIME ZONE;
BEGIN
  CASE pattern
    WHEN 'daily' THEN
      next_date := current_date + INTERVAL '1 day';
    WHEN 'weekly' THEN
      next_date := current_date + INTERVAL '1 week';
    WHEN 'monthly' THEN
      next_date := current_date + INTERVAL '1 month';
    WHEN 'yearly' THEN
      next_date := current_date + INTERVAL '1 year';
    WHEN 'custom' THEN
      -- For custom patterns, use cron expression from config
      -- This would be handled by application logic in practice
      next_date := current_date + INTERVAL '1 day';
    ELSE
      next_date := NULL;
  END CASE;

  RETURN next_date;
END;
$$ LANGUAGE plpgsql;

-- 7. Triggers for Automatic Updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for tasks table
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 8. Sample Data Insertion (for testing)
/*
INSERT INTO tags (user_id, name, color) VALUES
('user-123', 'work', '#EF4444'),
('user-123', 'personal', '#3B82F6'),
('user-123', 'shopping', '#10B981'),
('user-456', 'work', '#EF4444'),
('user-456', 'urgent', '#DC2626');

-- Example of linking tasks to tags
-- INSERT INTO task_tags (task_id, tag_id) VALUES (1, 1), (1, 2); -- Task 1 has 'work' and 'personal' tags
*/