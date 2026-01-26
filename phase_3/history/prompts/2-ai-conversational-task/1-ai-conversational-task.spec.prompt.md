---
id: 1
title: "AI Conversational Task Management Specification"
stage: "spec"
date_iso: "2026-01-24"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "ai-conversational-task"
branch: "2-ai-conversational-task"
user: "user"
command: "/sp.specify You are working on an existing project where Phase 2 is already completed..."
labels: ["ai", "conversational-interface", "task-management", "mcp", "openai-agents"]
links:
  spec: "specs/2-ai-conversational-task/spec.md"
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - specs/2-ai-conversational-task/spec.md
  - specs/2-ai-conversational-task/plan.md
  - specs/2-ai-conversational-task/tasks.md
  - specs/2-ai-conversational-task/checklists/requirements.md
tests_yaml: |
  - backend/tests/test_mcp_tools.py
  - backend/tests/test_security.py
  - backend/tests/e2e_chat.py
  - frontend/tests/regression.js
prompt_text: |
  You are working on an existing project where Phase 2 is already completed.
  Your task is to implement Phase 3 only by modifying the existing frontend and backend, NOT creating new separate apps.

  🔴 VERY IMPORTANT CONSTRAINTS

  ❌ Do NOT create a new frontend project

  ❌ Do NOT create a new backend project

  ✅ Modify the existing frontend and backend codebase

  ✅ Reuse existing database, auth, and task models

  ❌ Do NOT break Phase 2 functionality

  ❌ Do NOT introduce in-memory or session-based state

  📌 Phase 3 Objective

  Add AI-powered conversational task management using:

  OpenAI Agents SDK

  MCP (Model Context Protocol)
  while keeping the system fully stateless and persisting all state in the database.

  🧩 Features to Add (Phase 3 Only)
  1️⃣ Conversational Interface (Basic Features)

  Integrate chat-based task management inside the existing frontend

  Use OpenAI ChatKit for UI

  Supported actions via chat:

  Create task

  Update task

  Delete task

  List tasks

  Mark task as completed

  No task forms or buttons — chat only

  2️⃣ AI Logic (OpenAI Agents SDK)

  Integrate OpenAI Agents SDK into the existing backend

  AI handles:

  User intent understanding

  Tool calling

  AI must be stateless

  Conversation context must be fetched from DB on every request

  3️⃣ MCP Server (Official MCP SDK)

  Add an MCP server (can be a service/module inside the existing backend repo)

  Use Official MCP SDK

  MCP exposes task tools:

  create_task

  update_task

  delete_task

  get_tasks

  complete_task

  MCP tools:

  Are stateless

  Read/write directly from DB using SQLModel

  AI Agent must call MCP tools instead of directly accessing DB

  4️⃣ Stateless Chat API

  Add a stateless chat endpoint to existing FastAPI backend

  Flow per request:

  Authenticate user (Better Auth)

  Load conversation + messages from DB

  Send messages to AI Agent

  AI calls MCP tools if needed

  Store new messages in DB

  No Redis, no server memory

  5️⃣ Database Changes (If Missing)

  Extend existing database using SQLModel:

  Conversation Table

  id

  user_id

  created_at

  Message Table

  id

  conversation_id

  role (user, assistant, tool)

  content

  created_at

  ⚠️ Reuse existing Tasks table from Phase 2

  6️⃣ Authentication

  Use existing Better Auth setup

  Every chat and MCP tool call must be:

  User-scoped

  Secure

  MCP tools must validate user identity from request context

  🧠 Architecture Rules

  Frontend → Chat API → AI Agent → MCP Tools → Database

  AI does NOT contain business logic

  MCP tools are the single source of truth for task operations

  Everything must be production-ready and cleanly structured

  🛠️ Tech Stack (Must Use)
  Layer    Tech
  Frontend    OpenAI ChatKit
  Backend    Python FastAPI (existing)
  AI    OpenAI Agents SDK
  MCP    Official MCP SDK
  ORM    SQLModel
  DB    Neon Serverless PostgreSQL
  Auth    Better Auth
  ✅ Expected Result

  Existing project enhanced with AI chat

  No new apps created

  Stateless conversational task management

  Phase 2 features remain fully functional
response_text: |
  Created comprehensive specification, implementation plan, and task breakdown for AI-powered conversational task management feature. The solution includes:

  1. Database extensions with Conversation and Message models
  2. MCP server with task management tools (create, update, delete, get, complete)
  3. OpenAI Agents SDK integration for intent recognition
  4. Stateless chat API endpoint with Better Auth
  5. Frontend integration with OpenAI ChatKit

  The architecture follows the pattern: Frontend → Chat API → AI Agent → MCP Tools → Database, ensuring all state is persisted in the database while maintaining a stateless application layer.
outcome: "Successfully created feature specification with detailed requirements, implementation plan, and task breakdown for AI conversational task management system."
evaluation: "Specification covers all required components including database schema, MCP tools, AI integration, and frontend implementation. Success criteria are measurable and testable. Implementation plan follows logical phases with proper dependencies."
---