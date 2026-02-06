# Data Model: Task Entity

## Task Entity

### Attributes
- **id** (UUID/string, Primary Key)
  - Unique identifier for each task item
  - Auto-generated upon creation
  - Required field

- **title** (string, Required)
  - Title or description of the task
  - Maximum length: 255 characters
  - Cannot be empty/null

- **description** (string, Optional)
  - Additional details about the task
  - Maximum length: 1000 characters
  - Can be null/empty

- **completed** (boolean)
  - Status of the task completion
  - Default value: false
  - Required field

- **created_at** (datetime)
  - Timestamp when the task was created
  - Auto-populated on creation
  - Required field

- **updated_at** (datetime)
  - Timestamp when the task was last updated
  - Auto-updated on each modification
  - Required field

- **user_id** (UUID/string, Foreign Key)
  - Reference to the user who owns this task
  - Links to users table
  - Required field for data isolation

### Relationships
- **Belongs to**: User (many-to-one relationship)
  - Each task belongs to one user
  - User can have many tasks
  - Foreign key: user_id → users.id

### Validation Rules
- Title must not be empty (length > 0)
- Title must not exceed 255 characters
- Description, if provided, must not exceed 1000 characters
- user_id must reference an existing user
- created_at and updated_at are automatically managed by the system

### State Transitions
- **Created**: New task with completed = false
- **Updated**: Task modified (title, description, or completed status changed)
- **Completed**: Task marked as completed (completed = true)
- **Deleted**: Task removed from the system (soft delete preferred)

### Indexes
- Primary Key: id
- Foreign Key: user_id (for efficient user-based queries)
- Composite Index: (user_id, completed) for efficient filtering
- Index on created_at for chronological ordering