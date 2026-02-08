# Data Model: Integrate All Backend Features into Frontend

## Phase 1: Data Model Design

### Entity: SearchResult
**Description**: Represents a task with relevance score and matching criteria from search results

**Fields**:
- task: Task (the actual task object)
- relevance_score: number (score indicating how well the task matches the search query)
- matching_criteria: string[] (list of criteria that matched the search query)

**Relationships**:
- References Task entity for the actual task data

### Entity: Notification
**Description**: Real-time alert with type, content, timestamp, and delivery status

**Fields**:
- id: string (unique identifier for the notification)
- type: string (type of notification: 'reminder', 'task_update', 'system', etc.)
- title: string (notification title)
- message: string (notification message content)
- timestamp: Date (when the notification was created)
- delivery_status: string (status of delivery: 'sent', 'delivered', 'read', etc.)
- user_id: string (ID of the user receiving the notification)
- task_id?: number (optional reference to a related task)
- priority: string (priority level: 'low', 'medium', 'high')

**Relationships**:
- Belongs to User (user who receives the notification)
- Optionally references Task (for task-related notifications)

### Entity: ChatMessage
**Description**: Conversational exchange with user input and AI response

**Fields**:
- id: string (unique identifier for the message)
- conversation_id: string (ID of the conversation this message belongs to)
- sender: string (who sent the message: 'user' or 'ai')
- content: string (the actual message content)
- timestamp: Date (when the message was sent/received)
- status: string (delivery status: 'sending', 'sent', 'delivered', 'error')
- user_id: string (ID of the user participating in the conversation)

**Relationships**:
- Belongs to Conversation (the conversation this message is part of)

### Entity: Conversation
**Description**: Collection of messages in a chat session

**Fields**:
- id: string (unique identifier for the conversation)
- user_id: string (ID of the user who owns the conversation)
- title?: string (optional title for the conversation)
- created_at: Date (when the conversation was created)
- updated_at: Date (when the conversation was last updated)
- is_active: boolean (whether the conversation is currently active)

**Relationships**:
- Belongs to User (user who owns the conversation)
- Contains multiple ChatMessage entities

### Entity: AnalyticsData
**Description**: Aggregated task metrics and productivity insights

**Fields**:
- user_id: string (ID of the user whose data is being analyzed)
- period_start: Date (start of the analytics period)
- period_end: Date (end of the analytics period)
- task_completion_rate: number (percentage of tasks completed in the period)
- priority_distribution: object (distribution of completed tasks by priority)
- average_completion_time: number (average time to complete tasks)
- productivity_score: number (calculated productivity score)
- recurring_completion_rate: number (completion rate for recurring tasks)
- peak_productivity_hours: number[] (hours of day when user is most productive)

**Relationships**:
- Belongs to User (user whose analytics this is)

### State Transitions
- Notification can transition from 'sent' to 'delivered' to 'read'
- ChatMessage can transition from 'sending' to 'sent' to 'delivered'
- Conversation can transition from 'active' to 'archived'
- AnalyticsData is typically regenerated for each new period rather than transitioning