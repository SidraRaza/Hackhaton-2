# Implementation Plan: Fix Todo CRUD Functionality

## Technical Context

### Current State
Based on our research, the existing Todo application has broken CRUD functionality due to API endpoint mismatches. The frontend is calling `/api/tasks/*` endpoints while the backend implements `/api/todos/*` endpoints, causing all operations to fail with 404 errors.

### Architecture Overview
- Frontend: Next.js 16+ with TypeScript and Tailwind CSS
- Backend: Python FastAPI with Pydantic models
- Database: Neon Serverless PostgreSQL
- ORM: SQLModel
- Authentication: Better Auth with JWT

### Known Unknowns (RESOLVED)
- Specific error messages or stack traces for the broken functionality (RESOLVED: 404 errors due to endpoint mismatch)
- Current API endpoint implementations for todo operations (RESOLVED: Backend has `/api/todos/*`, frontend calls `/api/tasks/*`)
- Frontend state management approach currently in use (RESOLVED: Multiple inconsistent API implementations exist)
- Database schema for todos table (RESOLVED: Exists as Task model in backend)

### Technology Choices
- Backend: FastAPI with SQLModel ORM
- Frontend: Next.js App Router with TypeScript
- Database: PostgreSQL with proper indexing for performance
- Authentication: JWT-based using Better Auth

## Constitution Check

### I. Spec-Driven Development Compliance
✅ Plan follows structured specification in `/specs/1-fix-todo-crud/spec.md`
✅ Implementation will follow Agentic Dev Stack workflow
✅ All changes will be reflected in specs first

### II. User Privacy & Security Compliance
✅ All API endpoints will require valid JWT in `Authorization: Bearer <token>` header
✅ Invalid or missing JWT will return 401 Unauthorized
✅ Database queries will filter by authenticated user's ID
✅ Secrets will be stored in environment variables

### III. Code Quality & Maintainability Compliance
✅ Backend will use FastAPI with Pydantic models, SQLModel ORM patterns
✅ Frontend will use Next.js App Router with TypeScript, Tailwind CSS
✅ Clear separation of concerns across layers
✅ Consistent naming conventions and file organization
✅ Multiple conflicting API implementations will be consolidated

### IV. Responsiveness Compliance
✅ UI components will be responsive using Tailwind CSS breakpoints
✅ Mobile-first design approach maintained
✅ Touch-friendly interactions preserved

### V. Cross-Layer Integration Compliance
✅ Changes will reflect across frontend, backend, and specs
✅ API contract changes will update all relevant components
✅ Database schema will remain consistent
✅ Frontend-backend API endpoint alignment will be established

## Gates

### Gate 1: Specification Clarity
✅ Specification clearly defines the problem and requirements
✅ User scenarios are well-defined with acceptance criteria
✅ Success criteria are measurable and achievable

### Gate 2: Architecture Alignment
✅ Proposed solution aligns with existing technology stack
✅ No fundamental architectural changes required
✅ Backward compatibility maintained

### Gate 3: Security Compliance
✅ All CRUD operations will maintain user data isolation
✅ Proper authentication enforced on all endpoints
✅ No security vulnerabilities introduced

## Phase 0: Research & Discovery

### Research Tasks

#### 0.1: Investigate Current Todo Implementation
**Task**: Examine existing todo functionality to identify specific issues
- Locate current todo API endpoints
- Review frontend components handling todo operations
- Identify where the disconnect between UI and backend occurs

#### 0.2: Database Schema Analysis
**Task**: Understand current todo data model and relationships
- Examine todos table schema
- Verify foreign key relationships to users
- Check indexes and constraints

#### 0.3: Authentication Flow Verification
**Task**: Confirm JWT authentication is properly configured for todo endpoints
- Verify middleware implementation
- Check token validation logic
- Ensure user context is passed correctly

#### 0.4: State Management Review
**Task**: Identify how frontend manages todo state
- Determine if using useState, useReducer, or external state management
- Check how API responses update UI state
- Verify optimistic updates (if implemented)

## Phase 1: Design & Architecture

### 1.1: Data Model
Based on the specification, the Todo entity has these attributes:
- id (unique identifier, UUID or integer primary key)
- title/description (string, not null)
- completed status (boolean, default false)
- creation timestamp (datetime)
- update timestamp (datetime)
- user_id (foreign key to users table)

### 1.2: API Contract Design
Following RESTful patterns with JWT authentication:

#### POST /api/todos
- Creates a new todo for the authenticated user
- Request body: `{title: string, description?: string}`
- Response: `201 Created` with todo object
- Authentication: Required (JWT in Authorization header)
- Validation: Title must not be empty

#### GET /api/todos
- Retrieves all todos for the authenticated user
- Response: `200 OK` with array of todo objects
- Authentication: Required (JWT in Authorization header)

#### PUT /api/todos/{id}
- Updates an existing todo
- Request body: `{title?: string, description?: string, completed?: boolean}`
- Response: `200 OK` with updated todo object
- Authentication: Required (JWT in Authorization header)
- Authorization: User must own the todo

#### DELETE /api/todos/{id}
- Deletes a todo
- Response: `204 No Content`
- Authentication: Required (JWT in Authorization header)
- Authorization: User must own the todo

### 1.3: Frontend Component Design
- TodoForm: Handles adding and updating todos
- TodoList: Displays todos with edit/delete functionality
- TodoItem: Individual todo with status toggle and edit controls

## Phase 2: Implementation Approach

### 2.1: Backend Implementation Priority
1. Fix API endpoints to ensure proper CRUD operations
2. Verify database transaction handling
3. Ensure proper error responses
4. Test authentication middleware

### 2.2: Frontend Implementation Priority
1. Fix API call implementations in components
2. Ensure proper state updates after API operations
3. Add loading states and error handling
4. Implement optimistic updates if needed

### 2.3: Integration Testing
1. End-to-end testing of CRUD operations
2. Authentication and authorization validation
3. Error condition handling
4. Performance testing for multiple operations

## Risk Analysis

### High-Risk Areas
- Authentication flow disruption affecting all endpoints
- Database transaction failures causing data inconsistency
- Frontend state management conflicts

### Mitigation Strategies
- Implement proper error handling and rollback mechanisms
- Use transactions for complex operations
- Thorough testing before deployment
- Backup plan for reverting changes if needed

## Success Metrics

### Technical Metrics
- 100% success rate for all CRUD operations
- Sub-2-second response times for API calls
- Zero data inconsistencies between UI and backend

### Business Metrics
- User-reported functionality improvements
- Reduced error rates in production monitoring
- Positive user feedback on task management experience