---
id: "001"
title: "Fix better-auth import errors for useSession"
stage: "red"
date_iso: "2026-01-16"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "main"
user: "claude"
command: "sp.specify"
labels: ["auth", "imports", "errors"]
spec: null
ticket: null
adr: null
pr: null
files_yaml: |
  - frontend/lib/better-auth-client.ts
  - frontend/lib/auth.tsx
  - frontend/components/AuthComponent.tsx
  - frontend/app/page.tsx
tests_yaml: |
  - "Verify useSession hook works correctly"
  - "Test authentication flow"
prompt_text: |
  /sp.specfiy
   solve all errors
  ./app/page.tsx:3:1
  Export useSession doesn't exist in target module
    1 | 'use client';
    2 |
  > 3 | import { useSession } from 'better-auth/react';
      | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  4 | import AuthComponent from '../components/AuthComponent';
  5 | import TaskList from '../components/TaskList';
  6 | import { useAuth } from '../lib/auth';

  The export useSession was not found in module [project]/node_modules/better-auth/dist/client/react/index.mjs [app-ssr] (ecmascript).
  Did you mean to import useStore?
  All exports of the module are statically known (It doesn't have dynamic exports). So it's known statically that the requested export doesn't exist.
response_text: |
  Fixed the import errors by creating a proper better-auth client wrapper and updating all import statements.
  Created frontend/lib/better-auth-client.ts that properly implements createAuthClient pattern as documented.
  Updated all files to import from the client wrapper instead of directly from 'better-auth/react'.
outcome: "Successfully fixed all better-auth import errors and established proper client pattern"
evaluation: "All import errors resolved, authentication flow tested and working"
---