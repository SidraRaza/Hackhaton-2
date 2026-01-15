# AI-Powered Todo Chatbot Specification

## Project Overview

The AI-Powered Todo Chatbot is a conversational interface for managing todos through natural language. The system uses OpenAI's Agents SDK with Model Context Protocol (MCP) server architecture to enable AI agents to interact with task management operations via standardized tools.

## Objectives

- Implement a conversational interface for all basic todo management features
- Enable natural language processing for task creation, listing, completion, deletion, and updates
- Utilize MCP server architecture for standardized AI-to-application interaction
- Maintain stateless server architecture with database persistence
- Provide scalable and resilient todo management system

## Functional Requirements

### 1. Natural Language Processing
- System shall understand natural language commands for task management
- System shall support commands for creating, listing, completing, deleting, and updating tasks
- System shall maintain conversation context across multiple interactions

### 2. Task Management
- System shall allow users to add new tasks via natural language
- System shall allow users to list tasks with various filters (all, pending, completed)
- System shall allow users to mark tasks as complete
- System shall allow users to delete tasks
- System shall allow users to update task details

### 3. Conversation Management
- System shall maintain conversation history in database
- System shall support resuming conversations after server restart
- System shall provide contextual responses based on conversation history

### 4. MCP Integration
- System shall expose standardized MCP tools for AI agents
- System shall support tool composition and chaining
- System shall provide consistent responses for MCP tool invocations

## Non-Functional Requirements

### Performance
- Response time under 2 seconds for typical requests
- Support for concurrent users and requests
- Efficient database queries for task operations

### Scalability
- Stateless server architecture for horizontal scaling
- Database-backed session management
- Load balancer compatibility

### Reliability
- High availability with minimal downtime
- Graceful error handling and recovery
- Data consistency and integrity

### Security
- User authentication and authorization
- Secure data transmission
- Protection against unauthorized access

## Natural Language Commands

| User Says | System Action |
|-----------|---------------|
| "Add a task to buy groceries" | Call add_task with title "Buy groceries" |
| "Show me all my tasks" | Call list_tasks with status "all" |
| "What's pending?" | Call list_tasks with status "pending" |
| "Mark task 3 as complete" | Call complete_task with task_id 3 |
| "Delete the meeting task" | Call list_tasks first, then delete_task |
| "Change task 1 to 'Call mom tonight'" | Call update_task with new title |
| "I need to remember to pay bills" | Call add_task with title "Pay bills" |
| "What have I completed?" | Call list_tasks with status "completed" |

## System Architecture

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐     ┌─────────────────┐
│                 │     │              FastAPI Server                   │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │     │                 │
│  ChatKit UI     │────▶│  │         Chat Endpoint                  │  │     │    Neon DB      │
│  (Frontend)     │     │  │  POST /api/chat                        │  │     │  (PostgreSQL)   │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │  - tasks        │
│                 │     │                  ▼                           │     │  - conversations│
│                 │     │  ┌────────────────────────────────────────┐  │     │  - messages     │
│                 │     │  │      OpenAI Agents SDK                 │  │     │                 │
│                 │     │  │      (Agent + Runner)                  │  │     │                 │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │                 │
│                 │     │                  ▼                           │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │────▶│                 │
│                 │     │  │         MCP Server                 │  │     │                 │
│                 │     │  │  (MCP Tools for Task Operations)       │  │◀────│                 │
│                 │     │  └────────────────────────────────────────┘  │     │                 │
└─────────────────┘     └──────────────────────────────────────────────┘     └─────────────────┘
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | OpenAI ChatKit |
| Backend | Python FastAPI |
| AI Framework | OpenAI Agents SDK |
| MCP Server | Official MCP SDK |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth |

## Database Models

### Task Model
- user_id (string, required): Foreign key to user
- id (integer, primary key): Unique task identifier
- title (string, required): Task title
- description (string, optional): Task description
- completed (boolean): Completion status
- created_at (datetime): Creation timestamp
- updated_at (datetime): Last update timestamp

### Conversation Model
- user_id (string, required): Foreign key to user
- id (integer, primary key): Unique conversation identifier
- created_at (datetime): Creation timestamp
- updated_at (datetime): Last update timestamp

### Message Model
- user_id (string, required): Foreign key to user
- id (integer, primary key): Unique message identifier
- conversation_id (integer, required): Foreign key to conversation
- role (string, required): Message role (user/assistant)
- content (string, required): Message content
- created_at (datetime): Creation timestamp

