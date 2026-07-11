# Alerting

## Institutional Quant Platform

---

# Purpose

The Alerting framework detects operational anomalies and notifies engineers
before service degradation impacts users.

Alerts should be actionable, measurable, and noise-free.

---

# Alert Levels

| Severity | Description |
|-----------|-------------|
| INFO | Informational |
| WARNING | Degraded |
| ERROR | Failure |
| CRITICAL | Immediate action |

---

# Alert Categories

## Infrastructure

- CPU > 90%
- Memory > 90%
- Disk Full

---

## API

- Error Rate > 5%
- Latency > 500ms
- Service Down

---

## Pipeline

- Pipeline Failure
- Retry Limit Exceeded
- Scheduler Failure

---

## Portfolio

- Optimization Failed
- Constraint Violation
- Missing Holdings

---

## Risk

- VaR Limit Breach
- Exposure Limit Breach

---

## Execution

- OMS Failure
- Broker Offline
- Order Rejection Rate

---

# Notification Channels

- Email
- Slack
- Microsoft Teams
- PagerDuty
- Webhooks

---

# Escalation

```text
INFO

↓

WARNING

↓

ERROR

↓

CRITICAL
```

---

# Best Practices

- Eliminate alert fatigue
- Define ownership
- Use runbooks
- Test alerts regularly

---

# Related Documents

- Monitoring Overview
- Metrics
- Logging
- Grafana

---

End of Document