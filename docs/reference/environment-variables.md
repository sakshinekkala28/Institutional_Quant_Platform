# Environment Variables

The Institutional Quant Platform uses environment variables to configure application behavior, infrastructure integrations, external services, and runtime settings. This document describes the supported environment variables, their purpose, default values, and recommended usage.

---

# Configuration Principles

The platform follows the **Twelve-Factor App** methodology:

- Store configuration in environment variables.
- Never hardcode secrets or credentials.
- Separate development, staging, and production configurations.
- Use `.env` files only for local development.
- Manage production secrets using a secure secrets manager.

---

# Application Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `APP_NAME` | Application name | Institutional Quant Platform | No |
| `APP_ENV` | Runtime environment (`development`, `staging`, `production`) | development | Yes |
| `APP_VERSION` | Application version | 1.0.0 | No |
| `LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | INFO | No |
| `PYTHONPATH` | Python module search path | Project root | No |

---

# API Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `API_HOST` | API host | 0.0.0.0 | No |
| `API_PORT` | API port | 8000 | No |
| `API_WORKERS` | Number of API worker processes | 4 | No |
| `API_PREFIX` | REST API prefix | /api | No |

---

# Database Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `DATABASE_URL` | Database connection string | DuckDB | Yes |
| `DUCKDB_PATH` | Path to DuckDB database | data/database.duckdb | Yes |

---

# Portfolio Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `MAX_POSITIONS` | Maximum portfolio holdings | 100 |
| `MAX_POSITION_WEIGHT` | Maximum position weight | 0.05 |
| `MIN_POSITION_WEIGHT` | Minimum position weight | 0.005 |
| `REBALANCE_FREQUENCY` | Portfolio rebalance schedule | Monthly |

---

# Risk Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `RISK_MODEL` | Active risk model | Historical |
| `VAR_CONFIDENCE_LEVEL` | VaR confidence level | 95 |
| `MAX_PORTFOLIO_VOLATILITY` | Target volatility | 15% |
| `MAX_DRAWDOWN_LIMIT` | Maximum drawdown threshold | 20% |

---

# Market Data

| Variable | Description |
|----------|-------------|
| `MARKET_DATA_PROVIDER` | Primary market data provider |
| `MARKET_DATA_API_KEY` | Provider API key |
| `MARKET_DATA_TIMEOUT` | Request timeout (seconds) |
| `MARKET_DATA_CACHE_TTL` | Cache expiration time |

---

# Authentication

| Variable | Description |
|----------|-------------|
| `JWT_SECRET_KEY` | JWT signing key |
| `JWT_ALGORITHM` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime |

---

# Monitoring

| Variable | Description |
|----------|-------------|
| `PROMETHEUS_ENABLED` | Enable Prometheus metrics |
| `GRAFANA_ENABLED` | Enable Grafana dashboards |
| `METRICS_PORT` | Metrics endpoint port |

---

# Logging

| Variable | Description |
|----------|-------------|
| `LOG_FILE` | Log file location |
| `LOG_FORMAT` | Log output format |
| `LOG_ROTATION_DAYS` | Log retention period |

---

# Docker

| Variable | Description |
|----------|-------------|
| `DOCKER_IMAGE` | Docker image name |
| `DOCKER_TAG` | Docker image tag |

---

# Kubernetes

| Variable | Description |
|----------|-------------|
| `KUBE_NAMESPACE` | Kubernetes namespace |
| `KUBE_CONTEXT` | Kubernetes context |

---

# Terraform

| Variable | Description |
|----------|-------------|
| `TF_VAR_environment` | Deployment environment |
| `TF_VAR_region` | Cloud region |
| `TF_VAR_project_name` | Project name |

---

# Example `.env`

```env
APP_ENV=development
APP_NAME=Institutional Quant Platform
LOG_LEVEL=INFO

DATABASE_URL=data/database.duckdb

API_HOST=0.0.0.0
API_PORT=8000

MAX_POSITIONS=100
MAX_POSITION_WEIGHT=0.05

PROMETHEUS_ENABLED=true

JWT_SECRET_KEY=change-me
```

---

# Security Recommendations

- Never commit `.env` files to version control.
- Rotate secrets regularly.
- Use a dedicated secrets manager in production.
- Grant only the minimum permissions required for each service.
- Validate required environment variables during application startup.

---

# Related Documentation

- Configuration Reference
- Security Guide
- Deployment Guide
- CLI Reference
- Getting Started