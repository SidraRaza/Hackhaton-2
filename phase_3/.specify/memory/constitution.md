<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.0.1 (PATCH - validated templates alignment)

Modified principles: None

Added sections: None

Removed sections: None

Templates requiring updates:
- ✅ validated: .specify/templates/plan-template.md (Constitution Check section present)
- ✅ validated: .specify/templates/spec-template.md (user stories + requirements aligned)
- ✅ validated: .specify/templates/tasks-template.md (phase organization aligned)

Follow-up TODOs: None

Previous Version History:
- 1.0.0 (2026-01-08): Initial constitution creation with 5 core principles
-->

# Hackathon II Todo App Constitution

## Core Principles

### I. Spec-Driven Development

All features MUST be implemented based on structured specifications located in `/specs`.

- Specifications are the single source of truth for feature requirements
- Code generation and implementation follow the Agentic Dev Stack workflow:
  Write Spec → Generate Plan → Break into Tasks → Implement via Claude Code
- Changes to behavior MUST first be reflected in specs before code modifications
- No feature implementation without a corresponding specification

### II. User Privacy & Security

Each user MUST only access their own data; JWT-based authentication enforces isolation.

- All API endpoints MUST require valid JWT in `Authorization: Bearer <token>` header
- Invalid or missing JWT MUST return 401 Unauthorized
- Database queries MUST filter by authenticated user's ID
- Secrets (BETTER_AUTH_SECRET) MUST be stored in environment variables, never committed
- Production deployments MUST use HTTPS

### III. Code Quality & Maintainability

All code MUST follow modular design patterns and maintain readability.

- Backend: FastAPI with Pydantic models, SQLModel ORM patterns
- Frontend: Next.js App Router with TypeScript, Tailwind CSS
- Server components by default; Client components only for interactivity
- Clear separation of concerns across layers
- Consistent naming conventions and file organization

### IV. Responsiveness

Frontend MUST work seamlessly on mobile and desktop devices.

- All UI components MUST be responsive using Tailwind CSS breakpoints
- Mobile-first design approach
- Touch-friendly interactions on mobile
- Consistent user experience across screen sizes

### V. Cross-Layer Integration

Changes to features, API, or database MUST reflect across all layers.

- Frontend, backend, and specs MUST remain synchronized
- API contract changes require updates to:
  - Backend endpoint implementation
  - Frontend API client
  - Relevant spec documentation
- Database schema changes require migration scripts and model updates

## Technology Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Frontend | Next.js 16+ (App Router), TypeScript, Tailwind CSS | Server components default |
| Backend | Python FastAPI | RESTful API, Pydantic models |
| ORM | SQLModel | Database models and queries |
| Database | Neon Serverless PostgreSQL | Persistent storage |
| Authentication | Better Auth | JWT-based sessions |
| Spec-Driven | Claude Code + Spec-Kit Plus | Automated implementation |

## Development Workflow

### Spec First Rule
Always read/update relevant spec before implementing any feature.

### Testing Protocol
- Frontend: `cd frontend && npm run dev`
- Backend: `cd backend && uvicorn main:app --reload --port 8000`
- Full stack: `docker-compose up`
- Verify JWT-secured API calls using frontend or Postman

### Iteration Cycle
1. Update specs if behavior changes
2. Regenerate code via Claude Code
3. Test across all layers
4. Verify spec compliance

## Governance

This constitution supersedes all other development practices for this project.

### Amendment Procedure
1. Propose change with rationale
2. Document impact on existing code/specs
3. Update constitution with version bump
4. Propagate changes to dependent templates

### Versioning Policy
- MAJOR: Principle removals or incompatible redefinitions
- MINOR: New principles or expanded guidance
- PATCH: Clarifications and typo fixes

### Compliance
- All code reviews MUST verify constitution compliance
- Deviations require explicit justification and documentation
- See `/specs` and `CLAUDE.md` files for detailed guidance

**Version**: 1.0.1 | **Ratified**: 2026-01-08 | **Last Amended**: 2026-01-09
