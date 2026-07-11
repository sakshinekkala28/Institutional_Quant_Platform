# Portfolio Constraints

## Institutional Quant Platform

---

# Purpose

The Portfolio Constraints Engine ensures that every optimized portfolio adheres to investment policies, regulatory requirements, liquidity considerations, and internal risk controls.

Constraints define the feasible investment universe for the optimizer and prevent undesirable portfolio characteristics such as excessive concentration, illiquidity, or excessive turnover.

---

# Objectives

The Constraints Engine is designed to:

- Enforce investment policies
- Maintain diversification
- Control concentration risk
- Limit portfolio turnover
- Ensure liquidity
- Meet regulatory requirements
- Support institution-specific mandates
- Provide configurable constraint management

---

# Position within the Platform

```text
                 Alpha Engine
                      │
                      ▼
               Scoring Engine
                      │
                      ▼
            Portfolio Optimizer
                      │
                      ▼
            Portfolio Constraints
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
  Risk Validation            Compliance Check
        │                           │
        └─────────────┬─────────────┘
                      ▼
              Target Portfolio
```

---

# Constraint Categories

The platform supports multiple categories of constraints.

---

## Position Constraints

Control individual security exposure.

Examples

- Maximum Position Weight
- Minimum Position Weight
- Maximum Shares
- Minimum Shares

Example

```text
Maximum Position Weight

≤ 5%
```

---

## Sector Constraints

Limit sector concentration.

Example

```text
Technology

≤ 20%
```

---

## Industry Constraints

Prevent excessive exposure to individual industries.

Example

```text
Banking

≤ 15%
```

---

## Market Capitalization Constraints

Support investment mandates.

Examples

- Large Cap Only
- Mid Cap Only
- Small Cap Allocation
- Multi Cap Allocation

---

## Liquidity Constraints

Only invest in sufficiently liquid securities.

Examples

- Minimum Average Daily Volume
- Minimum Turnover
- Maximum Days to Liquidate
- Maximum Participation Rate

---

## Turnover Constraints

Reduce unnecessary trading.

Example

```text
Monthly Turnover

≤ 25%
```

---

## Cash Constraints

Maintain required cash reserves.

Example

```text
Cash Allocation

≥ 2%

≤ 10%
```

---

## Leverage Constraints

Applicable for leveraged strategies.

Example

```text
Gross Exposure

≤ 150%

Net Exposure

≤ 100%
```

---

## Diversification Constraints

Prevent excessive concentration.

Examples

- Maximum holdings
- Minimum holdings
- Equal-weight tolerance
- Concentration limits

---

## Country Constraints

Applicable for global portfolios.

Example

```text
India

≤ 80%

United States

≤ 20%
```

---

## Currency Constraints

Control foreign exchange exposure.

Examples

- Maximum USD exposure
- Maximum EUR exposure
- Hedging requirements

---

## ESG Constraints

Optional sustainability constraints.

Examples

- Minimum ESG Score
- Excluded Industries
- Carbon Exposure Limit

---

## Regulatory Constraints

Examples

- UCITS
- SEBI
- Internal Investment Policies
- Client-Specific Mandates

---

# Hard vs Soft Constraints

## Hard Constraints

Must never be violated.

Examples

- Weight sum equals 100%
- Maximum position size
- Cash cannot be negative
- Regulatory limits

Violation results in optimization failure.

---

## Soft Constraints

May be relaxed if necessary.

Examples

- Preferred sector allocation
- Turnover target
- Style exposure
- Tracking error

Violations incur optimization penalties.

---

# Constraint Processing Workflow

```text
Target Portfolio
       │
       ▼
Position Constraints
       │
       ▼
Sector Constraints
       │
       ▼
Liquidity Constraints
       │
       ▼
Risk Constraints
       │
       ▼
Compliance Validation
       │
       ▼
Approved Portfolio
```

---

# Constraint Validation

Validation includes

- Position limits
- Sector exposure
- Industry exposure
- Cash allocation
- Weight sum
- Liquidity
- Turnover
- Regulatory compliance

---

# Optimization Integration

The Portfolio Optimizer incorporates constraints directly into the optimization problem.

Objective

```text
Maximize

Expected Return

Subject To

Portfolio Constraints
```

---

# Configuration

Constraint parameters are configurable.

Examples

```text
MAX_POSITION_WEIGHT = 5%

MAX_SECTOR_WEIGHT = 20%

MAX_TURNOVER = 25%

MIN_CASH = 2%
```

Configuration should be externalized and environment-specific.

---

# Monitoring

Operational metrics

- Constraint violations
- Average position size
- Sector concentration
- Portfolio diversification
- Liquidity score
- Turnover
- Compliance status

---

# Error Handling

Potential issues

- Infeasible optimization
- Conflicting constraints
- Missing constraint definitions
- Invalid configuration
- Regulatory violations

Fallback strategies

- Relax soft constraints
- Notify operators
- Use previous portfolio
- Generate validation report

---

# Reporting

Constraint reports include

- Position limit utilization
- Sector exposure
- Industry exposure
- Cash allocation
- Liquidity metrics
- Turnover statistics
- Compliance summary

---

# Integration

The Constraints Engine integrates with

- Portfolio Optimizer
- Risk Engine
- Transaction Cost Model
- Rebalance Engine
- Execution Engine
- Dashboard
- Reporting

---

# Future Enhancements

Planned capabilities

- Dynamic constraint adjustment
- AI-assisted constraint tuning
- Client-specific mandate templates
- Real-time compliance monitoring
- Multi-portfolio constraint optimization
- ESG policy automation

---

# Related Documents

- Portfolio Overview
- Portfolio Optimizer
- Portfolio Rebalancer
- Transaction Cost Model
- Risk Engine
- Execution Engine

---

End of Document