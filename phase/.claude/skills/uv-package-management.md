# Skill: UV Package Management

## Identifier
`uv-package-management`

## Purpose
Provides patterns for managing Python projects using UV (the fast Python package installer and resolver). This skill enables agents to work effectively with UV-based project structures, dependencies, and virtual environments.

## Scope
- UV project setup and configuration
- Dependency management with UV
- Virtual environment handling
- Package installation and updates
- Lock file management

## Capabilities

### Project Setup
- Initialize projects with `uv init`
- Configure pyproject.toml for UV
- Set up virtual environments with UV
- Configure Python version requirements
- Structure projects following UV conventions

### Dependency Management
- Add dependencies with `uv add <package>`
- Remove dependencies with `uv remove <package>`
- Specify version constraints appropriately
- Separate dev dependencies from runtime dependencies
- Lock dependencies with `uv lock`

### Virtual Environments
- Create environments with `uv venv`
- Activate and use UV-managed environments
- Sync environment with lock file using `uv sync`
- Handle multiple Python versions
- Clean and recreate environments when needed

### Package Installation
- Install packages quickly with UV's resolver
- Install from lock file for reproducibility
- Handle package extras and optional dependencies
- Install editable packages for development
- Manage platform-specific dependencies

### Lock File Management
- Generate and maintain uv.lock
- Commit lock file to version control
- Update lock file when dependencies change
- Resolve conflicts in lock files
- Understand lock file structure

### Integration with pyproject.toml
- Define project metadata
- Configure build requirements
- Specify optional dependencies
- Set up console scripts
- Configure tool settings

## Responsibilities
- Maintain consistent dependency management
- Ensure reproducible builds through lock files
- Keep dependencies up to date and secure
- Follow UV best practices

## Usage Intent
Apply this skill when setting up or managing Python projects using UV. UV provides fast, reliable dependency management that integrates well with modern Python workflows.

## Dependencies
- UV installed and available in PATH
- Python 3.13+ as specified by project
- pyproject.toml configuration

## Anti-Patterns to Avoid
- Mixing UV with pip in the same environment
- Ignoring lock file changes
- Not committing uv.lock to version control
- Installing packages globally instead of in venv
- Ignoring version constraints
- Not separating dev and runtime dependencies

## Quality Criteria
- All dependencies are tracked in pyproject.toml
- Lock file is up to date and committed
- Virtual environment synced with lock file
- No conflicting package versions
- Dependencies can be installed reproducibly
