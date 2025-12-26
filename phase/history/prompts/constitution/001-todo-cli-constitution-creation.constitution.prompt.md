---
id: 001
title: Todo CLI Constitution Creation
stage: constitution
date: 2025-12-26
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: ahed8
command: /sp.constitution
labels: ["constitution", "governance", "setup", "principles"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (governance document, no tests)
---

## Prompt

/sp.constitution
You are working on my personal project as part of the agentic development system.

Project Constitution — Todo CLI Application

Project Identity:
- Name: Todo CLI Application
- Type: Console-based, In-Memory
- Language: Python 3.13+
- Environment: UV
- AI Tooling: Claude Code
- Specification Authority: Spec-Kit Plus (installed and authoritative)

Source of Truth:
- Spec-Kit Plus specification is the SINGLE source of truth.
- No agent or human may redefine requirements or infer missing behavior.
- Conflicts resolution: Spec-Kit Plus > Project Constitution > Agent Instructions.

Core Functional Scope:
- Mandatory features:
  1. Add Todo
  2. Delete Todo
  3. Update Todo
  4. View Todos
  5. Mark Todo as Complete
- No feature may be added without Spec-Kit Plus approval and Project Manager Agent consent.

Development Philosophy:
- Spec-Driven Development
- Agentic Dev Stack
- Clean Code Principles
- Incremental & Verifiable Progress
- Workflow Order (MANDATORY):
  1. Specification (Spec-Kit Plus)
  2. Planning
  3. Task Breakdown
  4. Implementation
  5. Review
- Skipping or reordering steps is forbidden.

Agent Authority & Responsibilities:
- Project Manager Agent (`todo-task-manager`) controls all sub-agents and prevents premature coding.
- Sub-Agents:
  - Planning Agent (`todo-plan-manager`)
  - Task Breakdown Agent (`todo-task-breaker`)
  - Implementation Agent (`todo-code-implementer`)
  - Review Agent (`todo-quality-reviewer`)
- Agents must strictly follow their roles.

Coding Rules:
- No code before approved specification and assigned task.
- Code must be Python 3.13+ compatible, console-based, and in-memory.
- Each task produces minimal, focused code with no hidden behavior.
- Premature optimization is forbidden.

Scope Boundaries (OUT OF SCOPE unless specified):
- Databases
- File persistence
- GUI / Web UI
- Authentication
- Networking
- Background processes

Skills & Reusability:
- Skills are stored in `.claude/skills`
- Skills must be generic, reusable, and non-project-specific.
- Skills do NOT encode business logic.

Quality & Review Standards:
- Implemented code must match Spec-Kit Plus requirements, assigned tasks, and clean code practices.
- Review is mandatory before acceptance.

Change Management:
- Any change requires:
  1. Updated Spec-Kit Plus specification
  2. Re-planning
  3. New task breakdown
  4. Controlled implementation
- Ad-hoc changes are forbidden.

Final Principle:
- Nothing is built because it "seems obvious."
- Everything is built because it is specified.

## Response snapshot

Created Todo CLI Application Constitution v1.0.0 with:

**8 Core Principles:**
1. Spec-Driven Development (NON-NEGOTIABLE)
2. Mandatory Workflow Order (NON-NEGOTIABLE)
3. Clean Code Principles
4. Incremental & Verifiable Progress
5. Agent Authority & Hierarchy
6. Skills Reusability
7. Quality & Review Standards
8. Change Management

**Additional Sections:**
- Scope Boundaries (In Scope: 5 features, Out of Scope: 8 exclusions)
- Agent Hierarchy (visual diagram)
- Governance (amendment, versioning, compliance, precedence)

**Templates Verified Compatible:**
- plan-template.md ✅
- spec-template.md ✅
- tasks-template.md ✅

## Outcome

- ✅ Impact: Constitution established as governance foundation for Todo CLI project
- 🧪 Tests: N/A - governance document
- 📁 Files: 1 file created (.specify/memory/constitution.md)
- 🔁 Next prompts: Run /sp.specify to create first feature specification
- 🧠 Reflection: Constitution captures all user requirements and establishes clear authority hierarchy

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - all placeholders filled, no TODOs remaining
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
