# API Examples

## Example 1

Request

```http
GET /portfolio
Authorization: Bearer TOKEN
```

Response

```json
{
  "portfolio":"LIVE",
  "positions":50
}
```

---

## Example 2

Rebalance

```http
POST /portfolio/rebalance
```

```json
{
  "optimizer":"risk_parity"
}
```

---

Response

```json
{
  "status":"accepted",
  "job_id":"abc123"
}
```

---

## Example 3

Risk Report

```http
GET /risk/report
```

Response

```json
{
  "VaR":0.023,
  "CVaR":0.031,
  "TrackingError":0.015
}
```

---

## Example 4

Alpha Signals

```http
GET /alpha/signals
```

Returns

- Momentum
- Value
- Quality
- Growth
- Volatility