# Data Model: AI-Powered Conversational Task Management

## Entity: Conversation

**Description**: Represents a user's chat session with the AI assistant, containing metadata like user_id and creation timestamp.

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the conversation
- `user_id`: String (Foreign Key) - Reference to the user who owns this conversation
- `title`: String (Optional) - Auto-generated title based on first message or topic
- `created_at`: DateTime - Timestamp when the conversation was initiated
- `updated_at`: DateTime - Timestamp when the conversation was last updated
- `is_active`: Boolean - Whether the conversation is currently active

**Relationships**:
- One-to-Many: Conversation → Messages (one conversation has many messages)
- Many-to-One: Conversation → User (many conversations belong to one user)

**Validation Rules**:
- `user_id` must reference a valid user in the system
- `created_at` must be in the past
- `updated_at` must be greater than or equal to `created_at`

## Entity: Message

**Description**: Represents individual messages within a conversation, including role (user, assistant, tool) and content.

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the message
- `conversation_id`: UUID (Foreign Key) - Reference to the conversation this message belongs to
- `role`: String (Enum) - Type of participant (user, assistant, tool)
- `content`: Text - The actual message content
- `timestamp`: DateTime - When the message was created
- `tool_call_id`: String (Optional) - ID of tool call if this is a tool message
- `tool_response`: JSON (Optional) - Response from tool call if applicable

**Relationships**:
- Many-to-One: Message → Conversation (many messages belong to one conversation)
- One-to-Many: Message → ToolResponses (one message may have many tool responses)

**Validation Rules**:
- `conversation_id` must reference a valid conversation
- `role` must be one of: "user", "assistant", or "tool"
- `content` must not be empty
- `timestamp` must be in the past or present

## Entity: Task (Existing from Phase 2)

**Description**: Existing entity from Phase 2 that represents user tasks, with attributes like title, description, completion status, and user association.

**Fields**:
- `id`: UUID (Primary Key) - Unique identifier for the task
- `user_id`: String (Foreign Key) - Reference to the user who owns this task
- `title`: String - Title of the task
- `description`: Text (Optional) - Detailed description of the task
- `completed`: Boolean - Whether the task is completed
- `due_date`: DateTime (Optional) - When the task is due
- `priority`: String (Enum) - Priority level (low, medium, high)
- `created_at`: DateTime - When the task was created
- `updated_at`: DateTime - When the task was last updated

**Relationships**:
- Many-to-One: Task → User (many tasks belong to one user)

**Validation Rules**:
- `user_id` must reference a valid user in the system
- `title` must not be empty
- `priority` must be one of: "low", "medium", or "high"
- `due_date` (if provided) must be in the future

## State Transitions

### Task State Transitions
- **Active** → **Completed**: When task is marked as completed via AI or traditional interface
- **Completed** → **Active**: When task is marked as incomplete via AI or traditional interface

### Conversation State Transitions
- **Inactive** → **Active**: When a new message is added to the conversation
- **Active** → **Inactive**: When a timeout period has passed without new messages

## Indexes

### Conversation Table
- Index on `user_id` for efficient user-specific queries
- Index on `created_at` for chronological ordering

### Message Table
- Index on `conversation_id` for efficient conversation-specific queries
- Index on `timestamp` for chronological ordering
- Composite index on `(conversation_id, timestamp)` for efficient conversation timeline queries

### Task Table (Existing)
- Index on `user_id` for efficient user-specific queries
- Index on `completed` for filtering completed/incomplete tasks
- Index on `due_date` for deadline-based queries