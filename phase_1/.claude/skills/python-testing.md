# Skill: Python Testing Practices

## Identifier
`python-testing`

## Purpose
Provides patterns and practices for writing effective tests in Python. This skill enables agents to implement Test-Driven Development (TDD), write comprehensive test suites, and ensure code quality through automated testing.

## Scope
- Unit testing with pytest
- Test-Driven Development workflow
- Test organization and structure
- Mocking and fixtures
- Assertion patterns

## Capabilities

### Test-Driven Development (TDD)
- Write tests before implementation (Red-Green-Refactor)
- Define expected behavior through test cases
- Iterate: failing test -> implementation -> passing test -> refactor
- Use tests as specification documentation

### Test Structure
- Organize tests in `tests/` directory mirroring source structure
- Name test files with `test_` prefix
- Name test functions descriptively: `test_<what>_<scenario>_<expected>`
- Use classes to group related tests when appropriate
- Keep tests focused and independent

### Test Types
- Unit tests: Test individual functions/methods in isolation
- Integration tests: Test component interactions
- Edge case tests: Test boundary conditions and error paths
- Regression tests: Prevent previously fixed bugs from recurring

### Pytest Features
- Use fixtures for setup and teardown
- Use parametrize for testing multiple inputs
- Use marks for categorizing tests
- Use conftest.py for shared fixtures
- Use plugins for extended functionality

### Assertions
- Use plain assert statements (pytest enhances them)
- Test one logical concept per test function
- Include both positive and negative test cases
- Assert expected exceptions with `pytest.raises`
- Assert approximately equal values with `pytest.approx`

### Mocking
- Use `unittest.mock` or `pytest-mock` for isolation
- Mock external dependencies and I/O
- Verify mock interactions when behavior matters
- Prefer dependency injection over patching when possible

## Responsibilities
- Ensure code correctness through comprehensive tests
- Maintain test quality alongside code quality
- Keep tests fast and reliable
- Document expected behavior through tests

## Usage Intent
Apply this skill when implementing any functionality. Tests should be written as part of the development process, not as an afterthought. Use TDD workflow when developing new features.

## Dependencies
- pytest (test framework)
- pytest-cov (optional, for coverage)
- unittest.mock (standard library)

## Anti-Patterns to Avoid
- Writing tests after all code is complete
- Tests that depend on execution order
- Tests that share mutable state
- Over-mocking (testing implementation, not behavior)
- Ignoring test failures or skipping flaky tests

## Quality Criteria
- All public functions have corresponding tests
- Tests cover both happy path and error cases
- Tests are independent and can run in any order
- Test names clearly describe what is being tested
- Tests run quickly (< 1 second per test for unit tests)
