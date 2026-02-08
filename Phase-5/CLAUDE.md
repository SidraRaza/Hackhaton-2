# CLAUDE.md
## Phase V: Advanced Cloud Deployment

### Project Context
This project implements Phase V: Advanced Cloud Deployment of the Todo application, transforming it into a production-grade, event-driven, cloud-native AI system with advanced features (priorities, tags, search, recurring tasks, due dates) deployed on DigitalOcean Kubernetes with Kafka and Dapr integration.

### Technology Stack
- **Frontend**: Next.js 14+, React 19+, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLModel, Python 3.13+
- **Database**: Neon Serverless PostgreSQL
- **Events**: Kafka (Redpanda Cloud)
- **Runtime**: Dapr (Distributed Application Runtime)
- **Orchestration**: Kubernetes (DOKS)
- **AI Layer**: OpenAI Agents SDK, Official MCP SDK
- **Package Management**: Helm Charts
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana, Loki

### Key Directories
- `/backend`: FastAPI application with advanced features
- `/frontend`: Next.js frontend with enhanced UI
- `/k8s`: Kubernetes manifests for deployment
- `/helm`: Helm charts for packaging
- `/docker`: Docker configurations
- `/specs/001-advanced-cloud-deployment`: Feature specifications
- `/events`: Event schemas and consumers
- `/dapr`: Dapr component configurations

### Architecture Highlights
- Event-driven architecture with Kafka/Redpanda for task events
- Dapr integration for cloud-native building blocks (pub/sub, state, secrets)
- Recurring tasks with automatic next occurrence generation
- Priority system with visual indicators
- Tag management system with autocomplete
- Advanced search and filtering capabilities
- Due dates with reminder notifications
- Deployment to DigitalOcean Kubernetes with auto-scaling

### Development Workflow
1. All code generated from specifications using Claude Code
2. Event-first approach: state changes emit events before persistence
3. Dapr-enabled services with sidecar pattern
4. Kubernetes-native deployment with Helm
5. CI/CD pipeline with GitHub Actions
6. Comprehensive monitoring with Prometheus/Grafana

### Key Files
- `backend/src/models/task_model.py`: Extended task model with advanced features
- `backend/src/api/task_router.py`: API endpoints with priority, tags, search, recurrence
- `frontend/src/components/task/TaskForm.tsx`: Enhanced task creation with all new features
- `frontend/src/components/task/PrioritySelector.tsx`: Priority selection component
- `frontend/src/components/task/TagInput.tsx`: Tag management component
- `k8s/base/`: Base Kubernetes manifests
- `helm/todo-app/`: Production Helm chart
- `dapr/components/`: Dapr component configurations
- `events/consumers/`: Event consumer services
- `specs/001-advanced-cloud-deployment/`: Complete feature specification

### MCP Integration
- Enhanced MCP tools with priority, tag, recurrence, and due date support
- Event-driven task operations
- Dapr-enabled service communication
- Cloud-native deployment patterns

### Environment Variables
- `DATABASE_URL`: Neon PostgreSQL connection string
- `KAFKA_BROKERS`: Redpanda Cloud cluster brokers
- `DAPR_SIDECAR_HOST`: Dapr sidecar host for service invocation
- `TODO_APP_ENV`: Environment indicator (development/staging/production)