## API Endpoints

### Chat Endpoint
- Method: POST
- Endpoint: `/api/{user_id}/chat`
- Description: Send message & get AI response

#### Request Parameters
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | integer | No | Existing conversation ID (creates new if not provided) |
| message | string | Yes | User's natural language message |

#### Response Parameters
| Field | Type | Description |
|-------|------|-------------|
| conversation_id | integer | The conversation ID |
| response | string | AI assistant's response |
| tool_calls | array | List of MCP tools invoked |

## MCP Tools Specification

The MCP server must expose the following tools for the AI agent:

### Tool: add_task
- Purpose: Create a new task
- Parameters: user_id (string, required), title (string, required), description (string, optional)
- Returns: task_id, status, title
- Example Input: `{"user_id": "ziakhan", "title": "Buy groceries", "description": "Milk, eggs, bread"}`
- Example Output: `{"task_id": 5, "status": "created", "title": "Buy groceries"}`

### Tool: list_tasks
- Purpose: Retrieve tasks from the list
- Parameters: user_id (string, required), status (string, optional: "all", "pending", "completed")
- Returns: Array of task objects
- Example Input: `{"user_id": "ziakhan", "status": "pending"}`
- Example Output: `[{"id": 1, "title": "Buy groceries", "completed": false}, ...]`

### Tool: complete_task
- Purpose: Mark a task as complete
- Parameters: user_id (string, required), task_id (integer, required)
- Returns: task_id, status, title
- Example Input: `{"user_id": "ziakhan", "task_id": 3}`
- Example Output: `{"task_id": 3, "status": "completed", "title": "Call mom"}`

### Tool: delete_task
- Purpose: Remove a task from the list
- Parameters: user_id (string, required), task_id (integer, required)
- Returns: task_id, status, title
- Example Input: `{"user_id": "ziakhan", "task_id": 2}`
- Example Output: `{"task_id": 2, "status": "deleted", "title": "Old task"}`

### Tool: update_task
- Purpose: Modify task title or description
- Parameters: user_id (string, required), task_id (integer, required), title (string, optional), description (string, optional)
- Returns: task_id, status, title
- Example Input: `{"user_id": "ziakhan", "task_id": 1, "title": "Buy groceries and fruits"}`
- Example Output: `{"task_id": 1, "status": "updated", "title": "Buy groceries and fruits"}`

## Agent Behavior Specification

| Behavior | Description |
|----------|-------------|
| Task Creation | When user mentions adding/creating/remembering something, use add_task |
| Task Listing | When user asks to see/show/list tasks, use list_tasks with appropriate filter |
| Task Completion | When user says done/complete/finished, use complete_task |
| Task Deletion | When user says delete/remove/cancel, use delete_task |
| Task Update | When user says change/update/rename, use update_task |
| Confirmation | Always confirm actions with friendly response |
| Error Handling | Gracefully handle task not found and other errors |

## Conversation Flow (Stateless Request Cycle)

1. Receive user message
2. Fetch conversation history from database
3. Build message array for agent (history + new message)
4. Store user message in database
5. Run agent with MCP tools
6. Agent invokes appropriate MCP tool(s)
7. Store assistant response in database
8. Return response to client
9. Server holds NO state (ready for next request)

## Key Architecture Benefits

| Aspect | Benefit |
|--------|---------|
| MCP Tools | Standardized interface for AI to interact with your app |
| Single Endpoint | Simpler API — AI handles routing to tools |
| Stateless Server | Scalable, resilient, horizontally scalable |
| Tool Composition | Agent can chain multiple tools in one turn |

## Deliverables

- GitHub repository with:
  - `/frontend` – ChatKit-based UI
  - `/backend` – FastAPI + Agents SDK + MCP
  - `/specs` – Specification files for agent and MCP tools
  - Database migration scripts
  - README with setup instructions

## Success Criteria

- Working chatbot that manages tasks through natural language via MCP tools
- Maintains conversation context via database (stateless server)
- Provides helpful responses with action confirmations
- Handles errors gracefully
- Resumes conversations after server restart

## OpenAI ChatKit Setup & Deployment

### Domain Allowlist Configuration (Required for Hosted ChatKit)
- Deploy frontend first to get a production URL
- Add domain to OpenAI's allowlist at: https://platform.openai.com/settings/organization/security/domain-allowlist
- Obtain domain key and configure in NEXT_PUBLIC_OPENAI_DOMAIN_KEY environment variable