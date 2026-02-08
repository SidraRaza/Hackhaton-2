# Migration Testing: Phase V Database Evolution

## Overview
This document outlines the testing procedures to verify the successful execution of database migrations for Phase V: Advanced Cloud Deployment. The tests ensure data integrity and functionality of new features (priorities, tags, recurrence, due dates).

## Prerequisites

### 1. Test Environment Setup
```bash
# Install required dependencies
pip install psycopg2-binary pytest alembic sqlmodel

# Set up test database connection
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/todo_test"
```

### 2. Test Data Preparation
```sql
-- Create test data for verification
INSERT INTO users (id, email, name) VALUES
('test-user-1', 'test1@example.com', 'Test User 1'),
('test-user-2', 'test2@example.com', 'Test User 2');

INSERT INTO tasks (user_id, title, description, completed, created_at, updated_at) VALUES
('test-user-1', 'Sample Task 1', 'This is a sample task', false, NOW(), NOW()),
('test-user-1', 'Sample Task 2', 'Another sample task', true, NOW(), NOW()),
('test-user-2', 'User 2 Task', 'Task for second user', false, NOW(), NOW());
```

## Migration Test Suite

### 1. Schema Validation Tests

#### Test 1.1: Verify New Columns Exist
```sql
-- Verify priority column exists with correct properties
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'tasks' AND column_name = 'priority';

-- Expected result:
-- column_name: priority
-- data_type: character varying
-- is_nullable: YES
-- column_default: 'medium'::character varying
```

#### Test 1.2: Verify New Tables Exist
```sql
-- Verify tags table exists with correct structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'tags'
ORDER BY ordinal_position;

-- Expected columns: id, user_id, name, color, created_at
-- Verify task_tags table exists
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'task_tags'
ORDER BY ordinal_position;

-- Expected columns: task_id, tag_id, created_at
```

#### Test 1.3: Verify Constraints Are Applied
```sql
-- Verify priority constraint exists
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'tasks' AND constraint_name LIKE '%priority%';

-- Expected: CHECK constraint named 'chk_priority' or similar
```

### 2. Index Verification Tests

#### Test 2.1: Verify Performance Indexes Exist
```sql
-- Check that required indexes were created
SELECT indexname
FROM pg_indexes
WHERE tablename IN ('tasks', 'tags', 'task_tags', 'events')
AND schemaname = 'public';

-- Expected indexes:
-- idx_tasks_priority, idx_tasks_due_date, idx_tasks_next_occurrence
-- idx_tags_user_id, idx_tags_name
-- idx_task_tags_task_id, idx_task_tags_tag_id
-- idx_events_aggregate, idx_events_timestamp, idx_events_type
```

### 3. Data Integrity Tests

#### Test 3.1: Verify Existing Data Was Preserved
```sql
-- Count existing tasks to ensure none were lost
SELECT COUNT(*) as original_task_count
FROM tasks
WHERE user_id LIKE 'test-user-%';

-- Expected: Should match the number of tasks inserted before migration
```

#### Test 3.2: Verify Default Values Were Applied
```sql
-- Check that existing tasks got default priority
SELECT COUNT(*) as tasks_with_default_priority
FROM tasks
WHERE user_id LIKE 'test-user-%' AND priority = 'medium';

-- Expected: Should equal the number of existing tasks
```

#### Test 3.3: Verify Foreign Key Constraints
```sql
-- Test that foreign key constraints work correctly
BEGIN;
-- This should succeed (valid parent task)
INSERT INTO tasks (user_id, title, parent_task_id)
VALUES ('test-user-1', 'Child Task', (SELECT id FROM tasks WHERE title = 'Sample Task 1' LIMIT 1));

-- This should fail (invalid parent task)
INSERT INTO tasks (user_id, title, parent_task_id)
VALUES ('test-user-1', 'Invalid Child', 999999);
ROLLBACK;
```

### 4. Functional Tests

#### Test 4.1: Test New Features with Extended Schema
```sql
-- Insert a task with new fields
INSERT INTO tasks (user_id, title, priority, due_date, recurrence_pattern, recurrence_config)
VALUES ('test-user-1', 'Test Task with Features', 'high', NOW() + INTERVAL '1 day', 'daily', '{"interval": 1}');

-- Verify insertion worked
SELECT id, title, priority, due_date, recurrence_pattern
FROM tasks
WHERE title = 'Test Task with Features';

-- Expected: All fields should be stored correctly
```

#### Test 4.2: Test Tags Functionality
```sql
-- Create a tag
INSERT INTO tags (user_id, name, color) VALUES ('test-user-1', 'important', '#EF4444');

-- Link task to tag
INSERT INTO task_tags (task_id, tag_id)
VALUES (
  (SELECT id FROM tasks WHERE title = 'Test Task with Features' LIMIT 1),
  (SELECT id FROM tags WHERE name = 'important' LIMIT 1)
);

-- Verify relationship
SELECT t.title, tg.name, tg.color
FROM tasks t
JOIN task_tags tt ON t.id = tt.task_id
JOIN tags tg ON tt.tag_id = tg.id
WHERE t.title = 'Test Task with Features';
```

#### Test 4.3: Test Events Functionality
```sql
-- Insert an event
INSERT INTO events (event_type, aggregate_type, aggregate_id, payload, user_id)
VALUES ('task.created', 'task', '1', '{"title": "Test Task", "user_id": "test-user-1"}', 'test-user-1');

-- Verify event was stored
SELECT event_type, aggregate_type, aggregate_id, user_id
FROM events
WHERE event_type = 'task.created'
LIMIT 1;

-- Expected: Event should be stored with correct fields
```

