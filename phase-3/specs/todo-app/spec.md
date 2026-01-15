# Hackathon Todo App Phase II - Specification

## Project Overview
- **Project Name**: hackathon-todo
- **Version**: 1.0
- **Description**: Transform a console Todo app into a full-stack multi-user web application with JWT authentication, responsive frontend, REST API, and Neon Serverless PostgreSQL storage.

## Core Principles
- **Always reference specs**: All implementation must reference specs
- **Never modify without spec**: No code change without updating specs
- **Maintain layer separation**: Frontend and backend layers are separate
- **Ensure security**: JWT auth, user isolation, token expiry enforced
- **Ensure responsiveness**: Frontend must work on mobile and desktop
- **Reuse skills**: Agents must reuse skills for repetitive tasks
- **Maintain code quality**: Follow coding standards, linting, type safety

## System Architecture

### Frontend Layer
- **Path**: `./frontend`
- **Technology Stack**: Next.js 16+, TypeScript, Tailwind CSS
- **Responsibilities**:
  - Implement pages and layouts
  - Build reusable UI components
  - Consume backend REST API
  - Attach JWT token to all API requests
  - Handle user authentication sessions
- **Guidelines**: @claude/frontend.md

### Backend Layer
- **Path**: `./backend`
- **Technology Stack**: Python FastAPI server using SQLModel ORM and Neon PostgreSQL
- **Responsibilities**:
  - Implement REST API endpoints
  - Verify JWT tokens and enforce user access
  - Manage database models and migrations
  - Handle CRUD operations for tasks
  - Validate input using Pydantic models
  - Return structured JSON responses
  - Error handling with proper HTTP status codes
- **Guidelines**: @claude/backend.md

### Database Layer
- **Path**: `./backend/models`
- **Technology Stack**: Neon Serverless PostgreSQL
- **Responsibilities**:
  - Define tables and indexes
  - Ensure data integrity and relations
  - Optimize for queries by status and user
  - Provide connection using environment variables
  - Maintain schema migrations

## Authentication System

### Authentication Method
- **Method**: JWT via Better Auth
- **Token Expiry**: 7 days
- **Stateless**: True
- **Environment Variable**: `BETTER_AUTH_SECRET`

### Authentication Flow
1. User logs in on frontend using Better Auth
2. Frontend receives JWT token
3. Frontend attaches JWT token to Authorization header
4. Backend verifies JWT token signature using shared secret
5. Backend decodes token to identify user and filter tasks

### Security Requirements
- User isolation enforced through user_id filtering in all queries
- All API requests must include proper JWT authentication headers
- Token expiry enforced after 7 days
- Users can only see and modify their own tasks

## API Specification

### REST API Endpoints

#### Task Endpoints
- `GET /api/tasks` - Retrieve all tasks for authenticated user
- `POST /api/tasks` - Create a new task for authenticated user
- `PUT /api/tasks/{task_id}` - Update a task for authenticated user
- `DELETE /api/tasks/{task_id}` - Delete a task for authenticated user
- `PATCH /api/tasks/{task_id}/complete` - Toggle task completion status

#### Authentication Endpoints
- `POST /api/auth/login` - User login with JWT token return
- `POST /api/auth/logout` - User logout
- `POST /api/auth/register` - User registration

### Request/Response Formats

#### Task Object
```json
{
  "id": 1,
  "title": "Sample task",
  "description": "Task description",
  "completed": false,
  "user_id": 1,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### Authentication Response
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "expires_in": 604800
}
```

## Component Specifications

### Frontend Components
- **TaskList**: Displays all tasks for authenticated user
- **TaskItem**: Individual task component with completion toggle
- **TaskForm**: Form for creating/updating tasks
- **AuthComponent**: Login/registration UI with Better Auth integration
- **Header**: Navigation and user session controls
- **Layout**: Responsive layout supporting mobile and desktop

### Backend Components
- **User Model**: User entity with authentication fields
- **Task Model**: Task entity with user relationship
- **Auth Service**: JWT token generation and verification
- **Task Service**: Business logic for task operations
- **Database Service**: CRUD operations with user isolation

## Agent Specifications

