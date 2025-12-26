# Skill: Command-Line Argument Parsing

## Identifier
`command-parsing`

## Purpose
Provides patterns for parsing command-line arguments in Python CLI applications. This skill enables agents to implement intuitive, well-documented command interfaces using standard Python tools.

## Scope
- Argument parser setup and configuration
- Command and subcommand structures
- Argument types and validation
- Help text generation
- Error handling for invalid arguments

## Capabilities

### Parser Setup
- Use argparse (standard library) or click (enhanced UX)
- Define program description and epilog
- Set appropriate formatter class
- Configure exit behavior
- Support configuration from files/environment when needed

### Arguments and Options
- Define positional arguments for required inputs
- Define optional arguments with flags (-x, --long-form)
- Use short and long form options consistently
- Set appropriate argument types
- Provide default values with documentation

### Subcommands
- Implement subcommand structure for multi-action CLIs
- Use consistent subcommand naming
- Share common options across subcommands
- Provide help for each subcommand
- Handle no-subcommand case gracefully

### Argument Types
- Use built-in types (str, int, float)
- Define custom type functions for validation
- Handle file path arguments appropriately
- Support choice constraints
- Validate argument combinations

### Help and Documentation
- Write clear argument help text
- Include usage examples in epilog
- Document default values
- Show required vs optional clearly
- Support --help at all levels

### Argument Validation
- Validate types during parsing
- Check argument relationships after parsing
- Provide specific error messages
- Suggest corrections for common mistakes
- Fail fast on invalid arguments

### Best Practices
- Follow GNU/POSIX conventions
- Use consistent naming across commands
- Keep argument lists manageable
- Group related options
- Support standard options (--version, --help, --verbose)

## Responsibilities
- Parse command-line arguments reliably
- Provide helpful usage information
- Validate input at the CLI boundary
- Maintain consistent command interface

## Usage Intent
Apply this skill when implementing any CLI interface. The command structure and argument handling form the user's primary interaction point with the application.

## Dependencies
- argparse (standard library) or click (external)
- Python 3.13+

## Anti-Patterns to Avoid
- Manual argument parsing without a library
- Inconsistent option naming (mixing conventions)
- Missing help text for arguments
- Silent defaults without documentation
- Ignoring argument parsing errors
- Too many required arguments
- Complex argument interdependencies

## Quality Criteria
- --help provides complete usage information
- Invalid arguments produce clear error messages
- Command structure is intuitive
- All arguments are documented
- Common conventions are followed
