# Authentication

## Overview

The Institutional Quant Platform supports multiple authentication mechanisms
depending on deployment mode.

| Environment | Authentication |
|-------------|----------------|
| Local Development | Disabled / Token |
| Staging | OAuth2 |
| Production | OAuth2 + JWT |
| Enterprise | SSO (SAML / OIDC) |

---

# Authentication Flow

```text
Client

↓

Identity Provider

↓

JWT Token

↓

API Gateway

↓

Authorization Middleware

↓

REST Endpoint
```

---

# OAuth2

Supported Grant Types

- Authorization Code
- Client Credentials
- Refresh Token

---

# JWT Claims

Example

```json
{
  "sub": "portfolio_manager",
  "role": "PM",
  "exp": 1892039200,
  "permissions": [
    "portfolio.read",
    "portfolio.write",
    "trade.execute"
  ]
}
```

---

# API Keys

Internal services may authenticate using API Keys.

Example

```
X-API-Key:
```

API Keys are encrypted and rotated automatically.

---

# Role Based Access Control

Supported Roles

- Administrator
- CIO
- Portfolio Manager
- Risk Manager
- Quant Researcher
- Operations
- Auditor
- Read Only

---

# Token Lifetime

| Token | Lifetime |
|---------|----------|
| Access Token | 1 Hour |
| Refresh Token | 30 Days |

---

# Security Best Practices

- Never hardcode secrets.
- Rotate API keys.
- Enforce HTTPS.
- Validate JWT signature.
- Enable audit logging.
- Apply least privilege.