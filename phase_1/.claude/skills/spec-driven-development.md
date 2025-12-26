# Skill: Spec-Driven Development

## Identifier
`spec-driven-development`

## Purpose
Provides patterns for implementing features following the Spec-Driven Development (SDD) methodology. This skill enables agents to work within the Spec-Kit Plus framework, ensuring all implementations are traceable to specifications and follow the defined workflow.

## Scope
- Specification interpretation
- Plan-to-implementation mapping
- Task execution workflow
- Artifact creation and management
- Quality gate compliance

## Capabilities

### Specification Compliance
- Read and interpret feature specifications (spec.md)
- Extract functional requirements for implementation
- Identify acceptance criteria for testing
- Understand scope boundaries and constraints
- Trace code changes to requirements

### Workflow Adherence
- Follow the SDD workflow: Spec -> Plan -> Tasks -> Implementation -> Review
- Wait for spec approval before planning
- Wait for plan approval before task breakdown
- Execute tasks in defined order
- Complete review before marking features done

### Artifact Awareness
- Understand spec.md structure and content
- Interpret plan.md for architectural guidance
- Follow tasks.md for implementation sequence
- Reference ADRs for architectural decisions
- Create PHRs for traceability

### Task Execution
- Execute one task at a time
- Implement exactly what the task specifies
- Test against task acceptance criteria
- Mark tasks complete when done
- Report blockers immediately

### Quality Gates
- Verify implementation matches spec
- Ensure tests cover acceptance criteria
- Follow code standards from constitution
- Complete review checklist items
- Pass all quality checks before proceeding

### Traceability
- Reference spec requirements in code comments when not self-evident
- Link implementations to task IDs
- Document deviations with rationale
- Maintain clear audit trail

## Responsibilities
- Ensure all code traces back to specifications
- Follow the established development workflow
- Maintain consistency with project artifacts
- Report issues and blockers proactively

## Usage Intent
Apply this skill when working on any feature within a Spec-Kit Plus project. This skill ensures implementations are aligned with specifications and follow the defined process.

## Dependencies
- Spec-Kit Plus templates and workflows
- Feature spec.md documents
- plan.md and tasks.md artifacts
- Constitution.md for project standards

## Anti-Patterns to Avoid
- Implementing without reading the spec
- Skipping workflow stages
- Adding features not in the spec
- Ignoring acceptance criteria
- Making architectural decisions without ADR
- Proceeding without required approvals

## Quality Criteria
- Implementation matches specification exactly
- All acceptance criteria are satisfied
- Tasks are completed in order
- Quality gates are passed
- Traceability is maintained
