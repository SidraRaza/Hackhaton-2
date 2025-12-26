# Skill: Console Output Formatting

## Identifier
`output-formatting`

## Purpose
Provides patterns for formatting console output in CLI applications. This skill enables agents to create clear, readable, and user-friendly terminal output that enhances the user experience.

## Scope
- Text formatting for terminals
- Table and list display
- Color and styling (optional)
- Progress indication
- Output streams (stdout/stderr)

## Capabilities

### Basic Formatting
- Use consistent indentation for hierarchy
- Align columns for tabular data
- Use appropriate line spacing
- Wrap long text to terminal width
- Format numbers and dates consistently

### Output Streams
- Use stdout for normal output
- Use stderr for errors and warnings
- Support piping and redirection
- Detect interactive vs non-interactive terminals
- Adjust formatting based on output destination

### Tabular Data
- Align columns with consistent spacing
- Use headers to label columns
- Handle varying content widths
- Truncate or wrap long content
- Support sorting and filtering output

### List Display
- Use numbered lists for ordered items
- Use bullets for unordered items
- Show item status indicators
- Support nested lists when needed
- Handle empty lists gracefully

### Status Messages
- Use clear success/failure indicators
- Show action performed and result
- Include relevant details without clutter
- Use consistent message patterns
- Support different verbosity levels

### Progress Indication
- Show progress for long operations
- Use simple text indicators (dots, counters)
- Provide completion status
- Handle interruption gracefully
- Support quiet mode

### Color and Styling (Optional)
- Use color sparingly for emphasis
- Ensure functionality without color
- Check terminal capability before using color
- Use standard ANSI codes or libraries
- Provide colorless fallback

## Responsibilities
- Ensure output is readable and professional
- Maintain consistency across all commands
- Respect terminal capabilities and user preferences
- Provide appropriate detail level

## Usage Intent
Apply this skill when producing any user-facing output. Output formatting significantly impacts user experience and perceived quality of the application.

## Dependencies
- Python 3.13+ standard library
- Optional: rich, colorama, or similar for enhanced formatting

## Anti-Patterns to Avoid
- Inconsistent formatting between commands
- Hardcoding terminal widths
- Sending errors to stdout
- Excessive or unnecessary output
- Formatting that breaks piping
- Assuming color support without checking
- Cluttered or hard-to-scan output

## Quality Criteria
- Output is clear and easy to read
- Formatting is consistent across commands
- Errors are clearly distinguished from normal output
- Output works correctly when piped
- Terminal capabilities are respected
