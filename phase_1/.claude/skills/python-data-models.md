# Skill: Python Data Models

## Identifier
`python-data-models`

## Purpose
Provides patterns for defining data models in Python using modern features. This skill enables agents to create type-safe, well-structured data representations using dataclasses and other Python constructs.

## Scope
- Dataclass definition and usage
- Type annotations for models
- Immutability and mutability
- Serialization patterns
- Model validation integration

## Capabilities

### Dataclasses
- Define data models using `@dataclass` decorator
- Use field() for default values and metadata
- Implement `__post_init__` for validation or computation
- Support frozen dataclasses for immutability
- Use slots for memory efficiency when appropriate

### Type Annotations
- Annotate all fields with appropriate types
- Use `Optional` for nullable fields
- Use `list`, `dict`, `set` generic types
- Use `Literal` for constrained values
- Use `Union` for multiple allowed types

### Default Values
- Provide sensible defaults for optional fields
- Use `field(default_factory=...)` for mutable defaults
- Document meaning of default values
- Distinguish between "not provided" and explicit None

### Immutability
- Use frozen=True for immutable models
- Prefer immutable models for value objects
- Use mutable models when state changes are required
- Document mutability expectations

### Model Relationships
- Reference other models by ID for loose coupling
- Embed models directly for tight coupling
- Avoid circular references
- Keep models focused and cohesive

### Serialization
- Support conversion to/from dictionaries
- Use `asdict()` for simple serialization
- Handle nested models appropriately
- Support custom serialization when needed

### Model Methods
- Add computed properties for derived data
- Implement comparison methods when needed
- Add factory methods for common creation patterns
- Keep business logic separate from models

## Responsibilities
- Define clear, type-safe data structures
- Ensure data integrity through proper modeling
- Provide consistent patterns across the application
- Support serialization and deserialization needs

## Usage Intent
Apply this skill when defining any data structures. Well-designed data models are fundamental to clean architecture and maintainable code.

## Dependencies
- Python 3.13+ dataclasses module
- typing module for type annotations

## Anti-Patterns to Avoid
- Using plain dictionaries instead of typed models
- Mutable default arguments in dataclasses
- God models with too many fields
- Missing type annotations
- Business logic in data models
- Circular dependencies between models
- Exposing mutable internals

## Quality Criteria
- All models have complete type annotations
- Models are appropriately scoped and focused
- Immutability is used where appropriate
- Models are easy to construct and use
- Serialization works correctly
