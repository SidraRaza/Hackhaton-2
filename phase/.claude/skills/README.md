# Skills Index

This directory contains skill definitions for the Python Console Todo CLI Application project. Skills describe capabilities, responsibilities, and usage patterns that agents use when implementing features.

## Available Skills

### Core Python Development

| Skill | Identifier | Description |
|-------|------------|-------------|
| [Python Console CLI](./python-console-cli.md) | `python-console-cli` | Foundational patterns for building Python CLI applications |
| [Clean Code Python](./clean-code-python.md) | `clean-code-python` | Clean code practices and Python conventions |
| [Python Data Models](./python-data-models.md) | `python-data-models` | Dataclass definitions and type-safe data structures |
| [Python Testing](./python-testing.md) | `python-testing` | TDD workflow and pytest best practices |

### CLI-Specific Patterns

| Skill | Identifier | Description |
|-------|------------|-------------|
| [Command Parsing](./command-parsing.md) | `command-parsing` | Command-line argument parsing with argparse/click |
| [Output Formatting](./output-formatting.md) | `output-formatting` | Console output formatting for terminal displays |
| [Input Validation](./input-validation.md) | `input-validation` | User input validation patterns |
| [Error Handling](./error-handling.md) | `error-handling` | Graceful error handling in CLI applications |

### Data Management

| Skill | Identifier | Description |
|-------|------------|-------------|
| [In-Memory Data Store](./in-memory-data-store.md) | `in-memory-data-store` | Patterns for managing data in memory |
| [CRUD Operations](./crud-operations.md) | `crud-operations` | Create, Read, Update, Delete operation patterns |

### Project Workflow

| Skill | Identifier | Description |
|-------|------------|-------------|
| [Spec-Driven Development](./spec-driven-development.md) | `spec-driven-development` | SDD workflow with Spec-Kit Plus |
| [UV Package Management](./uv-package-management.md) | `uv-package-management` | Python project management with UV |

## Usage

Skills are referenced by agents when implementing features. Each skill provides:

- **Purpose**: What the skill enables
- **Scope**: What areas the skill covers
- **Capabilities**: Specific patterns and techniques
- **Responsibilities**: What the skill ensures
- **Anti-Patterns**: What to avoid
- **Quality Criteria**: How to validate proper application

## Skill Structure

Each skill file follows this structure:

```markdown
# Skill: [Name]

## Identifier
`skill-identifier`

## Purpose
[What this skill enables]

## Scope
[Areas covered]

## Capabilities
[Patterns and techniques]

## Responsibilities
[What this ensures]

## Usage Intent
[When to apply]

## Dependencies
[Required tools/skills]

## Anti-Patterns to Avoid
[What not to do]

## Quality Criteria
[Validation checks]
```

## Adding New Skills

When adding a new skill:

1. Create a new `.md` file with a descriptive name
2. Follow the structure above
3. Update this README with the new skill
4. Keep skills generic and reusable
5. Do not hardcode project-specific details

## Technology Stack

These skills are designed for:

- **Python**: 3.13+
- **Package Manager**: UV
- **Development**: Claude Code with Spec-Kit Plus
- **Testing**: pytest
- **Application Type**: Console CLI (in-memory)
