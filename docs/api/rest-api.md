# REST API

## Overview

The Institutional Quant Platform exposes a REST API enabling external systems,
dashboards, schedulers, and research environments to interact with portfolio,
risk, execution, reporting, and monitoring services.

---

# Architecture

```text
Client

↓

API Gateway

↓

Authentication

↓

Router

↓

Business Services

↓

Database

↓

Response
```

---

# Supported Methods

| Method | Purpose |
|----------|----------|
| GET | Retrieve resources |
| POST | Create resources |
| PUT | Update resources |
| PATCH | Partial update |
| DELETE | Remove resource |

---

# Status Codes

| Code | Meaning |
|-------|---------|
|200|Success|
|201|Created|
|202|Accepted|
|400|Bad Request|
|401|Unauthorized|
|403|Forbidden|
|404|Not Found|
|409|Conflict|
|422|Validation Error|
|500|Internal Error|

---

# Pagination

```
?page=1&page_size=100
```

---

# Sorting

```
?sort=market_cap
```

Descending

```
?sort=-market_cap
```

---

# Filtering

```
?sector=IT
```

```
?industry=Banks
```

```
?country=India
```

---

# Versioning

```
/v1/
/v2/
```

---

# Rate Limits

Default

```
1000 requests/hour
```

Enterprise deployments may override limits.

---

# Error Handling

Every response includes

- request_id
- timestamp
- status
- message

to simplify observability and debugging.

---

# Best Practices

- Cache immutable resources.
- Use pagination.
- Handle retries with exponential backoff.
- Use idempotent requests where appropriate.
- Log correlation IDs for distributed tracing.