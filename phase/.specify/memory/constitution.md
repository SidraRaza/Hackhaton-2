<!--
  ============================================================================
  SYNC IMPACT REPORT
  ============================================================================
  Version change: 0.0.0 → 1.0.0 (MAJOR - Initial constitution adoption)

  Modified Principles: N/A (initial creation)

  Added Sections:
  - Core Principles (8 principles)
  - Scope Boundaries
  - Agent Hierarchy
  - Governance

  Removed Sections: N/A (initial creation)

  Templates requiring updates:
  - .specify/templates/plan-template.md ✅ Compatible (Constitution Check section exists)
  - .specify/templates/spec-template.md ✅ Compatible (mandatory sections align)
  - .specify/templates/tasks-template.md ✅ Compatible (phase structure aligns)

  Follow-up TODOs: None
  ============================================================================
-->

# Todo CLI Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

Spec-Kit Plus specification is the SINGLE source of truth for all requirements and behavior.

- No agent or human may redefine requirements or infer missing behavior
- All features MUST be specified before any implementation begins
- Conflicts resolution hierarchy: Spec-Kit Plus > Project Constitution > Agent Instructions
- Nothing is built because it "seems obvious" — everything is built because it is specified

### II. Mandatory Workflow Order (NON-NEGOTIABLE)

All development MUST follow this exact sequence without exception:

1. **Specification** (Spec-Kit Plus)
2. **Planning** (Architecture and design decisions)
3. **Task Breakdown** (Granular, testable tasks)
4. **Implementation** (Code execution)
5. **Review** (Quality verification)

- Skipping or reordering steps is forbidden
- Each phase requires approval before proceeding to the next
- No code may be written before approved specification and assigned task

### III. Clean Code Principles

All code MUST adhere to clean code standards:

- Python 3.13+ compatible syntax and idioms
- Console-based I/O (stdin/stdout/stderr)
- In-memory data handling only
- Each task produces minimal, focused code with no hidden behavior
- Type hints for all function signatures
- PEP 8 compliance
- Single responsibility per function/module

### IV. Incremental & Verifiable Progress

Development proceeds in small, verifiable increments:

- Each task MUST be independently testable
- Premature optimization is forbidden
- YAGNI (You Aren't Gonna Need It) principle applies
- Changes are committed after each logical unit of work
- Progress is tracked through explicit task completion

### V. Agent Authority & Hierarchy

The agentic development stack operates under strict role separation:

- **Project Manager Agent** (`todo-task-manager`): Controls all sub-agents, prevents premature coding, enforces workflow
- **Planning Agent** (`todo-plan-manager`): Converts specifications to implementation plans
- **Task Breakdown Agent** (`todo-task-breaker`): Creates granular, executable tasks from plans
- **Implementation Agent** (`todo-code-implementer`): Writes code for assigned tasks only
- **Review Agent** (`todo-quality-reviewer`): Verifies implementation quality and spec compliance

Agents MUST strictly follow their designated roles and not exceed their authority.

### VI. Skills Reusability

Skills stored in `.claude/skills` provide reusable patterns:

- Skills MUST be generic and non-project-specific
- Skills do NOT encode business logic
- Skills describe capabilities, responsibilities, and usage patterns
- Implementation agents reference skills during code execution

### VII. Quality & Review Standards

All implemented code MUST meet quality gates:

- Code matches Spec-Kit Plus requirements exactly
- Code fulfills assigned task requirements
- Code follows clean code practices from constitution
- Review is mandatory before feature acceptance
- No feature is complete until review passes

### VIII. Change Management

Any change to requirements or implementation requires:

1. Updated Spec-Kit Plus specification
2. Re-planning if architecture affected
3. New task breakdown reflecting changes
4. Controlled implementation following workflow

- Ad-hoc changes are forbidden
- All changes are traceable through PHRs (Prompt History Records)

## Scope Boundaries

### In Scope (Mandatory Features)

1. Add Todo
2. Delete Todo
3. Update Todo
4. View Todos
5. Mark Todo as Complete

No feature may be added without Spec-Kit Plus approval and Project Manager Agent consent.

### Out of Scope (Explicitly Excluded)

The following are NOT permitted unless explicitly specified:

- Databases or external data stores
- File persistence or disk I/O
- GUI or Web UI
- Authentication or authorization
- Networking or API calls
- Background processes or async operations
- Multi-user support
- Data encryption

## Agent Hierarchy

```
┌─────────────────────────────────────┐
│   Project Manager (todo-task-manager)   │
│   - Orchestrates all sub-agents         │
│   - Enforces workflow compliance        │
│   - Prevents premature implementation   │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌───────┐   ┌─────────┐   ┌─────────┐
│ Plan  │──▶│  Tasks  │──▶│  Code   │
│Manager│   │ Breaker │   │Implement│
└───────┘   └─────────┘   └────┬────┘
                               │
                               ▼
                         ┌─────────┐
                         │ Quality │
                         │ Reviewer│
                         └─────────┘
```

## Governance

### Amendment Procedure

1. Proposed changes MUST be documented with rationale
2. Changes require review against existing principles
3. Breaking changes require MAJOR version increment
4. All amendments MUST update the "Last Amended" date

### Versioning Policy

Constitution follows semantic versioning:

- **MAJOR**: Backward-incompatible governance/principle changes
- **MINOR**: New principles or materially expanded guidance
- **PATCH**: Clarifications, wording fixes, non-semantic refinements

### Compliance Review

- All implementation work MUST verify constitution compliance
- Constitution Check in plan.md validates alignment
- Violations MUST be justified in Complexity Tracking section
- Project Manager Agent enforces compliance across all agents

### Precedence

This constitution supersedes all other practices. When conflicts arise:

1. Spec-Kit Plus specification (highest authority)
2. Project Constitution (this document)
3. Agent-specific instructions
4. General development practices (lowest authority)

**Version**: 1.0.0 | **Ratified**: 2025-12-26 | **Last Amended**: 2025-12-26
