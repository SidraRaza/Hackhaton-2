---
id: 1
title: "Create Project Constitution"
stage: "constitution"
date: "2026-01-15"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "user"
command: "/sp.constitution"
labels: ["constitution", "setup", "hackathon-todo"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - ".specify/memory/constitution.md"
tests: []
---

# Create Project Constitution

## Prompt Text
```
/sp.constitution
project_name: hackathon-todo
version: 1.0
description: >
  Phase II Full-Stack Todo App transforming a console application into a full-stack multi-user web application.
  Managed with Spec-Kit Plus and Claude Code for spec-driven development. Implements task CRUD, authentication,
  responsive frontend, REST API, and persistent storage with Neon Serverless PostgreSQL.

principles:
  # Core principles guiding the project and agents
  always_reference_specs: true               # All implementation must reference specs
  never_modify_without_spec: true           # No code change without updating specs
  maintain_layer_separation: true           # Frontend and backend layers are separate
  ensure_security: true                     # JWT auth, user isolation, token expiry enforced
  ensure_responsiveness: true               # Frontend must work on mobile and desktop
  reuse_skills: true                        # Agents must reuse skills for repetitive tasks
  maintain_code_quality: true               # Follow coding standards, linting, type safety

layers:
  frontend:
    path: ./frontend
    description: >
      Next.js 16+ App Router, TypeScript, Tailwind CSS.
      Responsible for UI rendering, authentication flow, API requests, and client-side state management.
    guidelines: @claude/frontend.md
    responsibilities:
      - Implement pages and layouts
      - Build reusable UI components
      - Consume backend REST API
      - Attach JWT token to all API requests
      - Handle user authentication sessions

  backend:
    path: ./backend
    description: >
      Python FastAPI server using SQLModel ORM and Neon PostgreSQL.
      Responsible for handling REST API requests, database interactions, JWT verification, and business logic.
    guidelines: @claude/backend.md
    responsibilities:
      - Implement REST API endpoints
      - Verify JWT tokens and enforce user access
      - Manage database models and migrations
      - Handle CRUD operations for tasks
      - Validate input using Pydantic models
      - Return structured JSON responses
      - Error handling with proper HTTP status codes

  database:
    path: ./backend/models
    description: >
      Neon Serverless PostgreSQL database with tables for users and tasks.
      All queries filtered by user_id to ensure user isolation.
    responsibilities:
      - Define tables and indexes
      - Ensure data integrity and relations
      - Optimize for queries by status and user
      - Provide connection using environment variables
      - Maintain schema migrations

authentication:
  method: JWT via Better Auth
  flow:
    - User logs in on frontend using Better Auth
    - Frontend receives JWT token
    - Frontend attaches JWT token to Authorization header
    - Backend verifies JWT token signature using shared secret
    - Backend decodes token to identify user and filter tasks
  environment_variable: BETTER_AUTH_SECRET
  token_expiry: 7 days
  user_isolation: true
  stateless_auth: true

agents:
  # Autonomous agents to manage tasks, auth, frontend, backend, and testing
  - name: Task Manager Agent
    role: Developer Agent
    description: >
      Handles CRUD operations for tasks, including creation, update, deletion, and completion.
      Ensures tasks belong only to authenticated user.
    tools: ["claude-code", "spec-kit-plus", "fastapi", "nextjs", "sqlmodel", "postgresql"]
    tasks:
      - implement_task_crud_backend
      - implement_task_crud_frontend
      - write_unit_tests_for_tasks
      - verify_user_task_isolation

  - name: Authentication Agent
    role: Security & Auth Agent
    description: >
      Handles Better Auth integration, JWT issuance, verification, and frontend auth flows.
      Ensures secure login/signup and token-based authentication for all API requests.
    tools: ["claude-code", "better-auth", "jwt", "fastapi", "nextjs"]
    tasks:
      - implement_signup_login
      - configure_jwt_plugin
      - attach_jwt_to_frontend_requests
      - verify_backend_auth_middleware

  - name: API Agent
    role: API Development Agent
    description: >
      Creates and maintains all REST API endpoints according to the specification.
      Ensures endpoints follow HTTP conventions and handle proper request validation.
    tools: ["claude-code", "fastapi", "sqlmodel"]
    tasks:
      - implement_get_tasks_endpoint
      - implement_post_tasks_endpoint
      - implement_put_tasks_endpoint
      - implement_delete_tasks_endpoint
      - implement_patch_complete_endpoint
      - write_api_tests

  - name: Frontend Agent
    role: Frontend Development Agent
    description: >
      Develops responsive pages and components for the Next.js frontend.
      Ensures integration with backend API and Better Auth sessions.
    tools: ["claude-code", "nextjs", "typescript", "tailwind-css"]
    tasks:
      - build_task_pages
      - build_layouts_and_navigation
      - integrate_api_client
      - attach_jwt_to_requests
      - handle_error_and_loading_states

  - name: Backend Agent
    role: Backend Development Agent
    description: >
      Develops FastAPI backend logic, including task handling, authentication verification, and database interaction.
      Responsible for ensuring data integrity and business logic correctness.
    tools: ["claude-code", "fastapi", "sqlmodel", "postgresql"]
    tasks:
      - implement_database_models
      - configure_database_connection
      - implement_api_routes
      - enforce_jwt_auth
      - handle_exceptions_and_responses

skills:
  # Reusable skills that agents can leverage
  - name: create_api_endpoint
    description: Automates creation of FastAPI endpoint based on REST API spec
    steps:
      - read_spec_for_endpoint
      - generate_pydantic_models
      - create_fastapi_route
      - add_jwt_verification
      - return_endpoint_code

  - name: create_frontend_component
    description: Automates creation of reusable React components using Tailwind CSS
    steps:
      - read_ui_spec
      - generate_component_structure
      - add_props_and_state
      - integrate_api_calls_if_needed
      - return_component_code

  - name: create_sqlmodel_model
    description: Creates SQLModel ORM models based on database spec
    steps:
      - read_database_spec
      - generate_model_fields
      - define_relationships
      - return_model_code

  - name: verify_jwt_auth
    description: Verifies JWT token in FastAPI requests and returns user identity
    steps:
      - extract_token_from_header
      - decode_and_verify_signature
      - validate_token_expiry
      - return_user_info

  - name: write_unit_test
    description: Creates automated unit tests for backend or frontend functionality
    steps:
      - read_spec_for_test_case
      - generate_test_code
      - add_assertions
      - return_test_file

workflow:
  development_steps:
    - read_spec: true
    - break_into_tasks: true
    - assign_to_agents: true
    - implement_backend: true
    - implement_frontend: true
    - write_unit_tests: true
    - test_full_feature: true
    - deploy: true

permissions:
  claude_agents:
    read_specs: true
    write_code: true
    update_docs: true
    run_tests: true
  humans:
    approve_deployments: true
    update_specs: true
  security:
    jwt_secret: BETTER_AUTH_SECRET
    enforce_user_isolation: true

notes:
  - All code must strictly follow the specifications in /sp.specs
  - Agents must use skills to avoid repetitive implementations
  - Frontend requests must attach JWT token to Authorization header
  - Backend validates JWT on every request
  - User can only see and modify their own tasks
  - Token expiry enforced after 7 days
```

## Response Text
Constitution file created at `.specify/memory/constitution.md` with all specified principles, layer architectures, agent responsibilities, and development workflow.

## Outcome
Successfully created the project constitution file that captures all the specified requirements for the hackathon-todo project. The constitution defines core principles, system architecture, authentication flow, agent responsibilities, and development workflow.