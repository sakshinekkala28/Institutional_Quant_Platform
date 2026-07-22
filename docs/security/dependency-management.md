# Dependency Management

The Institutional Quant Platform relies on carefully managed third-party libraries and frameworks. This document describes the project's approach to dependency selection, maintenance, vulnerability management, and update strategy.

---

# Objectives

Dependency management aims to:

- Maintain a secure software supply chain
- Reduce operational risk
- Ensure reproducible builds
- Minimize dependency conflicts
- Keep libraries up to date
- Monitor known vulnerabilities
- Support long-term maintainability

---

# Dependency Categories

Dependencies are grouped into the following categories:

| Category | Examples |
|----------|----------|
| Core Runtime | Python, FastAPI, Streamlit |
| Analytics | NumPy, Pandas, Polars, SciPy |
| Machine Learning | Scikit-learn |
| Visualization | Plotly, Matplotlib |
| Database | DuckDB |
| Infrastructure | Docker, Terraform, Helm |
| Testing | Pytest |
| Documentation | MkDocs Material |
| Development | Ruff, MyPy, Pre-commit |

---

# Dependency Sources

Dependencies should be obtained only from trusted package repositories.

Recommended sources include:

- Python Package Index (PyPI)
- Official vendor repositories
- Verified GitHub releases
- Organization-approved package registries

Avoid using unverified or unofficial package sources.

---

# Version Management

Recommended practices:

- Pin production dependency versions.
- Review major version upgrades before adoption.
- Keep development dependencies compatible with runtime dependencies.
- Remove unused dependencies regularly.

Example:

```text
fastapi==0.116.0
pandas==2.3.1
numpy==2.3.1
duckdb==1.3.2
```

---

# Dependency Updates

Dependencies should be reviewed periodically.

Recommended cadence:

| Dependency Type | Frequency |
|----------------|-----------|
| Security Updates | Immediately |
| Patch Releases | Monthly |
| Minor Releases | Quarterly |
| Major Releases | After compatibility review |

---

# Vulnerability Monitoring

Third-party dependencies should be continuously monitored for known vulnerabilities.

Recommended tools include:

- GitHub Dependabot
- GitHub Security Advisories
- pip-audit
- Trivy
- OSV Scanner

Critical vulnerabilities should be addressed as soon as practical.

---

# Automated Scanning

Dependency scanning should be integrated into CI/CD pipelines.

Example workflow:

```text
Source Code
      │
      ▼
Install Dependencies
      │
      ▼
Dependency Scan
      │
      ▼
Security Report
      │
      ▼
Build Approval
      │
      ▼
Deployment
```

---

# Software Bill of Materials (SBOM)

The platform supports generation of Software Bills of Materials (SBOMs) to improve software supply chain visibility.

Recommended formats:

- SPDX
- CycloneDX

SBOMs should be generated for production releases where applicable.

---

# License Compliance

Before introducing a new dependency:

- Review the software license.
- Confirm compatibility with the project's license.
- Verify redistribution requirements.
- Ensure compliance with organizational policies.

---

# Removing Dependencies

Dependencies should be removed when:

- No longer used.
- Superseded by maintained alternatives.
- Security risks outweigh benefits.
- Project maintenance has ceased.

Unused dependencies increase maintenance burden and potential attack surface.

---

# Best Practices

- Prefer actively maintained libraries.
- Pin production versions.
- Regularly review dependency health.
- Automate vulnerability scanning.
- Keep transitive dependencies under review.
- Document new dependency introductions.
- Avoid unnecessary package proliferation.

---

# Related Documentation

- Security Overview
- Vulnerability Management
- Secure Development
- Secrets Management
- Configuration Reference
- Security Policy (`SECURITY.md`)