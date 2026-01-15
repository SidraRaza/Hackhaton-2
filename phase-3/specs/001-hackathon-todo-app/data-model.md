# Data Model: hackathon-todo

## Entities

### User
- **Fields**:
  - id: Integer (Primary Key, Auto Increment)
  - email: String (Unique, Not Null)
  - password_hash: String (Not Null)
  - created_at: DateTime (Not Null)
  - updated_at: DateTime (Not Null)
- **Relationships**: One-to-many with Task (user.tasks)
- **Validation**: Email format validation, password strength requirements
- **Indexes**: Unique index on email

### Task
- **Fields**:
  - id: Integer (Primary Key, Auto Increment)
  - title: String (Not Null)
  - description: Text (Optional)
  - completed: Boolean (Default: False)
  - user_id: Integer (Foreign Key to User, Not Null)
  - created_at: DateTime (Not Null)
  - updated_at: DateTime (Not Null)
- **Relationships**: Many-to-one with User (task.user)
- **Validation**: Title length constraints
- **Indexes**: Index on user_id for efficient user-based queries, index on completed status

## State Transitions

### Task State Transitions
- **Active** ↔ **Completed**: User can toggle completion status via PATCH /api/tasks/{id}/complete
- **Created**: New tasks start in Active state
- **Deleted**: Tasks can be permanently deleted by user

## Access Control
- All queries must be filtered by user_id to ensure user isolation
- Users can only access their own tasks
- Authentication required for all task operations