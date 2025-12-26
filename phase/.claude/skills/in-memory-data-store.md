# Skill: In-Memory Data Store Patterns

## Identifier
`in-memory-data-store`

## Purpose
Provides patterns and best practices for managing application data in memory. This skill enables agents to implement efficient, thread-safe in-memory storage solutions without external database dependencies.

## Scope
- In-memory data structures for storage
- Data lifecycle management
- Session-based data handling
- Collection management patterns
- Data access patterns

## Capabilities

### Storage Structures
- Use appropriate Python data structures (dict, list, set) for different use cases
- Implement lookup-optimized storage using dictionaries with unique keys
- Support ordered collections when sequence matters
- Handle nested data structures cleanly

### Data Lifecycle
- Initialize storage on application start
- Clear storage on application exit or reset
- Support bulk operations (clear all, load initial data)
- Maintain data consistency during operations

### Identifier Management
- Generate unique identifiers for stored items
- Support auto-incrementing integer IDs
- Support UUID-based identifiers when needed
- Ensure ID uniqueness within the store

### Access Patterns
- Get item by ID (O(1) lookup)
- Get all items (iteration)
- Filter items by criteria
- Check item existence
- Count items in store

### Encapsulation
- Encapsulate storage behind a clear interface
- Prevent direct access to internal data structures
- Return copies or immutable views when exposing data
- Validate operations before modifying state

## Responsibilities
- Ensure data integrity during all operations
- Provide consistent access patterns across the application
- Handle edge cases (empty store, missing items, duplicates)
- Maintain clear separation between storage and business logic

## Usage Intent
Apply this skill when implementing data storage for applications that do not require persistence. Ideal for prototypes, session-based applications, and learning projects where database complexity is unnecessary.

## Dependencies
- Python 3.13+ standard library
- No external dependencies required

## Anti-Patterns to Avoid
- Exposing mutable internal state directly
- Using global variables for storage without encapsulation
- Modifying returned data without copying
- Assuming storage persists between runs without explicit save/load
- Ignoring thread safety in concurrent applications

## Quality Criteria
- All CRUD operations work correctly
- Data integrity is maintained across operations
- Edge cases are handled gracefully
- Storage operations have predictable performance
