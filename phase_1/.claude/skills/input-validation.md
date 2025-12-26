# Skill: Input Validation Patterns

## Identifier
`input-validation`

## Purpose
Provides patterns for validating user input in console applications. This skill enables agents to implement robust input validation that ensures data integrity and provides helpful feedback.

## Scope
- Input type validation
- Business rule validation
- Constraint checking
- Validation error reporting
- Sanitization patterns

## Capabilities

### Type Validation
- Validate expected data types
- Handle type conversion safely
- Check for None/empty values
- Validate collection types and their contents
- Support optional vs required fields

### String Validation
- Check minimum/maximum length
- Validate against patterns (regex when needed)
- Handle whitespace (trim, reject, normalize)
- Check for prohibited characters
- Validate encoding when relevant

### Numeric Validation
- Validate numeric ranges
- Check for positive/negative constraints
- Handle precision requirements
- Validate integer vs decimal requirements
- Check for overflow potential

### Business Rule Validation
- Apply domain-specific rules
- Validate relationships between fields
- Check against allowed values (enums)
- Enforce uniqueness constraints
- Validate state-dependent rules

### Validation Strategies
- Fail-fast: Stop at first error
- Collect-all: Gather all errors before reporting
- Use appropriate strategy based on context
- Combine with clear error reporting
- Validate at system boundaries

### Error Reporting
- Report specific validation failures
- Include field name and constraint violated
- Provide expected vs actual values when helpful
- Order errors logically
- Support both single and multiple error reporting

### Sanitization
- Trim whitespace from strings
- Normalize case when appropriate
- Convert to expected types safely
- Remove or escape dangerous characters
- Apply consistent formatting

## Responsibilities
- Prevent invalid data from entering the system
- Provide clear feedback on validation failures
- Ensure consistent validation across the application
- Balance security with usability

## Usage Intent
Apply this skill at all system boundaries where external input is received. Input should be validated before processing and before storage.

## Dependencies
- Python 3.13+ standard library
- Domain-specific validation rules from spec

## Anti-Patterns to Avoid
- Trusting user input without validation
- Inconsistent validation across entry points
- Vague validation error messages
- Validating too late in the process
- Over-restrictive validation that frustrates users
- Validation that can be bypassed
- Mixing validation with business logic

## Quality Criteria
- All external input is validated
- Validation errors are clear and specific
- Invalid data never reaches storage
- Validation is consistent across the application
- Edge cases are handled properly
