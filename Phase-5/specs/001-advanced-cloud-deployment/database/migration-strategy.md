# Database Migration Strategy: Phase V Advanced Cloud Deployment

## Overview
This document outlines the migration strategy for evolving the Phase IV database schema to support Phase V advanced features (priorities, tags, search, recurrence, due dates) while maintaining data integrity and ensuring zero-downtime deployment.

## Migration Objectives
1. **Evolve existing schema** to support advanced features without data loss
2. **Maintain backward compatibility** during transition period
3. **Ensure zero-downtime deployment** with proper migration procedures
4. **Provide robust rollback capabilities** in case of issues
5. **Preserve data integrity** throughout the migration process

## Migration Approach: Phased Evolution

### Phase 1: Schema Extension (Safe, Non-Breaking Changes)
- Add new columns with default values
- Create new tables (tags, task_tags, events)
- Add indexes for performance
- No changes to existing functionality

### Phase 2: Data Population (Backfill Existing Data)
- Populate new columns with appropriate defaults for existing records
- Create default tags for existing users if needed
- Update application logic to use new fields

### Phase 3: Feature Activation (Gradual Rollout)
- Enable new features gradually
- Monitor for any issues
- Provide fallback mechanisms

## Detailed Migration Steps

### Step 1: Pre-Migration Preparation
```sql
-- 1. Create backup of current schema and data
-- This would be done externally before running migrations
-- pg_dump --schema-only todo_db > backup_schema_before_migration.sql
-- pg_dump --data-only --table=users --table=tasks --table=conversations --table=messages todo_db > backup_data_before_migration.sql

-- 2. Create migration log table
CREATE TABLE IF NOT EXISTS migration_log (
  id SERIAL PRIMARY KEY,
  migration_name VARCHAR(255) NOT NULL,
  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP,
  status VARCHAR(20) DEFAULT 'running', -- running, completed, failed, rolled_back
  rollback_script TEXT,
  notes TEXT
);

-- 3. Start migration log entry
INSERT INTO migration_log (migration_name, notes)
VALUES ('Phase_V_Advanced_Features', 'Starting Phase V schema evolution');
```

### Step 2: Safe Schema Extensions (Transaction 1)
```sql
-- Begin transaction for safe schema changes
BEGIN;

-- Add new columns to tasks table with defaults
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium',
ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(50),
ADD COLUMN IF NOT EXISTS recurrence_config JSONB,
ADD COLUMN IF NOT EXISTS parent_task_id INTEGER,
ADD COLUMN IF NOT EXISTS next_occurrence TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS occurrences_remaining INTEGER,
ADD COLUMN IF NOT EXISTS reminder_times JSONB,
ADD COLUMN IF NOT EXISTS last_reminder_sent TIMESTAMP WITH TIME ZONE;

-- Add constraints for priority column
ALTER TABLE tasks ADD CONSTRAINT chk_priority CHECK (priority IN ('low', 'medium', 'high'));

-- Add foreign key constraint for parent_task_id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_tasks_parent_task_id'
        AND table_name = 'tasks'
    ) THEN
        ALTER TABLE tasks ADD CONSTRAINT fk_tasks_parent_task_id
        FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Update migration log
UPDATE migration_log
SET notes = CONCAT(notes, ', Schema extensions added')
WHERE migration_name = 'Phase_V_Advanced_Features'
AND status = 'running';

COMMIT;
```

### Step 3: Create New Tables (Transaction 2)
```sql
-- Begin transaction for new table creation
BEGIN;

-- Create tags table
CREATE TABLE IF NOT EXISTS tags (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  name VARCHAR(50) NOT NULL,
  color VARCHAR(7) DEFAULT '#3B82F6',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, name),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create task_tags junction table
CREATE TABLE IF NOT EXISTS task_tags (
  task_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (task_id, tag_id),
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Create events table for event-driven architecture
CREATE TABLE IF NOT EXISTS events (
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

-- Update migration log
UPDATE migration_log
SET notes = CONCAT(notes, ', New tables created')
WHERE migration_name = 'Phase_V_Advanced_Features'
AND status = 'running';

COMMIT;
```

### Step 4: Create Performance Indexes (Transaction 3)
```sql
-- Begin transaction for index creation
BEGIN;

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_next_occurrence ON tasks(next_occurrence);
CREATE INDEX IF NOT EXISTS idx_tasks_parent_task ON tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_recurrence_pattern ON tasks(recurrence_pattern);

-- Create indexes for new tables
CREATE INDEX IF NOT EXISTS idx_tags_user_id ON tags(user_id);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX IF NOT EXISTS idx_task_tags_tag_id ON task_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_events_aggregate ON events(aggregate_type, aggregate_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);

-- Update migration log
UPDATE migration_log
SET notes = CONCAT(notes, ', Performance indexes created')
WHERE migration_name = 'Phase_V_Advanced_Features'
AND status = 'running';

COMMIT;
```

### Step 5: Data Population (Transaction 4)
```sql
-- Begin transaction for data population
BEGIN;

-- Backfill existing tasks with default priority
UPDATE tasks
SET priority = 'medium'
WHERE priority IS NULL;

-- Set updatable timestamp for updated_at column
-- (This is handled by database triggers in production)

-- Update migration log
UPDATE migration_log
SET notes = CONCAT(notes, ', Existing data backfilled')
WHERE migration_name = 'Phase_V_Advanced_Features'
AND status = 'running';

COMMIT;
```

