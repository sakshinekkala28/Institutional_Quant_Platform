# Performance Attribution

Performance attribution explains **why** a portfolio generated its returns by decomposing performance into meaningful investment decisions. It helps portfolio managers understand the contribution of asset allocation, security selection, factor exposures, and execution quality.

---

# Overview

The attribution framework within the Institutional Quant Platform supports:

- Portfolio-level attribution
- Sector attribution
- Security attribution
- Factor attribution
- Style attribution
- Transaction cost attribution
- Benchmark-relative attribution

---

# Attribution Objectives

Performance attribution enables users to:

- Evaluate investment decisions
- Identify return drivers
- Measure active management skill
- Compare results against benchmarks
- Improve portfolio construction
- Monitor investment consistency

---

# Attribution Levels

## Portfolio Attribution

Measures the overall contribution of the portfolio relative to its benchmark.

Typical metrics include:

- Total Return
- Active Return
- Benchmark Return
- Tracking Difference

---

## Sector Attribution

Analyzes the impact of sector allocation decisions.

Example:

| Sector | Portfolio Weight | Benchmark Weight | Contribution |
|----------|----------------:|-----------------:|-------------:|
| Financials | 22.5% | 18.0% | +0.82% |
| IT | 16.0% | 20.5% | -0.37% |
| Energy | 9.8% | 8.5% | +0.14% |

---

## Security Attribution

Measures the contribution of individual securities.

Example metrics:

- Portfolio Weight
- Security Return
- Contribution to Return
- Active Contribution

---

## Factor Attribution

Evaluates how systematic factor exposures affected performance.

Common factors include:

- Value
- Momentum
- Quality
- Size
- Low Volatility
- Growth

---

## Style Attribution

Measures returns generated from investment styles.

Examples:

- Growth
- Value
- Blend
- Defensive
- Cyclical

---

# Brinson Attribution

The platform can support the Brinson attribution methodology, decomposing active return into:

- Allocation Effect
- Selection Effect
- Interaction Effect

Formula:

```
Active Return

= Allocation Effect
+ Selection Effect
+ Interaction Effect
```

---

# Factor Contribution

Example factor attribution output:

| Factor | Exposure | Contribution |
|----------|----------:|-------------:|
| Value | 0.42 | +0.76% |
| Momentum | 0.28 | +0.41% |
| Quality | 0.51 | +0.68% |
| Size | -0.13 | -0.12% |

---

# Risk Attribution

Risk attribution explains which components contribute most to portfolio risk.

Examples:

- Sector contribution
- Position contribution
- Factor contribution
- Country contribution
- Industry contribution

Typical metrics:

- Marginal Risk Contribution
- Percentage Risk Contribution
- Component Volatility

---

# Transaction Cost Attribution

Execution-related performance can be decomposed into:

- Slippage
- Commission
- Market Impact
- Timing Cost
- Opportunity Cost

---

# Benchmark Attribution

Supported benchmark comparisons include:

- NIFTY 50
- NIFTY 100
- NIFTY 500
- Custom Benchmarks

Common benchmark metrics:

- Active Return
- Tracking Error
- Information Ratio
- Active Share

---

# Attribution Workflow

```text
Portfolio Returns
        │
        ▼
Benchmark Returns
        │
        ▼
Allocation Analysis
        │
        ▼
Selection Analysis
        │
        ▼
Factor Attribution
        │
        ▼
Risk Attribution
        │
        ▼
Generate Attribution Report
```

---

# Deliverables

Typical attribution reports include:

- Executive Summary
- Portfolio Contribution
- Benchmark Comparison
- Sector Analysis
- Security Contribution
- Factor Contribution
- Risk Attribution
- Transaction Cost Summary

---

# Best Practices

- Use a consistent benchmark.
- Align attribution periods with reporting periods.
- Validate portfolio weights before analysis.
- Include both return and risk attribution.
- Review transaction costs alongside investment decisions.
- Archive attribution reports for historical analysis.

---

# Related Documentation

- Performance Reporting
- Report Exports
- Dashboard Documentation
- Portfolio Documentation
- Risk Documentation
- Analytics Documentation