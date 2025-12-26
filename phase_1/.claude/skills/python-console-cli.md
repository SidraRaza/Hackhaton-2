# Skill: Python Console CLI Development

## Identifier
`python-console-cli`

## Purpose
Provides foundational knowledge and patterns for building command-line interface applications in Python. This skill enables agents to create interactive, user-friendly console applications following Python best practices.

## Scope
- Console application architecture
- User interaction patterns via terminal
- Application entry points and bootstrapping
- Signal handling (CTRL+C, etc.)
- Exit code conventions

## Capabilities

### Application Structure
- Define clear entry points using `if __name__ == "__main__"` or console script entry points
- Organize code into logical modules (commands, core, utils)
- Implement clean separation between CLI layer and business logic
- Support both interactive and non-interactive modes

### Terminal Interaction
- Read user input via `input()` or stdin
- Write output to stdout for normal messages
- Write errors to stderr for error messages
- Handle terminal signals gracefully (KeyboardInterrupt, SIGTERM)
- Support piping and redirection where appropriate

### Exit Codes
- Return 0 for successful execution
- Return non-zero codes for different error types:
  - 1: General errors
  - 2: Command-line usage errors
  - Other codes as defined by application spec

### Python 3.13+ Compatibility
- Use modern Python syntax and features
- Leverage structural pattern matching where appropriate
- Use type hints throughout
- Follow PEP 8 and modern Python idioms

## Responsibilities
- Ensure CLI applications are intuitive and follow Unix conventions
- Maintain consistency in command structure and output formatting
- Provide helpful feedback to users
- Handle edge cases at the CLI boundary

## Usage Intent
Apply this skill when building any Python console application. It serves as the foundation upon which other skills (command parsing, output formatting, etc.) are layered.

## Dependencies
- Python 3.13+
- No external dependencies for core functionality

## Anti-Patterns to Avoid
- Mixing business logic with CLI handling
- Ignoring exit codes
- Printing errors to stdout instead of stderr
- Blocking indefinitely without timeout or interrupt handling
- Hardcoding terminal widths or ANSI codes without checking terminal capabilities

## Quality Criteria
- Application starts and exits cleanly
- All user-facing messages are clear and actionable
- Exit codes correctly reflect execution status
- Application handles interrupts gracefully
