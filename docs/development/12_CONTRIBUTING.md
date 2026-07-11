# Contributing Guide

> Institutional Quant Platform

---

# Document Information

| Field | Value |
|-------|-------|
| Document | Contributing Guide |
| Version | 1.0.0 |
| Status | Approved |
| Owner | Platform Architecture |
| Classification | Internal |
| Last Updated | YYYY-MM-DD |
| Next Review | Quarterly |

---

# Purpose

This document defines the contribution process for the
Institutional Quant Platform.

It establishes the standards for proposing, implementing,
reviewing, and merging changes into the project.

Every contributor shall follow this guide.

---

# Objectives

This guide standardizes

- Contributor onboarding
- Development workflow
- Coding expectations
- Documentation requirements
- Testing requirements
- Pull Request process
- Code review etiquette
- Repository maintenance

---

# Guiding Principles

Every contribution should

- Improve the platform
- Follow the architecture
- Maintain quality
- Include documentation
- Include tests
- Respect coding standards

The project values maintainability over speed.

---

# Before You Start

Before contributing

- Read the Architecture Handbook
- Read the Development Handbook
- Understand repository structure
- Review open issues
- Confirm the proposed change aligns with the roadmap

---

# Development Environment

Required software

- Python 3.12+
- Git
- Docker (optional)
- VS Code or equivalent IDE

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Repository Setup

Clone the repository

```bash
git clone <repository-url>

cd Institutional_Quant_Platform
```

Create a feature branch

```bash
git checkout -b feature/my-feature
```

---

# Contribution Workflow

```
Issue

↓

Discussion

↓

Feature Branch

↓

Implementation

↓

Tests

↓

Documentation

↓

Pull Request

↓

Code Review

↓

Approval

↓

Merge
```

---

# Branch Naming

Use descriptive names.

Examples

```
feature/risk-engine

feature/portfolio-optimizer

bugfix/repository-validation

hotfix/security-patch
```

Avoid generic names.

```
test

update

new

changes
```

---

# Coding Requirements

All contributions shall

- Follow coding standards
- Include type hints
- Include docstrings
- Pass formatting
- Pass linting
- Pass tests

Reference

```
01_CODING_STANDARDS.md
```

---

# Architecture Compliance

Contributions shall

- Respect layer boundaries
- Use repositories for persistence
- Keep engines independent
- Keep pipelines lightweight
- Avoid circular dependencies

Architecture changes require an approved ADR.

---

# Testing Requirements

Every contribution shall include

- Unit tests
- Integration tests (where applicable)

New features without tests shall not be merged.

---

# Documentation Requirements

Documentation shall be updated whenever changes affect

- Architecture
- APIs
- Pipelines
- Engines
- Configuration
- User workflows

Required updates may include

- README
- Development Guides
- Architecture Documents
- Changelog

---

# Pull Requests

Every Pull Request shall include

- Purpose
- Summary of changes
- Testing performed
- Documentation updates
- Breaking changes
- Related issue

---

# Code Review

All Pull Requests require

- Automated checks
- Reviewer approval
- Documentation review
- Successful CI

No contributor may merge unreviewed production code.

---

# Commit Messages

Use clear, imperative messages.

Good examples

```
Add factor correlation engine

Fix portfolio validation

Improve execution pipeline logging

Refactor repository abstraction
```

Avoid

```
update

fix

misc

changes
```

---

# Issue Reporting

When reporting issues include

- Description
- Expected behavior
- Actual behavior
- Steps to reproduce
- Environment
- Logs (if applicable)

---

# Feature Requests

Feature requests should include

- Business motivation
- Proposed solution
- Alternatives considered
- Expected impact

---

# Communication

Contributors should

- Be respectful
- Be constructive
- Focus on technical discussion
- Provide evidence when proposing changes

---

# Quality Expectations

Every contribution should

- Improve readability
- Maintain consistency
- Preserve architecture
- Reduce technical debt where practical

---

# Contributor Responsibilities

Contributors are responsible for

- Code quality
- Testing
- Documentation
- Security
- Performance
- Maintainability

---

# Maintainer Responsibilities

Maintainers are responsible for

- Reviewing Pull Requests
- Protecting architecture
- Managing releases
- Updating documentation
- Resolving conflicts
- Guiding contributors

---

# Code of Conduct

Contributors shall

- Be professional
- Be respectful
- Welcome constructive feedback
- Encourage collaboration
- Respect differing technical opinions

Harassment, discrimination, or disruptive behavior will not be tolerated.

---

# License

By contributing, you agree that your contributions will be
distributed under the project's license.

---

# Best Practices

- Keep Pull Requests focused
- Write readable code
- Update documentation
- Respond to review comments promptly
- Rebase regularly
- Keep feature branches short-lived

---

# Anti-Patterns

Avoid

- Large unrelated Pull Requests
- Direct commits to protected branches
- Skipping tests
- Skipping documentation
- Introducing architectural violations
- Ignoring review feedback

---

# Related Documents

- README.md
- 00_DEVELOPMENT_GUIDE.md
- 01_CODING_STANDARDS.md
- 09_CODE_REVIEW.md
- 10_GIT_WORKFLOW.md
- 11_RELEASE_PROCESS.md
- ../GOVERNANCE.md

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | YYYY-MM-DD | Initial contributing guide |

---

**End of Document**