# Security Policy

## Institutional Quant Platform

Thank you for helping improve the security of the **Institutional Quant Platform**.

Security is a core priority for this project. We greatly appreciate responsible disclosure of vulnerabilities and collaboration from the security community to help protect users and contributors.

---

# Security Scope

This policy applies to all officially maintained components of the Institutional Quant Platform, including:

- Source Code
- REST APIs
- Streamlit Dashboard
- Analytics Engines
- Alpha Models
- Portfolio Construction
- Risk Analytics
- Execution Engine
- Monitoring & Telemetry
- Docker Images
- Helm Charts
- Kubernetes Manifests
- Terraform Modules
- GitHub Actions Workflows
- Documentation

---

# Supported Versions

The following versions currently receive security updates.

| Version | Supported |
|----------|:---------:|
| Latest Release | ✅ |
| Previous Minor Release | ✅ |
| Older Releases | ❌ |

---

# Reporting a Vulnerability

**Please do not open a public GitHub Issue for confidential security vulnerabilities.**

Instead, report security issues privately.

## Preferred Method

Use **GitHub Security Advisories** if they are enabled for this repository.

Alternatively, contact the maintainer directly.

### Maintainer

**Pavan Sai Nekkala**

Email:

**sakshinekkala28@gmail.com**

---

# What to Include

To help us investigate efficiently, please include:

- Vulnerability description
- Affected component
- Severity assessment
- Steps to reproduce
- Proof of Concept (if available)
- Potential impact
- Suggested mitigation
- Environment details
- Platform version
- Relevant logs or screenshots

Please remove any credentials, secrets, API keys, tokens, or personal information before submitting your report.

---

# Secure Communication

If your report contains sensitive information, please encrypt communications whenever possible.

Avoid sending:

- Private keys
- API tokens
- Customer data
- Production credentials
- Personally identifiable information (PII)

through unencrypted channels.

---

# Response Targets

| Activity | Target |
|----------|---------|
| Initial acknowledgement | Within 3 business days |
| Initial assessment | Within 7 business days |
| Status updates | Weekly |
| Resolution target | Based on severity |

These targets are best-effort and may vary depending on the complexity of the issue.

---

# Severity Assessment

Severity is evaluated using the **Common Vulnerability Scoring System (CVSS)** together with practical impact on:

- Confidentiality
- Integrity
- Availability

---

# Severity Classification

## Critical

Examples include:

- Remote Code Execution (RCE)
- Authentication bypass
- Privilege escalation
- Sensitive data exposure
- Supply chain compromise

---

## High

Examples include:

- Authorization bypass
- Container escape
- Kubernetes privilege escalation
- Infrastructure compromise
- Secret exposure

---

## Medium

Examples include:

- Denial of Service (DoS)
- Dependency vulnerabilities
- Infrastructure misconfigurations
- Information disclosure

---

## Low

Examples include:

- Documentation-related security issues
- Minor hardening improvements
- Non-sensitive information leakage

---

# Out of Scope

The following are generally considered out of scope unless they result in significant security impact:

- Typographical errors
- Missing security headers on localhost
- Self-XSS
- Denial-of-service through unrealistic traffic volumes
- Social engineering attacks
- Vulnerabilities affecting unsupported versions

---

# Coordinated Disclosure

Please allow reasonable time for investigation, remediation, and validation before publicly disclosing vulnerabilities.

Whenever possible, we will coordinate disclosure with the reporter.

---

# Security Objectives

The platform is designed around the following principles:

- Confidentiality
- Integrity
- Availability
- Least Privilege
- Defense in Depth
- Zero Trust Principles
- Supply Chain Security
- Secure by Default

---

# Security Best Practices

Contributors are expected to:

- Never commit secrets or credentials
- Rotate credentials regularly
- Follow least-privilege access principles
- Validate all external inputs
- Keep dependencies up to date
- Review pull requests carefully
- Enable multi-factor authentication
- Follow secure coding practices

---

# Secure Development Lifecycle

Security is integrated throughout the development lifecycle using:

- Static Application Security Testing (SAST)
- Dependency Scanning
- Secret Scanning
- Infrastructure-as-Code Scanning
- Container Image Scanning
- Continuous Security Monitoring

---

# Automated Security

This repository integrates automated security tooling including:

- CodeQL
- Dependabot
- Trivy
- Semgrep
- Checkov
- tfsec
- Gitleaks
- Bandit
- pip-audit
- Software Bill of Materials (SBOM) generation
- Cosign artifact signing

---

# Third-Party Dependencies

Dependencies are continuously monitored using:

- GitHub Dependabot
- GitHub Security Advisories
- Automated CI/CD security workflows

Security updates are applied whenever practical.

---

# Infrastructure Security

Infrastructure is continuously validated using:

- Terraform Validation
- Kubernetes Validation
- Helm Linting
- Docker Image Scanning
- Infrastructure-as-Code Security Scanning

---

# Supply Chain Security

The project supports modern software supply chain practices including:

- SPDX SBOM
- CycloneDX SBOM
- Signed container images
- Signed release artifacts using Cosign (where applicable)

---

# Compliance

Security practices are designed to align with recognized industry guidance, including:

- OWASP Top 10
- OWASP ASVS
- CIS Benchmarks
- NIST Secure Software Development Framework (SSDF)

---

# Incident Response

Confirmed vulnerabilities follow an incident response process consisting of:

1. Triage
2. Risk Assessment
3. Containment
4. Remediation
5. Validation
6. Coordinated Disclosure
7. Post-Incident Review

---

# Scope

This policy applies to:

- Source Code
- APIs
- Analytics
- Portfolio Construction
- Risk Engine
- Execution Engine
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

We sincerely appreciate responsible disclosure.

Researchers who responsibly report valid security vulnerabilities may be acknowledged in future releases, subject to their consent.

---

# License

This security policy applies to all supported versions of the **Institutional Quant Platform** and may be updated as the project evolves.