# hackathon-todo Constitution
<!-- Full-Stack Todo App with Authentication -->

## Core Principles

### I. Always Reference Specs
<!-- All implementation must reference specs -->
Code changes must be based on documented specifications; No implementation without corresponding spec updates; All architectural decisions must be recorded in specs before implementation begins.

### II. Never Modify Without Spec
<!-- No code change without updating specs -->
Any code modification requires an accompanying spec update; Feature additions must have spec documentation first; Bug fixes should update relevant spec sections to prevent regression.

### III. Maintain Layer Separation
<!-- Frontend and backend layers are separate -->
Frontend and backend must remain independent with clean API boundaries; Cross-layer dependencies should be minimized; Each layer has distinct responsibilities and technology stacks.

### IV. Ensure Security
<!-- JWT auth, user isolation, token expiry enforced -->
Authentication implemented via JWT with Better Auth; User data isolation enforced at database level; Token expiry and security best practices must be followed.

### V. Ensure Responsiveness
<!-- Frontend must work on mobile and desktop -->
UI must be responsive across device sizes; Mobile-first design approach encouraged; Performance considerations for various network speeds.

### VI. Reuse Skills
<!-- Agents must reuse skills for repetitive tasks -->
Standardized skills should be leveraged for common operations; Avoid duplicating functionality across implementations; Skills should be maintained and improved for reusability.

### VII. Maintain Code Quality
<!-- Follow coding standards, linting, type safety -->
Type safety enforced with TypeScript and Python typing; Code linting and formatting standards applied; Proper error handling and validation implemented.

## Additional Constraints
<!-- Security, Performance, and Technology Requirements -->

Frontend: Next.js 16+, TypeScript, Tailwind CSS with responsive design;
Backend: Python FastAPI server using SQLModel ORM and Neon PostgreSQL;
Database: Neon Serverless PostgreSQL with user_id filtering for isolation;
Authentication: JWT via Better Auth with 7-day token expiry;
All API requests must include proper JWT authentication headers.

## Development Workflow
<!-- Implementation Process, Testing, and Deployment -->

Development Steps:
1. Read specification thoroughly before implementation
2. Break features into discrete, testable tasks
3. Assign tasks to appropriate specialized agents
4. Implement backend functionality first
5. Implement frontend components and UI
6. Write comprehensive unit and integration tests
7. Test full feature functionality end-to-end
8. Deploy to appropriate environment

Quality Assurance:
- All endpoints must follow REST conventions
- Input validation using Pydantic models
- Proper HTTP status codes for all responses
- Comprehensive error handling and logging
- User isolation verified for all data operations

## Governance
<!-- Constitution Authority and Amendment Process -->

This constitution governs all development activities for the hackathon-todo project;
All agents must follow the specified architecture and technology constraints;
Changes to constitution require explicit approval and documentation;
Agent responsibilities must align with defined roles and tools;
Skills must be reused consistently to maintain code quality and reduce duplication.

**Version**: 1.0 | **Ratified**: 2026-01-15 | **Last Amended**: 2026-01-15
