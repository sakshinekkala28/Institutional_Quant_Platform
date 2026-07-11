# REST API Endpoints

## Base URL

```
https://api.company.com/v1
```

---

# Portfolio

## GET Portfolio

```
GET /portfolio
```

Returns current holdings.

---

## POST Rebalance

```
POST /portfolio/rebalance
```

Triggers optimization.

---

## GET Holdings

```
GET /portfolio/holdings
```

Returns latest holdings.

---

# Alpha

## GET Signals

```
GET /alpha/signals
```

Returns alpha signals.

---

## POST Alpha Build

```
POST /alpha/build
```

Runs alpha engine.

---

# Risk

## GET Risk Report

```
GET /risk/report
```

Returns risk metrics.

---

## GET Stress Test

```
GET /risk/stress
```

Returns stress testing.

---

# Execution

## POST Orders

```
POST /execution/orders
```

Creates execution orders.

---

## GET Trades

```
GET /execution/trades
```

Returns executed trades.

---

# Reporting

## GET Dashboard

```
GET /report/dashboard
```

---

## GET PDF

```
GET /report/pdf
```

---

# Monitoring

## GET Health

```
GET /monitor/health
```

---

## GET Metrics

```
GET /monitor/metrics
```

---

# Response Format

```json
{
  "status":"success",
  "data":{},
  "metadata":{}
}
```

---

# Error Format

```json
{
  "status":"error",
  "code":400,
  "message":"Invalid request"
}
```