### Task Manager Agent
- **Role**: Developer Agent
- **Description**: Handles CRUD operations for tasks, including creation, update, deletion, and completion. Ensures tasks belong only to authenticated user.
- **Tools**: claude-code, spec-kit-plus, fastapi, nextjs, sqlmodel, postgresql
- **Tasks**:
  - implement_task_crud_backend
  - implement_task_crud_frontend
  - write_unit_tests_for_tasks
  - verify_user_task_isolation

### Authentication Agent
- **Role**: Security & Auth Agent
- **Description**: Handles Better Auth integration, JWT issuance, verification, and frontend auth flows. Ensures secure login/signup and token-based authentication for all API requests.
- **Tools**: claude-code, better-auth, jwt, fastapi, nextjs
- **Tasks**:
  - implement_signup_login
  - configure_jwt_plugin
  - attach_jwt_to_frontend_requests
  - verify_backend_auth_middleware

### API Agent
- **Role**: API Development Agent
- **Description**: Creates and maintains all REST API endpoints according to the specification. Ensures endpoints follow HTTP conventions and handle proper request validation.
- **Tools**: claude-code, fastapi, sqlmodel
- **Tasks**:
  - implement_get_tasks_endpoint
  - implement_post_tasks_endpoint
  - implement_put_tasks_endpoint
  - implement_delete_tasks_endpoint
  - implement_patch_complete_endpoint
  - write_api_tests

### Frontend Agent
- **Role**: Frontend Development Agent
- **Description**: Develops responsive pages and components for the Next.js frontend. Ensures integration with backend API and Better Auth sessions.
- **Tools**: claude-code, nextjs, typescript, tailwind-css
- **Tasks**:
  - build_task_pages
  - build_layouts_and_navigation
  - integrate_api_client
  - attach_jwt_to_requests
  - handle_error_and_loading_states

### Backend Agent
- **Role**: Backend Development Agent
- **Description**: Develops FastAPI backend logic, including task handling, authentication verification, and database interaction. Responsible for ensuring data integrity and business logic correctness.
- **Tools**: claude-code, fastapi, sqlmodel, postgresql
- **Tasks**:
  - implement_database_models
  - configure_database_connection
  - implement_api_routes
  - enforce_jwt_auth
  - handle_exceptions_and_responses

## Reusable Skills Specification

### create_api_endpoint
- **Description**: Automates creation of FastAPI endpoint based on REST API spec
- **Steps**:
  1. read_spec_for_endpoint
  2. generate_pydantic_models
  3. create_fastapi_route
  4. add_jwt_verification
  5. return_endpoint_code

### create_frontend_component
- **Description**: Automates creation of reusable React components using Tailwind CSS
- **Steps**:
  1. read_ui_spec
  2. generate_component_structure
  3. add_props_and_state
  4. integrate_api_calls_if_needed
  5. return_component_code

### create_sqlmodel_model
- **Description**: Creates SQLModel ORM models based on database spec
- **Steps**:
  1. read_database_spec
  2. generate_model_fields
  3. define_relationships
  4. return_model_code

### verify_jwt_auth
- **Description**: Verifies JWT token in FastAPI requests and returns user identity
- **Steps**:
  1. extract_token_from_header
  2. decode_and_verify_signature
  3. validate_token_expiry
  4. return_user_info

### write_unit_test
- **Description**: Creates automated unit tests for backend or frontend functionality
- **Steps**:
  1. read_spec_for_test_case
  2. generate_test_code
  3. add_assertions
  4. return_test_file

## Development Workflow

### Workflow Steps
1. **read_spec**: true
2. **break_into_tasks**: true
3. **assign_to_agents**: true
4. **implement_backend**: true
5. **implement_frontend**: true
6. **write_unit_tests**: true
7. **test_full_feature**: true
8. **deploy**: true

### Quality Assurance Requirements
- All endpoints must follow REST conventions
- Input validation using Pydantic models
- Proper HTTP status codes for all responses
- Comprehensive error handling and logging
- User isolation verified for all data operations
- Type safety enforced with TypeScript and Python typing
- Code linting and formatting standards applied

## Database Schema Specification

### Users Table
- id (Integer, Primary Key, Auto Increment)
- email (String, Unique, Not Null)
- password_hash (String, Not Null)
- created_at (DateTime, Not Null)
- updated_at (DateTime, Not Null)

