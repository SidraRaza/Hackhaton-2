# Research: Todo CRUD Functionality Issues

## Decision: API Endpoint Mismatch Resolution
**Rationale**: The primary issue is that frontend components are calling `/api/tasks/*` endpoints while backend implements `/api/todos/*` endpoints. We need to standardize on one convention.

**Chosen Approach**: Standardize on `/api/todos` endpoints as this appears to be the backend's intended convention.

**Alternatives Considered**:
- Keep `/api/tasks` - would require changing backend endpoints
- Use `/api/todos` - aligns with existing backend implementation in `backend/app/api/tasks.py`
- Hybrid approach - would create further confusion

## Decision: Frontend API Library Consolidation
**Rationale**: Multiple conflicting API implementations exist (`api.js` with fetch, `api.ts` with axios, `tasks.tsx` with hardcoded endpoints).

**Chosen Approach**: Consolidate to a single API library using TypeScript with proper typing.

**Alternatives Considered**:
- Keep multiple implementations - leads to maintenance issues
- Use only fetch API - simpler but less type-safe
- Use only axios - more features but adds dependency
- TypeScript with fetch - balances type safety with minimal dependencies

## Decision: Type Consistency Resolution
**Rationale**: Field naming inconsistencies between frontend and backend (`createdAt` vs `created_at`).

**Chosen Approach**: Standardize on camelCase (`createdAt`) to align with JavaScript/TypeScript conventions.

**Alternatives Considered**:
- Snake_case (`created_at`) - aligns with Python/PostgreSQL but not JS ecosystem
- camelCase (`createdAt`) - aligns with JavaScript/TypeScript conventions
- Leave as is - would perpetuate inconsistency

## Decision: Component Architecture
**Rationale**: Existing component structure is sound but needs proper API integration.

**Chosen Approach**: Maintain existing component structure and fix API connections.

**Alternatives Considered**:
- Rewrite components from scratch - unnecessary overhead
- Keep as-is - wouldn't fix underlying issues
- Refactor with new architecture - adds complexity unnecessarily