# Skill: CRUD Operations Patterns

## Identifier
`crud-operations`

## Purpose
Provides patterns for implementing Create, Read, Update, and Delete operations. This skill enables agents to build consistent, reliable data manipulation functionality following established conventions.

## Scope
- Create operations with validation
- Read operations (single and bulk)
- Update operations (partial and full)
- Delete operations (soft and hard)
- Operation result handling

## Capabilities

### Create Operations
- Validate input data before creation
- Generate identifiers for new items
- Set default values for optional fields
- Return created item with generated ID
- Handle duplicate prevention when applicable

### Read Operations
- Retrieve single item by identifier
- Retrieve all items with optional filtering
- Support pagination for large datasets
- Return None/empty list for missing data (not exceptions)
- Provide count/exists operations

### Update Operations
- Validate item exists before updating
- Support partial updates (only specified fields)
- Support full replacement updates
- Preserve immutable fields (ID, created_at)
- Return updated item or success indicator

### Delete Operations
- Validate item exists before deletion
- Support hard delete (permanent removal)
- Support soft delete (mark as deleted) when applicable
- Return success indicator or deleted item
- Handle cascading deletes if relationships exist

### Result Handling
- Return consistent result types for each operation
- Distinguish between success and failure clearly
- Provide meaningful error information
- Support both exception-based and return-value-based error handling

## Responsibilities
- Ensure data consistency across all operations
- Validate inputs at operation boundaries
- Provide clear feedback for operation results
- Handle edge cases (not found, already exists, invalid data)

## Usage Intent
Apply this skill when implementing any data manipulation functionality. CRUD patterns provide a consistent interface that users and other code can rely upon.

## Dependencies
- Data validation skill (input-validation)
- Data storage mechanism (in-memory or persistent)

## Anti-Patterns to Avoid
- Silently failing on errors
- Inconsistent return types between operations
- Modifying data without validation
- Exposing storage implementation details
- Mixing CRUD logic with business rules

## Quality Criteria
- All four operations (CRUD) work correctly
- Operations return consistent, predictable results
- Validation prevents invalid data from being stored
- Edge cases return appropriate responses
