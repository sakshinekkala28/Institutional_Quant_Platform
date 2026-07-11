# Expected Shortfall (Conditional Value at Risk)

## Institutional Quant Platform

---

# Purpose

Expected Shortfall (ES), also known as **Conditional Value at Risk (CVaR)**, measures the **average portfolio loss when losses exceed the Value at Risk (VaR) threshold**.

Unlike VaR, which only identifies a loss threshold, Expected Shortfall quantifies the severity of extreme losses. It is widely regarded as a superior tail-risk measure and has been adopted under the **Basel III / Basel IV Fundamental Review of the Trading Book (FRTB)** framework.

The Expected Shortfall Engine enables the Institutional Quant Platform to evaluate extreme downside risk, optimize portfolios under tail-risk constraints, and improve capital preservation.

---

# Objectives

The Expected Shortfall Engine is designed to

- Measure tail risk
- Estimate extreme portfolio losses
- Improve downside risk management
- Support institutional compliance
- Enhance portfolio optimization
- Complement Value at Risk
- Improve capital allocation

---

# Position within the Platform

```text
Portfolio Holdings
        │
        ▼
 Historical Returns
        │
        ▼
   VaR Calculation
        │
        ▼
Expected Shortfall Engine
        │
        ▼
 Risk Dashboard
        │
        ▼
Portfolio Optimizer
```

---

# Definition

Expected Shortfall answers the question:

> "If losses exceed the VaR threshold, what is the average expected loss?"

Unlike VaR, ES considers the entire tail of the loss distribution.

---

# Example

Portfolio Value

```text
₹100,000,000
```

95% VaR

```text
₹2,400,000
```

95% Expected Shortfall

```text
₹3,800,000
```

Interpretation

```text
There is a 5% probability that losses exceed the VaR.

If this occurs,

the average expected loss is ₹3.8 million.
```

---

# Why Expected Shortfall?

VaR has an important limitation.

It tells us

```text
Loss

≤ ₹2.4 Million
```

but provides no information regarding

```text
Loss

> ₹2.4 Million
```

Expected Shortfall measures the severity of these extreme outcomes.

---

# Comparison with VaR

| Metric | Value at Risk | Expected Shortfall |
|---------|---------------|--------------------|
| Measures Threshold | Yes | No |
| Measures Tail Loss | No | Yes |
| Uses Tail Distribution | No | Yes |
| Coherent Risk Measure | No | Yes |
| Basel III Standard | No | Yes |

---

# Mathematical Definition

Conceptually

```text
Expected Shortfall

=

Average Loss

Given

Loss > VaR
```

---

# Estimation Methods

---

## Historical Simulation

Workflow

```text
Historical Returns

↓

Loss Distribution

↓

VaR Threshold

↓

Average Tail Loss

↓

Expected Shortfall
```

Advantages

- No distribution assumptions
- Simple implementation
- Reflects historical behavior

---

## Parametric Method

Assumes

- Normally distributed returns
- Estimated volatility
- Estimated covariance matrix

Advantages

- Fast
- Computationally efficient

Limitations

- Sensitive to distribution assumptions

---

## Monte Carlo Simulation

Workflow

```text
Market Model

↓

Random Scenarios

↓

Portfolio Valuation

↓

Loss Distribution

↓

Tail Loss Average
```

Advantages

- Flexible
- Supports nonlinear portfolios
- Suitable for derivatives

---

# Inputs

The Expected Shortfall Engine consumes

## Portfolio Holdings

- Positions
- Weights
- Market Values

---

## Market Data

- Prices
- Returns
- Volatility
- Correlations

---

## VaR Results

- Confidence Level
- Holding Period
- Tail Threshold

---

# Confidence Levels

Typical confidence levels

| Confidence | Tail Probability |
|------------|-----------------:|
| 95% | 5% |
| 97.5% | 2.5% |
| 99% | 1% |

---

# Holding Periods

Supported horizons

- 1 Day
- 5 Days
- 10 Days
- Monthly

---

# Calculation Workflow

```text
Historical Returns
        │
        ▼
Loss Distribution
        │
        ▼
VaR Threshold
        │
        ▼
Tail Loss Selection
        │
        ▼
Average Tail Loss
        │
        ▼
Expected Shortfall
```

---

# Outputs

Generated outputs

- Daily Expected Shortfall
- Weekly Expected Shortfall
- Monthly Expected Shortfall
- Tail Loss Distribution
- Tail Risk Report
- Expected Shortfall Utilization

---

# Portfolio Optimization

Expected Shortfall can be used directly as an optimization objective.

Example

```text
Maximize

Expected Return

Subject To

Expected Shortfall ≤ Target
```

or

```text
Maximize

Expected Return

−

λ × Expected Shortfall
```

where

```text
λ

=

Risk Aversion Parameter
```

---

# Basel III / Basel IV

Expected Shortfall replaces VaR for market risk capital calculations under the **Fundamental Review of the Trading Book (FRTB)** because it provides a more comprehensive measure of tail risk.

Benefits include

- Better capital estimation
- Improved stress resilience
- More accurate downside measurement

---

# Integration

The Expected Shortfall Engine integrates with

- Value at Risk
- Portfolio Optimizer
- Stress Testing
- Factor Exposure
- Dashboard
- Reporting

---

# Monitoring

Operational metrics

- Daily ES
- Weekly ES
- Monthly ES
- Tail Loss Percentage
- ES Utilization
- Processing Time
- Data Freshness

---

# Validation

Validation includes

- Portfolio Weights
- Historical Returns
- Tail Sample Size
- Confidence Level
- Holding Period
- Distribution Consistency

---

# Error Handling

Potential issues

- Insufficient historical observations
- Missing prices
- Invalid confidence level
- Empty tail distribution
- Portfolio mismatch

Fallback actions

- Increase observation window
- Use historical approximation
- Apply conservative estimates
- Generate validation warning

---

# Performance Optimization

The engine uses

- Vectorized NumPy calculations
- DuckDB aggregation
- Cached return matrices
- Parallel simulations
- Incremental updates

---

# Limitations

Expected Shortfall depends on

- Historical data quality
- Market assumptions
- Model selection
- Observation window

It should be used alongside

- VaR
- Stress Testing
- Scenario Analysis
- Concentration Risk

---

# Future Enhancements

Planned capabilities

- Filtered Historical ES
- Extreme Value Theory (EVT)
- Dynamic ES Forecasting
- Intraday ES
- Component Expected Shortfall
- Marginal Expected Shortfall
- AI-based Tail Risk Prediction

---

# Related Documents

- Risk Overview
- Value at Risk
- Stress Testing
- Factor Exposure
- Portfolio Optimizer
- Portfolio Constraints

---

End of Document