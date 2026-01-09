# Project Overview

> **Hackathon II Todo App** - Phase II Specification

## Project Information

| Field | Value |
|-------|-------|
| **Project Name** | Hackathon II Todo App |
| **Current Phase** | Phase II – Full-Stack Web Application |
| **Version** | 1.0.0 |
| **Last Updated** | 2026-01-08 |

## Objective

Transform the console-based Todo application into a multi-user web application with:
- Persistent storage using PostgreSQL
- RESTful API backend
- Responsive frontend UI
- JWT-based user authentication

## Technology Stack

| Layer | Technology | Version | Notes |
|-------|------------|---------|-------|
| **Frontend** | Next.js (App Router) | 16+ | TypeScript, Server Components |
| **Styling** | Tailwind CSS | 3.x | Utility-first, responsive |
| **Backend** | Python FastAPI | 0.100+ | RESTful API, async support |
| **ORM** | SQLModel | 0.0.14+ | Pydantic + SQLAlchemy |
| **Database** | Neon PostgreSQL | Serverless | Persistent storage |
| **Authentication** | Better Auth | Latest | JWT-based sessions |

## Core Features

### 1. Task Management
- Create, read, update, delete tasks
- Mark tasks as complete/incomplete
- Filter tasks by status (pending/completed)
- Sort tasks by title, created date, due date
- **Spec**: `@specs/features/task-crud.md`

### 2. User Authentication
- User signup with email/password
- User signin with JWT token issuance
- Protected API endpoints
- User-specific data isolation
- **Spec**: `@specs/features/authentication.md`

### 3. Responsive UI
- Mobile-first design
- Desktop-optimized layouts
- Reusable component library
- **Spec**: `@specs/ui/components.md`, `@specs/ui/pages.md`

## Related Specifications

| Spec Type | File Path | Description |
|-----------|-----------|-------------|
| Features | `@specs/features/task-crud.md` | Task CRUD operations |
| Features | `@specs/features/authentication.md` | Auth flow |
| API | `@specs/api/rest-endpoints.md` | REST endpoint definitions |
| Database | `@specs/database/schema.md` | Data models and schema |
| UI | `@specs/ui/components.md` | Reusable components |
| UI | `@specs/ui/pages.md` | Page definitions |

## Phase II Acceptance Criteria

### Functional Requirements
- [ ] User can sign up with email and password
- [ ] User can sign in and receive JWT token
- [ ] User can create a new task with title and optional description
- [ ] User can view all their tasks
- [ ] User can update task title, description, and status
- [ ] User can delete a task
- [ ] User can mark task as complete/incomplete
- [ ] User can filter tasks by completion status
- [ ] User can sort tasks by different fields

### Non-Functional Requirements
- [ ] All API endpoints require JWT authentication
- [ ] Users can only access their own tasks
- [ ] Frontend is responsive on mobile (320px) to desktop (1920px)
- [ ] API response time < 500ms for all endpoints
- [ ] Data persists across server restarts (PostgreSQL)

### Security Requirements
- [ ] JWT tokens required for all task endpoints
- [ ] Invalid/expired tokens return 401 Unauthorized
- [ ] Passwords hashed before storage
- [ ] No sensitive data in JWT payload
- [ ] HTTPS enforced in production

## Development Workflow

```
1. Read relevant spec (@specs/...)
2. Implement feature following spec
3. Test against acceptance criteria
4. Update spec if behavior changes
5. Commit with reference to spec
```

## Commands

```bash
# Frontend development
cd frontend && npm run dev

# Backend development
cd backend && uvicorn main:app --reload --port 8000

# Full stack
docker-compose up
```
