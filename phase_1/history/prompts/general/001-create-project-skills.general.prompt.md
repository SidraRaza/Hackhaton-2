---
id: 001
title: Create Project Skills
stage: general
date: 2025-12-26
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: ahed8
command: skills creation request
labels: ["skills", "setup", "foundation", "cli", "python"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/python-console-cli.md
  - .claude/skills/in-memory-data-store.md
  - .claude/skills/crud-operations.md
  - .claude/skills/python-testing.md
  - .claude/skills/clean-code-python.md
  - .claude/skills/error-handling.md
  - .claude/skills/input-validation.md
  - .claude/skills/output-formatting.md
  - .claude/skills/python-data-models.md
  - .claude/skills/command-parsing.md
  - .claude/skills/spec-driven-development.md
  - .claude/skills/uv-package-management.md
  - .claude/skills/README.md
tests:
  - N/A (foundation setup, no tests)
---

## Prompt

Create all required SKILLS for my project inside the directory:
.claude/skills

Project Context:
- Python Console Todo CLI Application (In-Memory)
- Technology Stack:
  - Python 3.13+
  - UV
  - Claude Code
  - Spec-Kit Plus (installed and authoritative)

Core Features (for skill scope):
- Add Todo
- Delete Todo
- Update Todo
- View Todos
- Mark Todo as Complete

Skill Requirements:
- Each skill must be created as a separate, clearly named skill file
- Skills should support:
  - Spec-driven development
  - Clean code practices
  - Console CLI behavior
  - In-memory data handling
  - Python 3.13 compatibility
- Skills must be GENERIC and REUSABLE
- Do NOT hardcode specifications or assumptions
- Do NOT implement business logic yet
- Skills should describe capabilities, responsibilities, and usage intent

Rules:
- Treat Spec-Kit Plus as the source of truth for future specs
- Do NOT generate application code
- Do NOT skip any foundational skill required for this type of project

Output:
- Create the `.claude/skills` directory
- Populate it with all relevant skill definitions needed for this project
- Use clean, professional naming conventions
- Ensure skills are ready to be used later by agents

## Response snapshot

Created 12 foundational skills plus README index for the Python Console Todo CLI Application:

**Core Python Development:**
- python-console-cli: CLI application patterns
- clean-code-python: Code quality standards
- python-data-models: Dataclass and type patterns
- python-testing: TDD and pytest practices

**CLI-Specific Patterns:**
- command-parsing: argparse/click patterns
- output-formatting: Terminal output formatting
- input-validation: User input validation
- error-handling: Graceful error handling

**Data Management:**
- in-memory-data-store: In-memory storage patterns
- crud-operations: CRUD operation patterns

**Project Workflow:**
- spec-driven-development: SDD workflow integration
- uv-package-management: UV project management

## Outcome

- ✅ Impact: Foundation skills created for all agents to reference during implementation
- 🧪 Tests: N/A - setup task, no code implementation
- 📁 Files: 13 files created in .claude/skills/
- 🔁 Next prompts: Run /sp.constitution, then /sp.specify for first feature
- 🧠 Reflection: Skills cover all aspects needed for a Python CLI todo app without hardcoding business logic

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - all skills created, generic, reusable
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
