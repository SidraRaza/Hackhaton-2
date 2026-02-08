# CLAUDE.md
## Backend Service: Advanced Cloud Deployment

### Service Context
Backend service for Phase V: Advanced Cloud Deployment featuring event-driven architecture with Kafka/Redpanda, Dapr integration, and advanced task features (priorities, tags, search, recurrence, due dates).

### Technology Stack
- **Framework**: FastAPI 0.104+
- **Database**: SQLModel (SQLAlchemy + Pydantic)
- **Events**: Kafka/Redpanda via Dapr pub/sub
- **Runtime**: Dapr sidecar for cloud-native building blocks
- **Testing**: pytest, tox, mypy
- **API Documentation**: OpenAPI/Swagger with automatic generation

### Key Components
- `/src/models`: Extended data models with priority, tags, recurrence, due_date
- `/src/services`: Business logic for advanced features
- `/src/api`: REST API endpoints with enhanced functionality
- `/src/database`: Database connection and session management
- `/src/dapr`: Dapr integration utilities
- `/src/events`: Event publishing and consumption
- `/src/utils`: Helper functions including recurrence engine
- `/src/middleware`: Request logging, authentication, rate limiting

### Advanced Features Implemented
- **Priority System**: Low/Medium/High priority levels with filtering/sorting
- **Tag Management**: Create, assign, filter tasks by tags with autocomplete
- **Search & Filter**: Full-text search on title/description with multiple filters
- **Sorting**: Multi-column sorting with primary/secondary criteria
- **Recurring Tasks**: Daily/weekly/monthly/yearly/custom patterns with series management
- **Due Dates & Reminders**: Date/time picker with browser notifications
- **Event-Driven**: All operations emit events via Kafka/Redpanda
- **Dapr Integration**: Service invocation, pub/sub, state management, secrets

### Event Schema
- `task.created`: Emitted when new task is created
- `task.updated`: Emitted when task is updated (includes changes)
- `task.completed`: Emitted when task is completed (handles recurrence)
- `task.deleted`: Emitted when task is deleted
- `task.recurrence_created`: Emitted when next occurrence is generated
- `reminder.triggered`: Emitted when reminder time is reached
- `notification.sent`: Emitted when notification is delivered

### Dapr Components Used
- **Pub/Sub**: Kafka component for event streaming
- **State Store**: PostgreSQL component for conversation state
- **Secrets**: Kubernetes secrets via Dapr secret store
- **Service Invocation**: Inter-service communication
- **Bindings**: Cron bindings for scheduled operations

### API Endpoints
- `POST /api/tasks`: Create task with priority, tags, due_date, recurrence
- `PUT /api/tasks/{id}`: Update task with all advanced features
- `GET /api/tasks`: Retrieve tasks with advanced filtering, sorting, search
- `POST /api/tasks/{id}/complete`: Complete task with recurrence handling
- `GET /api/tags`: Get user's tags with autocomplete support
- `POST /api/tags`: Create new tag
- `DELETE /api/tags/{id}`: Delete tag

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `KAFKA_BROKERS`: Comma-separated list of Kafka broker addresses
- `DAPR_SIDECAR_HOST`: Host address of Dapr sidecar (usually localhost)
- `DAPR_HTTP_PORT`: Port for Dapr HTTP API (default 3500)
- `RECURRENCE_ENGINE_TYPE`: Type of recurrence engine to use
- `REMINDER_CHECK_INTERVAL`: Interval for checking due tasks (seconds)

### Development Commands
- `uvicorn src.main:app --reload`: Run development server
- `pytest tests/`: Run all tests
- `mypy src/`: Type checking
- `black src/`: Code formatting
- `flake8 src/`: Linting

### MCP Integration
- Enhanced MCP tools with priority, tag, recurrence, due date support
- Event-emitting operations for all task modifications
- Dapr-enabled service communication patterns
- Event-driven architecture implementation