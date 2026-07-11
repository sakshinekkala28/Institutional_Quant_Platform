# Configuration Guide

## Institutional Quant Platform

---

# Purpose

This guide explains how to configure the Institutional Quant Platform across development, testing, staging, and production environments.

Configuration is designed to be:

- Environment specific
- Secure
- Version controlled where appropriate
- Easily extensible
- Cloud native

---

# Configuration Hierarchy

Configuration is loaded in the following order.

```text
Default Values
        │
        ▼
Configuration Files
        │
        ▼
Environment Variables
        │
        ▼
Runtime Overrides
```

Environment variables always take precedence.

---

# Configuration Sources

The platform supports configuration from:

- Environment Variables
- `.env`
- YAML
- TOML
- JSON
- Kubernetes ConfigMaps
- Kubernetes Secrets

---

# Environment Variables

Create a local environment file.

```text
.env
```

Example

```text
APP_ENV=development

APP_NAME=Institutional Quant Platform

APP_VERSION=1.0.0

LOG_LEVEL=INFO

TIMEZONE=Asia/Kolkata
```

---

# Application Settings

| Variable | Description | Default |
|-----------|-------------|----------|
| APP_ENV | Application environment | development |
| APP_NAME | Application name | Institutional Quant Platform |
| APP_VERSION | Version | 1.0.0 |
| LOG_LEVEL | Logging level | INFO |
| TIMEZONE | Default timezone | Asia/Kolkata |

---

# Data Configuration

```text
DATA_DIRECTORY=data

CACHE_DIRECTORY=cache

REPORT_DIRECTORY=reports

TEMP_DIRECTORY=tmp
```

---

# Database Configuration

DuckDB

```text
DUCKDB_PATH=data/institutional_quant.db
```

SQLite (optional)

```text
SQLITE_PATH=data/database.sqlite
```

Future PostgreSQL example

```text
POSTGRES_HOST=

POSTGRES_PORT=

POSTGRES_DATABASE=

POSTGRES_USERNAME=

POSTGRES_PASSWORD=
```

---

# API Configuration

```text
API_HOST=0.0.0.0

API_PORT=8000

API_WORKERS=4
```

---

# Dashboard Configuration

```text
STREAMLIT_PORT=8501

STREAMLIT_HOST=0.0.0.0
```

---

# Market Data

Example

```text
YFINANCE_ENABLED=true

CACHE_MARKET_DATA=true
```

Future providers

```text
NSE_API_KEY=

TWELVEDATA_API_KEY=

POLYGON_API_KEY=
```

---

# Logging

Example

```text
LOG_LEVEL=INFO

LOG_FORMAT=json

LOG_DIRECTORY=logs
```

Supported levels

- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

---

# Security

Never store secrets in Git.

Store secrets in

- GitHub Secrets
- Kubernetes Secrets
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager

Examples

```text
API_KEY=

JWT_SECRET=

DATABASE_PASSWORD=
```

---

# Docker Configuration

Environment variables can be passed

```bash
docker run \
-e APP_ENV=production \
-e LOG_LEVEL=INFO \
institutional-quant-platform
```

---

# Kubernetes Configuration

Configuration should be split between

ConfigMap

```text
Application Configuration
```

Secret

```text
Passwords

API Keys

Tokens
```

---

# Terraform Variables

Infrastructure values should be defined in

```text
terraform.tfvars
```

Example

```text
environment="development"

region="ap-south-1"
```

---

# Feature Flags

Feature flags enable incremental rollout.

Example

```text
ENABLE_ALPHA_ENGINE=true

ENABLE_RISK_ENGINE=true

ENABLE_EXECUTION_ENGINE=true

ENABLE_STREAMING=false
```

---

# Performance Configuration

Example

```text
MAX_WORKERS=8

BATCH_SIZE=500

CACHE_ENABLED=true
```

---

# Monitoring Configuration

```text
METRICS_ENABLED=true

PROMETHEUS_ENABLED=true

HEALTHCHECK_ENABLED=true
```

---

# File Structure

```text
.env

.env.example

pyproject.toml

mkdocs.yml

ruff.toml

mypy.ini

bandit.yaml

checkov.yaml
```

---

# Best Practices

- Never commit secrets.
- Keep `.env.example` up to date.
- Validate configuration at startup.
- Use environment variables for deployment-specific values.
- Document new configuration options.

---

# Validation

Before running the application

```bash
make ci
```

Verify

- Configuration files
- Environment variables
- Dependencies
- Database path
- Logging configuration

---

# Troubleshooting

Missing environment variable

```text
Environment variable not found
```

Solution

```bash
cp .env.example .env
```

Database connection

Verify

```text
DUCKDB_PATH
```

API

Verify

```text
API_PORT
```

Dashboard

Verify

```text
STREAMLIT_PORT
```

---

# Related Documents

- Installation Guide
- Quick Start
- Development Guide
- Deployment Guide
- Operations Guide

---

End of Document