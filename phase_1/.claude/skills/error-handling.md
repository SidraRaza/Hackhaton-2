# Skill: Error Handling Patterns

## Identifier
`error-handling`

## Purpose
Provides patterns for handling errors gracefully in console applications. This skill enables agents to implement robust error handling that provides clear feedback to users and maintains application stability.

## Scope
- Exception handling strategies
- User-friendly error messages
- Error categorization
- Recovery patterns
- Logging and debugging support

## Capabilities

### Exception Handling
- Catch specific exceptions, not bare `except`
- Handle exceptions at appropriate levels
- Preserve exception context when re-raising
- Use custom exceptions for domain-specific errors
- Clean up resources in `finally` blocks

### Custom Exceptions
- Define domain-specific exception classes
- Inherit from appropriate base exceptions
- Include relevant context in exception messages
- Group related exceptions in a hierarchy
- Keep exception classes simple and focused

### Error Categories
- Input errors: Invalid user input
- State errors: Invalid operation for current state
- Not found errors: Requested resource doesn't exist
- Validation errors: Data fails validation rules
- System errors: Unexpected failures

### User-Friendly Messages
- Translate technical errors to user-friendly messages
- Explain what went wrong clearly
- Suggest corrective actions when possible
- Avoid exposing internal details in user messages
- Maintain consistent message formatting

### Error Boundaries
- Establish error handling boundaries at layer transitions
- Handle errors at CLI layer for user-facing messages
- Propagate errors with context from lower layers
- Never swallow exceptions silently
- Log errors for debugging before converting to user messages

### Recovery Patterns
- Provide retry options for transient failures
- Offer fallback behavior when appropriate
- Allow graceful degradation
- Support rollback for failed transactions
- Exit cleanly on unrecoverable errors

## Responsibilities
- Prevent application crashes from unhandled exceptions
- Provide clear, actionable error feedback to users
- Maintain error context for debugging
- Ensure consistent error handling across the application

## Usage Intent
Apply this skill when implementing any functionality that can fail. Error handling should be considered during design, not added as an afterthought.

## Dependencies
- Python 3.13+ exception system
- Logging module (for error logging)

## Anti-Patterns to Avoid
- Bare `except:` clauses
- Silently swallowing exceptions
- Using exceptions for control flow
- Exposing stack traces to end users
- Catching exceptions too broadly
- Not cleaning up resources on error
- Generic error messages that don't help users

## Quality Criteria
- All expected errors are handled gracefully
- Error messages are clear and actionable
- Exceptions don't crash the application
- Error context is preserved for debugging
- Resources are cleaned up properly on error
