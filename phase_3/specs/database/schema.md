# Database Schema Specification

> **Feature**: Data Models and Storage
> **Phase**: II
> **Status**: Ready for Implementation

## Overview

Define the database schema for the Hackathon II Todo App using SQLModel with PostgreSQL. The schema supports user authentication and task management with proper foreign key relationships and indexing.

## Related Specs

- `@specs/features/task-crud.md` - Task model requirements
- `@specs/features/authentication.md` - User model requirements
- `@specs/api/rest-endpoints.md` - API data requirements

---

## Data Models

### Users Table (Managed by Better Auth)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id`: UUID primary key, auto-generated
- `email`: Unique email address for authentication
- `username`: Unique username for identification
- `full_name`: Optional full name
- `hashed_password`: BCrypt hashed password
- `is_active`: Account status flag
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp

### Tasks Table

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(10) DEFAULT 'medium',
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Fields:**
- `id`: UUID primary key, auto-generated
- `user_id`: Foreign key to users table
- `title`: Task title (1-200 characters)
- `description`: Optional task description (max 1000 characters)
- `status`: Task status ('pending', 'in-progress', 'completed')
- `priority`: Task priority ('low', 'medium', 'high')
- `due_date`: Optional deadline for task
- `completed_at`: Timestamp when task was marked complete
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp

---

## SQLModel/Pydantic Definitions

### User Model
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import uuid
from datetime import datetime

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: Optional[str] = Field(default=None)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="owner")

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class UserUpdate(SQLModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
```

### Task Model
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import uuid
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in-progress"
    completed = "completed"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    due_date: Optional[datetime] = None

class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")

    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to owner
    owner: "User" = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    title: str

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None

class TaskRead(TaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
```

---

## Indexes

### Required Indexes
```sql
-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Tasks table indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
```

### Performance Considerations
- `idx_tasks_user_id`: Critical for user isolation queries
- `idx_tasks_status`: Essential for filtering by completion status
- `idx_tasks_created_at`: Important for chronological sorting
- `idx_tasks_priority`: Needed for priority-based sorting/filtering

---

## Validation Rules

### Users
- Email: Valid email format, unique
- Username: 3-50 alphanumeric characters + underscores/hyphens, unique
- Password: Min 6 characters (validated in application layer)

### Tasks
- Title: 1-200 characters
- Description: Max 1000 characters (optional)
- Status: Must be one of: 'pending', 'in-progress', 'completed'
- Priority: Must be one of: 'low', 'medium', 'high'

---

## Constraints

### Foreign Key Constraints
- `tasks.user_id` references `users.id` with CASCADE delete
- Prevents orphaned tasks when users are deleted

### Check Constraints
```sql
-- Task title length constraint
ALTER TABLE tasks ADD CONSTRAINT chk_task_title_length
CHECK (LENGTH(title) >= 1 AND LENGTH(title) <= 200);

-- Task description length constraint
ALTER TABLE tasks ADD CONSTRAINT chk_task_desc_length
CHECK (LENGTH(description) <= 1000);

-- Valid status values
ALTER TABLE tasks ADD CONSTRAINT chk_task_status
CHECK (status IN ('pending', 'in-progress', 'completed'));

-- Valid priority values
ALTER TABLE tasks ADD CONSTRAINT chk_task_priority
CHECK (priority IN ('low', 'medium', 'high'));
```

---

## Implementation Checklist

### Backend
- [ ] SQLModel User model created
- [ ] SQLModel Task model created
- [ ] Validation rules implemented
- [ ] Relationships defined
- [ ] Indexes applied to database
- [ ] Foreign key constraints implemented
- [ ] Check constraints applied
- [ ] Migration scripts created for schema changes
- [ ] Seed data for testing created

### Security
- [ ] Passwords stored as hashes (BCrypt)
- [ ] No sensitive data stored in plain text
- [ ] User isolation enforced via foreign keys
- [ ] Cascade delete prevents orphaned data