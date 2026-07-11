# Value at Risk (VaR)

## Institutional Quant Platform

---

# Purpose

Value at Risk (VaR) estimates the maximum expected portfolio loss over a specified holding period at a given confidence level under normal market conditions.

VaR provides a standardized measure of downside risk and is one of the primary risk metrics used by institutional investment managers.

---

# Objectives

The VaR Engine is designed to

- Estimate potential portfolio losses
- Measure downside exposure
- Support risk budgeting
- Monitor portfolio risk
- Validate portfolio constraints
- Compare portfolio risk over time
- Generate institutional risk reports

---

# Position within the Platform

```text
Portfolio Holdings
         │
         ▼
 Market Returns
         │
         ▼
 Covariance Matrix
         │
         ▼
      VaR Engine
         │
         ▼
 Risk Dashboard
         │
         ▼
Portfolio Optimizer
```

---

# What is Value at Risk?

VaR answers the following question.

> "What is the maximum expected loss over a given time horizon at a specified confidence level under normal market conditions?"

Example

```text
1-Day VaR

95%

₹2,500,000
```

Interpretation

There is a **95% probability** that the portfolio will **not lose more than ₹2.5 million in one trading day**, assuming normal market conditions.

---

# Components

VaR depends on

- Portfolio Value
- Expected Return
- Portfolio Volatility
- Confidence Level
- Holding Period

---

# Confidence Levels

Typical institutional confidence levels

| Confidence | Tail Probability |
|------------|-----------------:|
| 90% | 10% |
| 95% | 5% |
| 97.5% | 2.5% |
| 99% | 1% |

---

# Holding Periods

Common horizons

- 1 Day
- 5 Days
- 10 Days
- 1 Month

---

# VaR Methodologies

The platform supports multiple estimation methods.

---

## Historical Simulation

Uses historical portfolio returns without assuming a probability distribution.

Workflow

```text
Historical Returns

↓

Portfolio Returns

↓

Sort Losses

↓

Percentile Selection

↓

Historical VaR
```

Advantages

- Distribution free
- Captures real market behavior

Limitations

- Depends on historical data
- May not capture future events

---

## Parametric (Variance-Covariance)

Assumes portfolio returns follow a normal distribution.

Formula

```text
VaR

=

Portfolio Value

×

Z Score

×

Portfolio Volatility
```

Advantages

- Fast
- Efficient
- Suitable for large portfolios

Limitations

- Assumes normality
- Underestimates fat tails

---

## Monte Carlo Simulation

Generates thousands of simulated market scenarios.

Workflow

```text
Market Model

↓

Random Scenarios

↓

Portfolio Revaluation

↓

Loss Distribution

↓

VaR
```

Advantages

- Highly flexible
- Supports complex portfolios

Limitations

- Computationally intensive
- Model dependent

---

# Inputs

The VaR Engine consumes

## Portfolio Holdings

- Security
- Quantity
- Weight
- Market Value

---

## Market Data

- Historical Prices
- Returns
- Volatility
- Correlations

---

## Covariance Matrix

Required for

- Parametric VaR
- Risk Attribution

---

## Configuration

Examples

- Confidence Level
- Holding Period
- Estimation Method
- Observation Window

---

# Calculation Workflow

```text
Market Data
      │
      ▼
Return Calculation
      │
      ▼
Volatility Estimation
      │
      ▼
Covariance Matrix
      │
      ▼
VaR Method
      │
      ▼
Portfolio VaR
```

---

# Example

Portfolio Value

```text
₹100,000,000
```

Confidence

```text
95%
```

Daily Volatility

```text
1.5%
```

Approximate VaR

```text
₹2,470,000
```

---

# Interpretation

Higher VaR indicates greater potential downside risk.

Example

| Portfolio | 1-Day VaR |
|-----------|----------:|
| Portfolio A | ₹1.8M |
| Portfolio B | ₹4.2M |

Portfolio B carries significantly higher downside risk.

---

# Risk Limits

Typical institutional limits

- Maximum Daily VaR
- Maximum Weekly VaR
- Maximum Monthly VaR
- VaR as % of NAV

Example

```text
Daily VaR

≤ 2%

of Portfolio Value
```

---

# Integration

The VaR Engine integrates with

- Portfolio Optimizer
- Constraint Engine
- Stress Testing
- Expected Shortfall
- Dashboard
- Reporting

---

# Monitoring

Operational metrics

- Daily VaR
- Weekly VaR
- Monthly VaR
- VaR Utilization
- Confidence Level
- Calculation Time
- Data Freshness

---

# Validation

Validation checks

- Portfolio Weights
- Missing Prices
- Missing Returns
- Covariance Matrix
- Confidence Level
- Holding Period

---

# Error Handling

Potential issues

- Missing historical data
- Singular covariance matrix
- Invalid confidence level
- Insufficient observations
- Portfolio mismatch

Fallback methods

- Previous VaR
- Historical approximation
- Conservative volatility estimate

---

# Performance Optimization

The engine uses

- Vectorized NumPy calculations
- DuckDB aggregation
- Cached covariance matrices
- Parallel simulations
- Incremental updates

---

# Limitations

VaR should not be interpreted as a worst-case loss.

Limitations include

- Assumes normal market conditions
- Does not estimate losses beyond the confidence level
- Sensitive to model assumptions
- Historical data may not predict future crises

For tail-risk estimation, Expected Shortfall should also be used.

---

# Future Enhancements

Planned capabilities

- Filtered Historical Simulation
- Cornish-Fisher VaR
- Extreme Value Theory (EVT)
- Intraday VaR
- Incremental VaR
- Component VaR
- Marginal VaR

---

# Related Documents

- Risk Overview
- Expected Shortfall
- Stress Testing
- Factor Exposure
- Portfolio Optimizer
- Portfolio Constraints

---

End of Document