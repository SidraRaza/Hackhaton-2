# Data Model for Improve Todo Application

Based on the key entities identified in the feature specification, here are the data models:

## Todo Entity
Represents a user task with the following attributes:
- **id**: Unique identifier (UUID/string)
- **title**: String, required (cannot be empty)
- **description**: Optional string
- **status**: Enum (pending/completed), default: pending
- **createdAt**: Timestamp, auto-generated
- **updatedAt**: Timestamp, auto-generated
- **dueDate**: Optional timestamp
- **userId**: Foreign key to User entity (for authenticated users)

**Validation rules**:
- Title must not be empty
- Status must be one of allowed values (pending, completed)
- createdAt and updatedAt are managed automatically

## User Entity
Represents an authenticated user with the following attributes:
- **id**: Unique identifier (UUID/string)
- **email**: String, required, unique
- **name**: String, optional
- **passwordHash**: String, required (for registered users)
- **createdAt**: Timestamp, auto-generated
- **updatedAt**: Timestamp, auto-generated
- **jwtToken**: Session token (managed by auth system)

**Validation rules**:
- Email must be valid format and unique
- Password must meet security requirements
- createdAt and updatedAt are managed automatically

## ChatMessage Entity
Represents a message in the chatbot conversation with the following attributes:
- **id**: Unique identifier (UUID/string)
- **sender**: Enum (user/system), required
- **content**: String, required (cannot be empty)
- **timestamp**: Timestamp, auto-generated
- **conversationId**: String, groups related messages
- **messageType**: Enum (text/command/response), default: text
- **userId**: Foreign key to User entity (for authenticated users)

**Validation rules**:
- Content must not be empty
- Sender must be one of allowed values (user, system)
- timestamp is managed automatically
- conversationId groups related messages for continuity