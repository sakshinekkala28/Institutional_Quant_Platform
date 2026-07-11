# Transaction Cost Model

## Institutional Quant Platform

---

# Purpose

The Transaction Cost Model estimates the total cost of implementing portfolio changes.

Rather than optimizing solely for expected returns, the Portfolio Optimizer incorporates transaction costs to maximize **net expected returns** after all trading expenses.

The model supports both historical backtesting and live portfolio rebalancing.

---

# Objectives

The Transaction Cost Model is designed to:

- Estimate execution costs
- Reduce unnecessary turnover
- Improve net portfolio performance
- Support realistic backtesting
- Assist portfolio optimization
- Prioritize cost-efficient trades
- Model market impact

---

# Position within the Platform

```text
Portfolio Optimizer
        │
        ▼
Transaction Cost Model
        │
        ▼
Portfolio Rebalancer
        │
        ▼
Execution Engine
        │
        ▼
Trade Orders
```

---

# Transaction Cost Components

The total transaction cost consists of multiple components.

```text
Total Cost

=

Brokerage

+

Exchange Charges

+

Taxes

+

Slippage

+

Bid-Ask Spread

+

Market Impact
```

---

# Brokerage

Brokerage depends on

- Broker
- Trading Segment
- Order Type
- Brokerage Plan

Example

```text
Brokerage

=

Trade Value × Brokerage Rate
```

---

# Exchange Charges

Applicable exchange fees include

- NSE Transaction Charges
- BSE Transaction Charges
- Clearing Charges

These values should be externally configurable.

---

# Regulatory Charges (India)

The model supports estimation of

- Securities Transaction Tax (STT)
- Stamp Duty
- GST
- SEBI Turnover Fees

All values should be configurable to accommodate regulatory changes.

---

# Bid-Ask Spread

The cost associated with crossing the market spread.

Example

```text
Spread Cost

=

Spread

×

Trade Quantity
```

---

# Slippage

Slippage represents the difference between expected and executed prices.

Sources include

- Fast-moving markets
- Large orders
- Low liquidity
- Partial fills

Example

```text
Slippage

=

Executed Price

−

Expected Price
```

---

# Market Impact

Large orders may move market prices.

Factors influencing impact

- Order Size
- Average Daily Volume
- Liquidity
- Volatility
- Participation Rate

Typical approaches

- Linear Impact Model
- Square Root Impact Model
- Almgren–Chriss Model (future enhancement)

---

# Liquidity Cost

The model evaluates

- Average Daily Volume
- Turnover
- Days to Liquidate
- Participation Rate

Illiquid securities incur higher estimated costs.

---

# Cost Estimation Workflow

```text
Trade List
      │
      ▼
Brokerage
      │
      ▼
Taxes
      │
      ▼
Spread
      │
      ▼
Slippage
      │
      ▼
Market Impact
      │
      ▼
Total Estimated Cost
```

---

# Inputs

The model consumes

## Trade Information

- Buy/Sell
- Quantity
- Price
- Trade Value

---

## Market Data

- Bid
- Ask
- Last Price
- Volume
- Volatility

---

## Portfolio Data

- Current Holdings
- Target Holdings
- Cash Balance

---

# Outputs

Generated outputs

- Brokerage Estimate
- Regulatory Charges
- Slippage Estimate
- Spread Cost
- Market Impact
- Total Transaction Cost
- Net Trade Cost

Example

| Component | Estimated Cost |
|-----------|---------------:|
| Brokerage | ₹420 |
| Taxes | ₹315 |
| Spread | ₹180 |
| Slippage | ₹540 |
| Market Impact | ₹760 |
| **Total** | **₹2,215** |

---

# Integration with Portfolio Optimization

The Portfolio Optimizer incorporates transaction costs into its objective function.

Conceptually

```text
Maximize

Expected Return

−

Risk

−

Transaction Costs
```

This discourages unnecessary trading and favors portfolios with higher net expected returns.

---

# Integration with Rebalancing

The Rebalancer uses transaction cost estimates to

- Skip low-value trades
- Reduce turnover
- Batch orders
- Delay non-critical trades

---

# Monitoring

Operational metrics

- Average Trade Cost
- Cost as % of Portfolio
- Slippage
- Market Impact
- Brokerage
- Tax Cost
- Turnover
- Cost per Rebalance

---

# Configuration

Typical configurable parameters

- Brokerage Rates
- Exchange Charges
- Tax Rates
- Slippage Model
- Market Impact Model
- Liquidity Thresholds

Configuration should be externalized.

---

# Validation

Validation checks include

- Missing prices
- Invalid quantities
- Negative trade values
- Zero liquidity
- Invalid brokerage configuration

---

# Error Handling

Potential issues

- Missing market prices
- Invalid tax configuration
- Zero volume
- Negative trade quantity
- Missing brokerage schedule

Fallback logic estimates costs using configurable defaults while logging warnings.

---

# Performance Optimization

The model uses

- Vectorized calculations
- Cached fee schedules
- Batch trade evaluation
- Incremental cost estimation
- DuckDB aggregation

---

# Future Enhancements

Planned capabilities

- Broker-specific fee schedules
- Dynamic spread estimation
- Intraday transaction cost models
- AI-based slippage prediction
- Real-time execution feedback
- Cross-exchange cost optimization

---

# Related Documents

- Portfolio Overview
- Portfolio Optimizer
- Portfolio Constraints
- Portfolio Rebalancer
- Execution Engine
- Risk Engine

---

End of Document