---
id: 1
title: Update Constitution Phase IV
stage: constitution
date: 2026-01-25
surface: agent
model: qwen-2.5-72b-instruct
feature: none
branch: main
user: sidra
command: /sp.constitution
labels: [constitution, phase-iv, kubernetes, deployment]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
---

## Prompt

```
Purpose & Scope

This constitution governs Phase IV only of the project.

Phase IV Objective
Deploy the existing Phase III Todo + AI Chatbot application on a local Kubernetes cluster using:

Docker (Docker Desktop)

Minikube

Helm Charts

AI-assisted DevOps tools (kubectl-ai, kagent, Gordon if available)

📌 No application feature development is allowed in this phase.
📌 Only infrastructure, deployment, and DevOps automation.

2️⃣ Immutable Rules (Must NOT Be Violated)
🔒 Application Code Freeze

Frontend (Next.js) → ❌ NO changes

Backend (FastAPI) → ❌ NO changes

Database schema → ❌ NO changes

Auth logic → ❌ NO changes

If something is broken:

Fix must be done only via configuration, environment variables, or infrastructure

🔒 Single Source of Truth

Phase III code is the only valid application source

Kubernetes manifests, Helm charts, and Dockerfiles must adapt to the app, not the other way around

3️⃣ Architecture Principles
🧱 Containerization Rules

Frontend and Backend must be separate containers

One process per container

Containers must be:

Stateless

Configured via environment variables

Database remains Neon (external managed PostgreSQL)

☸ Kubernetes Rules

Minikube is the only cluster

Namespace-based isolation is required

Use Kubernetes-native resources:

Deployment

Service

ConfigMap

Secret

No hardcoded credentials inside YAML

📦 Helm Rules

Helm is mandatory

No raw kubectl apply -f for final deployment

Each service must be templated:

frontend

backend

Values must be configurable via values.yaml

4️⃣ AI-Assisted DevOps Governance
🤖 Docker AI (Gordon)

Use Gordon only if available

Gordon is advisory, not authoritative

Generated commands must be reviewed before execution

Fallback:

Standard Docker CLI

Claude Code generated Docker commands

🤖 kubectl-ai & kagent

AI tools may be used to:

Generate manifests

Debug pod failures

Analyze cluster health

AI must not auto-apply destructive actions

Human confirmation is mandatory for:

Deletions

Scaling down to zero

Namespace removal

5️⃣ Environment & Secrets Policy
🔐 Secrets

No secrets in Git

Use:

Kubernetes Secrets

.env → converted to Secrets

Secrets include:

DATABASE_URL

JWT_SECRET

BETTER_AUTH_SECRET

OPENAI keys

🌱 Configuration

Environment-specific values go into:

Helm values.yaml

No hardcoded localhost URLs inside containers

6️⃣ Validation & Acceptance Rules

Deployment is considered successful only if:

✅ Minikube cluster runs without errors
✅ Frontend accessible via NodePort / Ingress
✅ Backend API reachable from frontend
✅ Database connection works (Neon)
✅ Pods are healthy (no CrashLoopBackOff)
✅ Helm install / upgrade works cleanly
✅ App survives pod restarts

7️⃣ Out-of-Scope (Explicitly Forbidden)

🚫 Cloud providers (AWS/GCP/Azure)
🚫 CI/CD pipelines
🚫 Production hardening
🚫 Autoscaling (HPA)
🚫 Service Mesh
🚫 Observability stacks (Prometheus, Grafana)

8️⃣ Failure Handling Rule

If:

Docker AI is unavailable

kubectl-ai fails

kagent not supported

Then:
➡️ Proceed manually
➡️ Use Docker CLI + Helm + kubectl
➡️ Do NOT block the phase

9️⃣ Governance Rule (Spec Discipline)

This phase MUST strictly follow:

sp.constitution
→ sp.specify
→ sp.plan
→ sp.tasks
→ sp.implement


Skipping steps invalidates the phase. and only work in phase-4 never create spec and history outside the phase-4 forlder
```

## Response snapshot

Updated the project constitution to reflect Phase IV requirements for Kubernetes deployment of the Todo + AI Chatbot application. The new constitution enforces the immutable rules specified by the user, including application code freeze, containerization requirements, Kubernetes deployment rules, Helm chart governance, and security policies. The version has been updated from 1.1.0 to 1.2.0 to reflect the addition of Phase IV-specific requirements.

## Outcome

- ✅ Impact: Updated constitution to govern Phase IV Kubernetes deployment activities
- 🧪 Tests: N/A
- 📁 Files: Updated .specify/memory/constitution.md
- 🔁 Next prompts: sp.specify to create Phase IV deployment specification
- 🧠 Reflection: Constitution now properly defines the scope and constraints for Phase IV

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin Phase IV specification with sp.specify
