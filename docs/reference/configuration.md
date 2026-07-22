# Configuration Reference

The Institutional Quant Platform is designed to be configurable, reproducible, and environment-independent. This document describes the primary configuration areas, recommended practices, and configuration hierarchy.

---

# Configuration Hierarchy

Configuration values are resolved in the following order (highest precedence first):

1. Command-line arguments
2. Environment variables
3. Environment-specific configuration files
4. Project defaults

This approach enables consistent deployments across development, staging, and production environments.

---

# Configuration Categories

The platform configuration is organized into the following areas:

| Category | Purpose |
|----------|---------|
| Application | Runtime behavior and metadata |
| Analytics | Signal generation and factor models |
| Portfolio | Portfolio construction and optimization |
| Risk | Risk models and limits |
| Execution | Trade generation and execution parameters |
| Data | Market data sources and storage |
| API | REST API configuration |
| Dashboard | Streamlit application settings |
| Logging | Logging and monitoring |
| Infrastructure | Docker, Kubernetes, and Terraform |

---

# Application Configuration

| Setting | Description | Example |
|----------|-------------|---------|
| Environment | Runtime environment | `development` |
| Version | Platform version | `1.0.0` |
| Log Level | Logging verbosity | `INFO` |
| Time Zone | Default timezone | `UTC` |

---

# Data Configuration

Typical configuration includes:

- Market data provider
- Data storage location
- Cache directory
- Refresh interval
- Historical data window
- Retry policy
- Request timeout

Example:

```yaml
data:
  provider: local
  cache_enabled: true
  refresh_interval: daily
```

---

# Analytics Configuration

Analytics settings determine how signals and factors are generated.

Typical parameters include:

- Universe selection
- Factor normalization
- Ranking methodology
- Signal thresholds
- Market regime detection
- Missing data handling

Example:

```yaml
analytics:
  universe: nse500
  ranking: composite
  normalize: true
```

---

# Portfolio Configuration

Portfolio settings control construction and optimization.

Common options include:

- Optimization method
- Target holdings
- Maximum position weight
- Minimum position weight
- Sector constraints
- Turnover limits
- Rebalancing frequency

Example:

```yaml
portfolio:
  optimizer: risk_parity
  holdings: 100
  rebalance: monthly
```

---

# Risk Configuration

Risk configuration defines portfolio constraints and monitoring rules.

Typical settings include:

- Value at Risk confidence level
- Maximum drawdown limit
- Target volatility
- Position concentration limits
- Sector exposure limits
- Tracking error threshold

Example:

```yaml
risk:
  var_confidence: 0.95
  max_drawdown: 0.20
```

---

# Execution Configuration

Execution settings influence trade generation and transaction cost modelling.

Typical configuration:

- Slippage model
- Commission model
- Execution delay
- Order size limits
- Liquidity thresholds

Example:

```yaml
execution:
  slippage: fixed
  commission: broker
```

---

# API Configuration

Typical REST API settings include:

- Host
- Port
- Worker count
- CORS origins
- Authentication
- Rate limiting

Example:

```yaml
api:
  host: 0.0.0.0
  port: 8000
```

---

# Dashboard Configuration

Dashboard options include:

- Theme
- Refresh interval
- Default portfolio
- Chart preferences
- Export formats

---

# Logging Configuration

Logging settings may include:

- Log level
- Output format
- File location
- Rotation policy
- Retention period

Example:

```yaml
logging:
  level: INFO
  rotation: daily
```

---

# Environment Profiles

The platform supports separate configuration for multiple environments.

| Environment | Purpose |
|-------------|---------|
| Development | Local development |
| Staging | Pre-production validation |
| Production | Live deployment |

Each environment should maintain independent:

- Configuration
- Secrets
- Database connections
- API credentials

---

# Configuration Validation

At application startup, configuration should be validated to ensure:

- Required values are present.
- Types are correct.
- Paths exist.
- Numeric ranges are valid.
- Unsupported options are rejected.

Validation failures should prevent the application from starting.

---

# Best Practices

- Keep configuration outside source code.
- Use environment variables for secrets.
- Version-control non-sensitive configuration.
- Separate configuration by environment.
- Validate configuration during startup.
- Document new configuration options.
- Use sensible defaults where appropriate.

---

# Related Documentation

- Environment Variables
- CLI Reference
- Getting Started
- Security Guide
- Deployment Guide
- Infrastructure Documentation