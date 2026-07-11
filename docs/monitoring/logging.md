# Logging

## Institutional Quant Platform

---

# Purpose

The Logging framework captures structured operational events for debugging,
auditing, compliance, and observability.

All production logs must be structured JSON.

---

# Logging Levels

| Level | Usage |
|--------|-------|
| DEBUG | Development |
| INFO | Normal operation |
| WARNING | Recoverable issue |
| ERROR | Failed operation |
| CRITICAL | Service unavailable |

---

# Log Structure

Example

```json
{
  "timestamp":"2026-01-01T09:15:00Z",
  "level":"INFO",
  "service":"portfolio",
  "operation":"rebalance",
  "request_id":"abc123",
  "duration_ms":245
}
```

---

# Correlation IDs

Every request must include

```text
request_id

trace_id

span_id
```

---

# Log Categories

- Application
- Audit
- Security
- Performance
- Business
- Infrastructure

---

# Storage

Recommended

- Loki
- Elasticsearch
- Cloud Logging

---

# Retention

| Type | Retention |
|-------|-----------|
| Application | 90 Days |
| Audit | 7 Years |
| Security | 1 Year |

---

# Best Practices

- Never log passwords
- Never log API secrets
- Mask sensitive data
- Use structured logging
- Include timestamps

---

End of Document