## Rollback Test Suite

### 1. Rollback Validation
```sql
-- 1. Run the rollback migration
-- (This would be done using your migration tool, e.g., alembic downgrade -1)

-- 2. Verify columns are removed
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'tasks' AND column_name IN ('priority', 'due_date', 'recurrence_pattern');

-- Expected: No rows should be returned

-- 3. Verify tables are dropped
SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('tags', 'task_tags', 'events');

-- Expected: No rows should be returned

-- 4. Verify indexes are removed
SELECT indexname
FROM pg_indexes
WHERE indexname LIKE 'idx_%_priority' OR indexname LIKE 'idx_tags_%';

-- Expected: No rows should be returned
```

## Performance Tests

### 1. Query Performance Validation
```sql
-- Test query performance with new indexes
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test-user-1'
AND priority = 'high'
AND completed = false
ORDER BY due_date DESC
LIMIT 10;

-- Expected: Should use indexes and execute efficiently
```

### 2. Join Performance Validation
```sql
-- Test performance of task-tags join query
EXPLAIN ANALYZE
SELECT t.title, array_agg(tg.name) as tags
FROM tasks t
LEFT JOIN task_tags tt ON t.id = tt.task_id
LEFT JOIN tags tg ON tt.tag_id = tg.id
WHERE t.user_id = 'test-user-1'
GROUP BY t.id, t.title
LIMIT 20;

-- Expected: Should use indexes and execute efficiently
```

## Data Migration Test Cases

### 1. Recurring Task Migration
```sql
-- Insert a recurring task
INSERT INTO tasks (user_id, title, recurrence_pattern, recurrence_config, due_date)
VALUES ('test-user-1', 'Weekly Meeting', 'weekly', '{"days_of_week": [1]}', NOW());

-- Verify next occurrence calculation
-- (This would be done by the application logic, but schema supports it)
SELECT title, recurrence_pattern, recurrence_config, due_date
FROM tasks
WHERE title = 'Weekly Meeting';
```

### 2. Priority-Based Filtering
```sql
-- Insert tasks with different priorities
INSERT INTO tasks (user_id, title, priority) VALUES
('test-user-1', 'Low Priority Task', 'low'),
('test-user-1', 'High Priority Task', 'high');

-- Test filtering by priority
SELECT title, priority
FROM tasks
WHERE user_id = 'test-user-1' AND priority = 'high';

-- Expected: Should return only the high priority task
```

## Migration Validation Checklist

### Pre-Migration Verification
- [ ] Database backup created and verified
- [ ] Migration scripts reviewed for correctness
- [ ] Rollback procedures tested and documented
- [ ] Test environment prepared with sample data
- [ ] Dependencies verified (PostgreSQL 15+, extensions, etc.)

### Migration Execution Verification
- [ ] Migration runs successfully without errors
- [ ] All new columns exist with correct data types
- [ ] All new tables exist with correct structures
- [ ] All constraints are properly applied
- [ ] All indexes are created for performance
- [ ] Existing data remains intact
- [ ] Default values are correctly applied to existing records

### Post-Migration Verification
- [ ] New features work correctly with extended schema
- [ ] Performance benchmarks meet requirements
- [ ] Foreign key relationships function properly
- [ ] Check constraints enforce data integrity
- [ ] Application can read/write to new fields
- [ ] Event-driven architecture can utilize new tables
- [ ] Tags and task relationships work as expected

### Rollback Verification
- [ ] Rollback migration executes successfully
- [ ] Schema returns to pre-migration state
- [ ] Data integrity is preserved during rollback
- [ ] Application continues to function (with reduced features)

## Expected Test Results

### Success Criteria
1. All schema tests pass (columns, tables, constraints exist)
2. All data integrity tests pass (no data loss)
3. All functional tests pass (new features work)
4. All performance tests meet benchmarks
5. Rollback tests pass (safe to revert if needed)

### Failure Criteria
1. Any schema test fails (migration incomplete)
2. Data integrity test fails (data loss occurred)
3. Functional test fails (features not working)
4. Performance degradation beyond acceptable thresholds
5. Rollback fails (unsafe to proceed)

## Test Execution Script

```bash
#!/bin/bash
# migration-test-runner.sh

echo "Starting Phase V Database Migration Tests..."

# Set up test environment
export DATABASE_URL=$TEST_DATABASE_URL

# Run schema validation tests
echo "Running schema validation tests..."
psql $DATABASE_URL -f tests/schema-validation.sql

# Run data integrity tests
echo "Running data integrity tests..."
psql $DATABASE_URL -f tests/data-integrity.sql

# Run functional tests
echo "Running functional tests..."
psql $DATABASE_URL -f tests/functional.sql

# Run performance tests
echo "Running performance tests..."
psql $DATABASE_URL -f tests/performance.sql

echo "All tests completed successfully!"
```

## Troubleshooting Guide

### Common Issues and Solutions

1. **Migration Timeout Errors**:
   - Solution: Increase statement timeout, run migration during low-traffic period

2. **Constraint Violation Errors**:
   - Solution: Check data integrity before migration, clean up problematic data

3. **Index Creation Failures**:
   - Solution: Create indexes CONCURRENTLY to avoid table locks

4. **Foreign Key Constraint Failures**:
   - Solution: Temporarily disable constraints during migration if needed

5. **Insufficient Disk Space**:
   - Solution: Check available space before migration, consider offline migration

This testing suite ensures the migration is safe, preserves data integrity, and enables all new features for Phase V Advanced Cloud Deployment.