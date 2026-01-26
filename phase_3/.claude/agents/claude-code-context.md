# Claude Code Agent Context - Hackathon II Todo App

## Project Overview
The Hackathon II Todo App is a full-stack web application that transforms a console-based todo application into a multi-user web application with authentication, persistent storage, and responsive UI. The application has been enhanced with AI-powered conversational task management capabilities.

## Tech Stack
- **Frontend**: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- **Backend**: Python FastAPI with Pydantic models
- **Database**: Neon PostgreSQL (serverless) with SQLModel ORM
- **Authentication**: Better Auth with JWT-based sessions
- **AI Integration**: OpenAI Assistants API for conversational interface
- **MCP**: Model Context Protocol server for task management tools
- **Frontend Chat**: OpenAI Assistant UI components (@openai/assistant-ui-react)
- **Architecture**: Spec-driven development following Agentic Dev Stack workflow

## Key Features
- User authentication (signup, signin with JWT tokens)
- Task CRUD operations (Create, Read, Update, Delete)
- User data isolation (each user sees only their tasks)
- Task filtering and sorting capabilities
- Responsive UI design for mobile and desktop
- Secure API with JWT token validation
- AI-powered conversational task management via chat interface
- MCP server exposing task management tools (create_task, update_task, delete_task, get_tasks, complete_task)
- Persistent conversation history with message threading
- Natural language processing for task operations

## Architecture Patterns
- Server components by default in Next.js
- Client components only for interactivity
- JWT-based authentication with middleware
- SQLModel for database models and queries
- Component-based UI architecture with Tailwind CSS
- Stateful AI conversations managed through database-persisted context
- MCP server pattern for exposing tools to AI agents
- Stateless chat API that loads context from database on each request

## Specifications Location
- Feature specs: `specs/features/`
- API specs: `specs/api/`
- Database specs: `specs/database/`
- UI specs: `specs/ui/`
- AI/MCP specs: `specs/2-ai-conversational-task/`
- Implementation plan: `specs/2-ai-conversational-task/plan.md`
- Tasks: `specs/2-ai-conversational-task/tasks.md`

## Development Workflow
1. Read relevant spec (`@specs/...`)
2. Implement feature following spec
3. Test against acceptance criteria
4. Update spec if behavior changes
5. Commit with reference to spec

## Commands
- Frontend: `cd frontend && npm run dev`
- Backend: `cd backend && uvicorn main:app --reload --port 8000`
- Full stack: `docker-compose up`

## AI/MCP Development Notes
- MCP tools must validate user identity from request context
- AI operations must be stateless (fetch conversation context from DB on every request)
- MCP tools read/write directly from DB using SQLModel
- All AI interactions must be user-scoped and secure
- Conversation and Message models store chat history
- OpenAI Assistant API manages conversation threads and tool calling