### Tasks Table
- id (Integer, Primary Key, Auto Increment)
- title (String, Not Null)
- description (Text, Optional)
- completed (Boolean, Default: False)
- user_id (Integer, Foreign Key to Users, Not Null)
- created_at (DateTime, Not Null)
- updated_at (DateTime, Not Null)

### Indexes
- Index on user_id for efficient user-based queries
- Index on completed status for filtering
- Index on created_at for chronological ordering

## Environment Configuration

### Required Environment Variables
- `DATABASE_URL`: Connection string for Neon PostgreSQL
- `BETTER_AUTH_SECRET`: Secret key for JWT signing
- `NEXT_PUBLIC_API_URL`: Frontend API base URL
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins

### Development Environment
- Node.js 18+ for frontend
- Python 3.9+ for backend
- PostgreSQL compatible database (Neon Serverless)
- Next.js 16+ development server
- FastAPI development server

## Security Requirements

### Authentication & Authorization
- All API endpoints require JWT authentication except public routes
- User data isolation through user_id filtering
- JWT token validation on every request
- Token expiration enforcement after 7 days
- Secure password hashing for user accounts

### Input Validation
- All API inputs validated using Pydantic models
- Frontend and backend validation for data integrity
- Sanitization of user-generated content
- Prevention of SQL injection and XSS attacks

### Data Protection
- Encryption at rest for sensitive data
- HTTPS required for all API communications
- Proper error handling to prevent information disclosure
- Rate limiting to prevent abuse

## Performance Requirements

### Frontend Performance
- Page load time under 3 seconds
- Mobile-responsive design
- Lazy loading for large task lists
- Optimized asset delivery

### Backend Performance
- API response time under 500ms for standard operations
- Efficient database queries with proper indexing
- Connection pooling for database operations
- Caching for frequently accessed data

## Testing Requirements

### Unit Tests
- 80% code coverage for backend API
- 80% code coverage for frontend components
- Authentication flow tests
- User isolation tests

### Integration Tests
- End-to-end API functionality tests
- Database interaction tests
- Authentication and authorization tests
- Frontend-backend integration tests

### Acceptance Tests
- Complete user journey tests
- Multi-user isolation verification
- Performance benchmarks
- Security vulnerability assessments

## Deployment Requirements

### Infrastructure
- Neon Serverless PostgreSQL database
- Separate deployments for frontend and backend
- SSL certificates for secure connections
- Monitoring and logging setup

### CI/CD Pipeline
- Automated testing on all commits
- Staging environment for pre-production validation
- Rollback capabilities for failed deployments
- Environment-specific configuration management

## Permissions

### Claude Agents
- read_specs: true
- write_code: true
- update_docs: true
- run_tests: true

### Humans
- approve_deployments: true
- update_specs: true

### Security
- jwt_secret: BETTER_AUTH_SECRET
- enforce_user_isolation: true

## Constraints

### Technical Constraints
- All code must strictly follow the specifications in /sp.specs
- Agents must use skills to avoid repetitive implementations
- Frontend requests must attach JWT token to Authorization header
- Backend validates JWT on every request
- User can only see and modify their own tasks
- Token expiry enforced after 7 days

### Architecture Constraints
- Strict separation between frontend and backend
- No direct database access from frontend
- All data flows through API endpoints
- Consistent error handling across all layers
- Standardized logging format across all services

## Acceptance Criteria

### Functional Requirements
- [ ] Users can register and authenticate securely
- [ ] Users can create, read, update, and delete their own tasks
- [ ] Task completion status can be toggled
- [ ] Users cannot access other users' tasks
- [ ] Responsive UI works on mobile and desktop devices
- [ ] Authentication tokens expire after 7 days

### Non-functional Requirements
- [ ] Application passes all security tests
- [ ] API responds within performance requirements
- [ ] Frontend passes accessibility standards
- [ ] All tests pass with required coverage
- [ ] Application deploys successfully to target environment
- [ ] Error handling provides meaningful feedback to users

## Success Metrics

### User Experience
- Task creation and management feels responsive
- Authentication flow is seamless
- Mobile and desktop experiences are consistent

### Technical Quality
- Code follows established patterns and standards
- All tests pass consistently
- Performance meets defined benchmarks
- Security vulnerabilities are addressed