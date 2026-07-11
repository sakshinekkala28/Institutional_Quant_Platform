# Git Workflow Guide

> Institutional Quant Platform

---

# Document Information

| Field | Value |
|-------|-------|
| Document | Git Workflow Guide |
| Version | 1.0.0 |
| Status | Approved |
| Owner | Platform Architecture |
| Classification | Internal |
| Last Updated | YYYY-MM-DD |
| Next Review | Quarterly |

---

# Purpose

This document defines the Git workflow for the Institutional
Quant Platform.

The objective is to ensure

- Clean history
- Predictable releases
- Safe collaboration
- Controlled deployments
- Easy rollback
- High code quality

Every contributor shall follow this workflow.

---

# Objectives

The workflow standardizes

- Branch strategy
- Commit messages
- Pull Requests
- Merge strategy
- Releases
- Tags
- Repository maintenance

---

# Branch Strategy

The repository follows a simplified GitFlow model.

```
main

│

├── develop

│      │

│      ├── feature/*

│      ├── bugfix/*

│      ├── hotfix/*

│      └── release/*
```

---

# Main Branch

Purpose

Production-ready code.

Rules

- Protected
- No direct commits
- Pull Request required
- Passing CI required
- Approved review required

---

# Develop Branch

Purpose

Integration branch.

Rules

- Feature branches merge here
- Continuous testing
- Nightly validation

---

# Feature Branches

Naming

```
feature/

feature/risk-engine

feature/portfolio-optimizer

feature/master-orchestrator
```

Purpose

Develop one feature only.

---

# Bug Fix Branches

Naming

```
bugfix/

bugfix/security-master

bugfix/risk-calculation
```

Purpose

Correct defects.

---

# Hotfix Branches

Naming

```
hotfix/

hotfix/api-auth

hotfix/pipeline-crash
```

Purpose

Critical production fixes.

Hotfixes branch from

```
main
```

---

# Release Branches

Naming

```
release/1.0.0

release/1.1.0
```

Purpose

Release stabilization.

Activities

- Testing
- Documentation
- Version updates
- Changelog
- Final validation

---

# Commit Messages

Use imperative verbs.

Preferred format

```
Add portfolio optimizer

Fix risk engine validation

Improve pipeline logging

Refactor repository layer
```

Avoid

```
fixed stuff

update

changes

misc
```

---

# Commit Guidelines

Each commit should

- Solve one problem
- Be independently understandable
- Compile successfully
- Pass tests

Avoid mixing unrelated changes.

---

# Pull Requests

Every Pull Request shall include

- Summary
- Motivation
- Related Issue
- Testing Evidence
- Documentation Updates
- Breaking Changes

---

# Pull Request Workflow

```
Feature Branch

↓

Push

↓

Open Pull Request

↓

CI Validation

↓

Code Review

↓

Approval

↓

Merge
```

---

# Merge Strategy

Preferred

```
Squash and Merge
```

Advantages

- Cleaner history
- One commit per feature
- Easier rollback

Alternative

```
Rebase and Merge
```

Avoid

```
Merge Commit
```

unless preserving branch history is required.

---

# Protected Branches

Protect

- main
- develop

Rules

- No force push
- No direct commits
- Required reviews
- Required status checks

---

# Version Tags

Use Semantic Versioning.

Examples

```
v1.0.0

v1.1.0

v1.2.3
```

Tags are created only after successful production releases.

---

# Release Workflow

```
develop

↓

release/1.0.0

↓

Testing

↓

Approval

↓

main

↓

Tag

↓

Deploy
```

---

# Hotfix Workflow

```
main

↓

hotfix/

↓

Review

↓

main

↓

develop
```

Hotfixes must also be merged back into `develop`.

---

# Conflict Resolution

When conflicts occur

1. Pull latest changes
2. Rebase or merge locally
3. Resolve conflicts
4. Re-run tests
5. Push updated branch

Never resolve conflicts without understanding the affected code.

---

# Repository Maintenance

Regularly

- Remove stale branches
- Update dependencies
- Archive obsolete releases
- Clean tags when appropriate

---

# Git Hooks

Recommended pre-commit hooks

- Black
- Ruff
- isort
- mypy
- pytest

Prevent commits when checks fail.

---

# Continuous Integration

Every push shall trigger

- Formatting
- Linting
- Static Typing
- Unit Tests
- Integration Tests
- Security Scan

---

# Continuous Delivery

Release pipeline

```
Git Push

↓

CI

↓

Tests

↓

Review

↓

Merge

↓

Release

↓

Deployment
```

---

# Rollback Strategy

Every production release must support rollback.

Rollback requires

- Tagged release
- Deployment artifacts
- Migration rollback (if applicable)

---

# Best Practices

- Keep branches short-lived
- Rebase frequently
- Commit often
- Write meaningful commit messages
- Delete merged branches
- Keep history clean

---

# Anti-Patterns

Avoid

- Direct commits to main
- Force pushing protected branches
- Large unrelated Pull Requests
- Unreviewed merges
- Committing generated files
- Committing secrets

---

# Code Review Integration

Git workflow integrates with

- Code Review Guide
- Testing Guide
- Release Process
- Governance

No Pull Request shall bypass required approvals.

---

# Related Documents

- 09_CODE_REVIEW.md
- 11_RELEASE_PROCESS.md
- 12_CONTRIBUTING.md
- ../GOVERNANCE.md
- ../VERSIONING.md

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | YYYY-MM-DD | Initial Git workflow guide |

---

**End of Document**