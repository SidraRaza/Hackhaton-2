# Claude Code Agent Context - Hackathon II Todo App

## Project Overview
The Hackathon II Todo App is a full-stack web application that transforms a console-based todo application into a multi-user web application with authentication, persistent storage, and responsive UI.

## Tech Stack
- **Frontend**: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- **Backend**: Python FastAPI with Pydantic models
- **Database**: Neon PostgreSQL (serverless) with SQLModel ORM
- **Authentication**: Better Auth with JWT-based sessions
- **Architecture**: Spec-driven development following Agentic Dev Stack workflow

## Key Features
- User authentication (signup, signin with JWT tokens)
- Task CRUD operations (Create, Read, Update, Delete)
- User data isolation (each user sees only their tasks)
- Task filtering and sorting capabilities
- Responsive UI design for mobile and desktop
- Secure API with JWT token validation

## Architecture Patterns
- Server components by default in Next.js
- Client components only for interactivity
- JWT-based authentication with middleware
- SQLModel for database models and queries
- Component-based UI architecture with Tailwind CSS

## Specifications Location
- Feature specs: `specs/features/`
- API specs: `specs/api/`
- Database specs: `specs/database/`
- UI specs: `specs/ui/`
- Implementation plan: `specs/plan.md`
- Tasks: `specs/tasks.md`

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