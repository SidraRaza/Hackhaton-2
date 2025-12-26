# Skill: Clean Code Practices for Python

## Identifier
`clean-code-python`

## Purpose
Provides principles and practices for writing clean, maintainable Python code. This skill enables agents to produce code that is readable, testable, and follows Python community standards.

## Scope
- Code readability and clarity
- Function and class design
- Naming conventions
- Code organization
- Python-specific idioms

## Capabilities

### Readability
- Write self-documenting code with clear intent
- Use meaningful names for variables, functions, and classes
- Keep functions short and focused (single responsibility)
- Limit line length to 88-120 characters
- Use vertical spacing to separate logical sections

### Naming Conventions
- snake_case for functions, methods, and variables
- PascalCase for classes
- UPPER_SNAKE_CASE for constants
- Use verbs for functions that perform actions
- Use nouns for variables and classes
- Avoid abbreviations unless universally understood

### Function Design
- Functions should do one thing well
- Limit function arguments (prefer 3 or fewer)
- Use keyword arguments for clarity when helpful
- Return early to reduce nesting
- Prefer pure functions when possible

### Type Hints
- Add type hints to function signatures
- Use generic types from `typing` module appropriately
- Type hint return values, including `None`
- Use `Optional` for nullable types
- Keep type hints readable; use type aliases for complex types

### PEP 8 Compliance
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Add blank lines between functions and classes
- Place imports at file top, grouped logically
- Avoid wildcard imports

### Python Idioms
- Use list/dict/set comprehensions appropriately
- Use context managers for resource handling
- Prefer `in` for membership testing
- Use unpacking for multiple assignments
- Leverage the standard library

### Code Organization
- Group related functionality in modules
- Use `__init__.py` to define public APIs
- Keep modules focused and cohesive
- Avoid circular imports
- Separate concerns into layers (CLI, business logic, data)

## Responsibilities
- Produce code that others can read and maintain
- Follow established Python conventions
- Ensure code is testable by design
- Continuously improve code quality through refactoring

## Usage Intent
Apply this skill to all Python code written. Clean code is not optional; it is a fundamental requirement for professional software development.

## Dependencies
- Python 3.13+
- Understanding of PEP 8 and PEP 484 (type hints)

## Anti-Patterns to Avoid
- Magic numbers and hardcoded strings
- Deep nesting (more than 3 levels)
- God classes or functions
- Duplicate code (DRY violations)
- Ignoring linter warnings
- Commented-out code in production
- Mixing abstraction levels in same function

## Quality Criteria
- Code passes linting without warnings
- Functions are small and single-purpose
- Names are descriptive and consistent
- Code structure reflects logical organization
- No unnecessary complexity