## Rollback Strategy

### Complete Rollback Script
```sql
-- 1. Drop new indexes (except for safety)
DROP INDEX IF EXISTS idx_tasks_priority;
DROP INDEX IF EXISTS idx_tasks_due_date;
DROP INDEX IF EXISTS idx_tasks_next_occurrence;
DROP INDEX IF EXISTS idx_tasks_parent_task;
DROP INDEX IF EXISTS idx_tasks_recurrence_pattern;
DROP INDEX IF EXISTS idx_tags_user_id;
DROP INDEX IF EXISTS idx_tags_name;
DROP INDEX IF EXISTS idx_task_tags_task_id;
DROP INDEX IF EXISTS idx_task_tags_tag_id;
DROP INDEX IF EXISTS idx_events_aggregate;
DROP INDEX IF EXISTS idx_events_timestamp;
DROP INDEX IF EXISTS idx_events_type;

-- 2. Drop new tables
DROP TABLE IF EXISTS task_tags CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS events CASCADE;

-- 3. Drop new columns from tasks
ALTER TABLE tasks
DROP COLUMN IF EXISTS priority,
DROP COLUMN IF EXISTS due_date,
DROP COLUMN IF EXISTS recurrence_pattern,
DROP COLUMN IF EXISTS recurrence_config,
DROP COLUMN IF EXISTS parent_task_id,
DROP COLUMN IF EXISTS next_occurrence,
DROP COLUMN IF EXISTS occurrences_remaining,
DROP COLUMN IF EXISTS reminder_times,
DROP COLUMN IF EXISTS last_reminder_sent;

-- 4. Remove constraints
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS chk_priority;
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS fk_tasks_parent_task_id;

-- 5. Update migration log to indicate rollback
UPDATE migration_log
SET status = 'rolled_back',
    completed_at = CURRENT_TIMESTAMP
WHERE migration_name = 'Phase_V_Advanced_Features'
AND status = 'running';
```

### Partial Rollback Options
1. **Feature-level rollback**: Disable specific features without dropping schema
2. **Table-level rollback**: Drop new tables while keeping schema extensions
3. **Column-level rollback**: Drop specific columns while keeping others

## Zero-Downtime Deployment Strategy

### Approach 1: Dark Launch Pattern
1. Deploy new schema without enabling features
2. Test new schema with internal tools
3. Gradually enable features with feature flags
4. Monitor for any issues

### Approach 2: Blue-Green Deployment
1. Deploy new schema to "green" environment
2. Migrate data to new schema
3. Switch traffic from "blue" to "green"
4. Verify functionality in production
5. Decommission "blue" environment

### Approach 3: Shadow Migration
1. Run new schema in parallel with old schema
2. Write to both schemas simultaneously
3. Compare reads from both schemas
4. Gradually switch reads to new schema
5. Remove old schema after verification

## Migration Validation Plan

### Pre-Migration Validation
- [ ] Database backup completed successfully
- [ ] Migration scripts tested on staging environment
- [ ] Rollback procedures verified
- [ ] Application compatibility confirmed with extended schema
- [ ] Performance tests completed with new schema

### During Migration Validation
- [ ] Transaction completion verified
- [ ] Schema integrity checks passed
- [ ] Data consistency verified
- [ ] Index creation completed successfully

### Post-Migration Validation
- [ ] All new columns populated correctly
- [ ] New tables accessible and functional
- [ ] Performance benchmarks met
- [ ] Application features working with new schema
- [ ] Event-driven architecture operational

## Risk Mitigation

### Risk: Data Loss During Migration
**Mitigation**: Complete backup before migration, run in transactions, test rollback procedures

### Risk: Downtime During Migration
**Mitigation**: Use online schema change tools, implement blue-green deployment, minimize migration window

### Risk: Application Compatibility Issues
**Mitigation**: Thorough testing in staging, gradual feature rollout, fallback mechanisms

### Risk: Performance Degradation
**Mitigation**: Index planning, performance testing, monitoring during and after migration

## Performance Considerations

### Large Dataset Handling
- For tables with millions of records, use chunked updates
- Consider maintenance windows for large migrations
- Monitor lock times during schema changes

### Index Creation Impact
- Create indexes CONCURRENTLY to avoid table locking
- Consider creating indexes during low-traffic periods
- Monitor index creation progress

### Monitoring During Migration
- Database connection count
- Query performance metrics
- Lock contention monitoring
- Storage space utilization

## Migration Execution Checklist

### Pre-Execution
- [ ] Stakeholder notification sent
- [ ] Maintenance window scheduled
- [ ] Database backup verified
- [ ] Staging environment migration successful
- [ ] Rollback plan rehearsed

### Execution
- [ ] Migration script started with monitoring
- [ ] Progress tracked in real-time
- [ ] Performance metrics monitored
- [ ] Error logs checked continuously

### Post-Execution
- [ ] Data integrity verified
- [ ] Application functionality tested
- [ ] Performance metrics validated
- [ ] Migration completion logged
- [ ] Stakeholders notified of completion

## Rollback Trigger Conditions

### Automatic Rollback
- Migration timeout (> 30 minutes)
- Data integrity check failures
- Critical application errors post-migration

### Manual Rollback
- Performance degradation > 50%
- Unexpected data corruption
- Business stakeholder request

This migration strategy ensures a safe, reliable evolution of the database schema to support Phase V advanced features while maintaining data integrity and minimizing risk.