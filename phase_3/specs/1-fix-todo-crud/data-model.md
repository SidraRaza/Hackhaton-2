# Data Model: Todo Entity

## Todo Entity

### Attributes
- **id** (UUID/string, Primary Key)
  - Unique identifier for each todo item
  - Auto-generated upon creation
  - Required field

- **title** (string, Required)
  - Title or description of the todo
  - Maximum length: 255 characters
  - Cannot be empty/null

- **description** (string, Optional)
  - Additional details about the todo
  - Maximum length: 1000 characters
  - Can be null/empty

- **completed** (boolean)
  - Status of the todo completion
  - Default value: false
  - Required field

- **createdAt** (datetime)
  - Timestamp when the todo was created
  - Auto-populated on creation
  - Required field

- **updatedAt** (datetime)
  - Timestamp when the todo was last updated
  - Auto-updated on each modification
  - Required field

- **userId** (UUID/string, Foreign Key)
  - Reference to the user who owns this todo
  - Links to users table
  - Required field for data isolation

### Relationships
- **Belongs to**: User (many-to-one relationship)
  - Each todo belongs to one user
  - User can have many todos
  - Foreign key: userId → users.id

### Validation Rules
- Title must not be empty (length > 0)
- Title must not exceed 255 characters
- Description, if provided, must not exceed 1000 characters
- userId must reference an existing user
- createdAt and updatedAt are automatically managed by the system

### State Transitions
- **Created**: New todo with completed = false
- **Updated**: Todo modified (title, description, or completed status changed)
- **Completed**: Todo marked as completed (completed = true)
- **Deleted**: Todo removed from the system (soft delete preferred)

### Indexes
- Primary Key: id
- Foreign Key: userId (for efficient user-based queries)
- Composite Index: (userId, completed) for efficient filtering
- Index on createdAt for chronological ordering