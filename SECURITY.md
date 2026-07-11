# Security Policy

## Institutional Quant Platform

Thank you for helping improve the security of the Institutional Quant Platform.

We take security seriously and appreciate responsible disclosure of vulnerabilities.

---

# Supported Versions

The following versions currently receive security updates.

| Version | Supported |
|----------|-----------|
| Latest Release | ✅ |
| Previous Minor Release | ✅ |
| Older Releases | ❌ |

---

# Reporting a Vulnerability

## Do NOT open a public GitHub Issue for confidential vulnerabilities.

Instead, report security issues privately.

### Preferred Method

Use GitHub Security Advisories if enabled.

OR

Contact:

**Maintainer**

Pavan Sai Nekkala

Email:

sakshinekkala28@gmail.com

---

# What to Include

Please include:

- Vulnerability description
- Affected component
- Severity
- Steps to reproduce
- Proof of Concept (if available)
- Impact assessment
- Suggested mitigation
- Environment
- Version
- Supporting logs or screenshots

Please remove any credentials, secrets, API keys, or personal information before submitting.

---

# Response Targets

| Activity | Target |
|----------|---------|
| Initial acknowledgement | 3 business days |
| Initial assessment | 7 business days |
| Status update | Weekly |
| Resolution target | Depends on severity |

---

# Severity Classification

## Critical

Remote Code Execution

Authentication bypass

Privilege escalation

Sensitive data exposure

Supply chain compromise

---

## High

Authorization issues

Container escape

Kubernetes privilege issues

Infrastructure compromise

Secrets exposure

---

## Medium

Denial of Service

Dependency vulnerabilities

Misconfigurations

Information disclosure

---

## Low

Documentation security issues

Minor hardening improvements

Non-sensitive information leakage

---

# Coordinated Disclosure

Please allow reasonable time for investigation and remediation before publicly disclosing vulnerabilities.

We aim to coordinate disclosure with reporters whenever possible.

---

# Security Best Practices

Contributors should:

- Never commit secrets
- Rotate credentials regularly
- Use least-privilege access
- Validate all external inputs
- Keep dependencies updated
- Review pull requests carefully
- Enable multi-factor authentication
- Follow secure coding practices

---

# Automated Security

This repository uses automated security scanning including:

- CodeQL
- Dependabot
- Trivy
- Semgrep
- Checkov
- tfsec
- Gitleaks
- Bandit
- pip-audit
- SBOM Generation
- Cosign Signing

---

# Third-Party Dependencies

Dependencies are monitored through:

- GitHub Dependabot
- GitHub Security Advisories
- Automated CI/CD security workflows

---

# Infrastructure Security

Infrastructure is continuously validated using:

- Terraform validation
- Kubernetes validation
- Helm linting
- Docker image scanning
- Infrastructure-as-Code scanning

---

# Supply Chain Security

This project generates:

- SPDX SBOM
- CycloneDX SBOM

Container images and release artifacts are signed using Cosign where applicable.

---

# Scope

This policy applies to:

- Source code
- APIs
- Analytics
- Dashboard
- Infrastructure
- Kubernetes
- Helm
- Terraform
- Docker
- GitHub Actions
- Documentation

---

# Security Hall of Fame

We appreciate responsible disclosure.

Contributors who responsibly report valid security issues may be acknowledged in future releases, subject to their consent.

---

# License

This security policy applies to all supported versions of the Institutional Quant Platform.