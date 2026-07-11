# Universe Builder

## Institutional Quant Platform

---

# Purpose

The Universe Builder is responsible for constructing the investable universe by filtering all available securities according to predefined business, liquidity, quality, and regulatory rules.

The resulting universe serves as the foundation for factor calculation, alpha generation, portfolio optimization, and risk management.

---

# Objectives

The Universe Builder is designed to:

- Define the investable universe
- Remove ineligible securities
- Ensure sufficient liquidity
- Improve data quality
- Reduce execution risk
- Support strategy-specific universes
- Maintain reproducibility

---

# Position within the Platform

```text
          Market Data
               │
               ▼
        Data Validation
               │
               ▼
       Universe Builder
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
Factor Engine Alpha Engine Risk Engine
               │
               ▼
      Portfolio Optimizer
```

---

# Inputs

The Universe Builder consumes:

## Market Data

- Symbol
- Exchange
- Market Capitalization
- Daily Volume
- Free Float
- Sector
- Industry

---

## Fundamental Data

- Financial Statements
- Earnings
- Cash Flow
- Balance Sheet
- Financial Ratios

---

## Metadata

- Listing Status
- Listing Date
- Delisting Information
- Trading Status
- Corporate Actions

---

# Universe Construction Workflow

```text
All Listed Securities
          │
          ▼
Exchange Filter
          │
          ▼
Listing Status Filter
          │
          ▼
Liquidity Filter
          │
          ▼
Market Cap Filter
          │
          ▼
Data Quality Filter
          │
          ▼
Sector Classification
          │
          ▼
Business Rules
          │
          ▼
Final Investment Universe
```

---

# Eligibility Rules

Securities must satisfy:

- Actively traded
- Valid symbol
- Listed on supported exchange
- Sufficient trading history
- Reliable market data
- Reliable financial data

---

# Exchange Filter

Supported exchanges include:

- NSE
- BSE

Future support:

- NYSE
- NASDAQ
- LSE
- SGX

---

# Liquidity Filter

Minimum requirements may include:

- Average Daily Volume
- Average Daily Value Traded
- Minimum Trading Days
- Bid-Ask Spread Threshold

Example

```text
Average Daily Volume

>= 100,000 Shares
```

---

# Market Capitalization Filter

Universe can be configured for:

- Large Cap
- Mid Cap
- Small Cap
- Micro Cap
- Multi Cap

Example

```text
Market Cap

>= ₹1,000 Crore
```

---

# Trading History

Minimum trading history

Example

```text
365 Trading Days
```

This prevents recently listed securities from entering the investment universe prematurely.

---

# Data Quality Filter

Validation checks include:

- Missing prices
- Missing financial statements
- Duplicate symbols
- Invalid sectors
- Invalid industries
- Stale market data

---

# Corporate Actions

The engine considers:

- Stock Splits
- Bonus Issues
- Rights Issues
- Mergers
- Demergers
- Delistings

---

# Sector Classification

Each security is mapped to:

- Sector
- Industry
- Sub-Industry

This supports:

- Diversification
- Sector Constraints
- Relative Ranking

---

# Business Rules

Examples

- Exclude suspended securities
- Exclude ETFs
- Exclude preferred shares
- Exclude penny stocks
- Exclude bankrupt companies

Rules are configurable.

---

# Duplicate Handling

Duplicate listings are resolved by:

- Exchange priority
- Liquidity
- Primary listing

---

# Output Structure

Example

```text
Ticker

Company

Sector

Industry

Market Cap

Liquidity Score

Eligibility

Universe Rank
```

---

# Configuration

Typical configuration options:

- Supported exchanges
- Liquidity thresholds
- Market cap thresholds
- Trading history
- Allowed sectors
- Excluded industries
- Eligible security types

---

# Performance Optimization

The engine uses:

- DuckDB SQL filtering
- Vectorized filtering
- Cached metadata
- Parallel processing
- Incremental updates

---

# Validation

Validation includes:

- Symbol uniqueness
- Exchange consistency
- Data freshness
- Sector mapping
- Missing metadata
- Universe completeness

---

# Monitoring

Operational metrics

- Total securities scanned
- Securities rejected
- Eligible securities
- Liquidity failures
- Market cap failures
- Missing data rate
- Processing time

---

# Error Handling

Common scenarios

- Missing metadata
- Invalid exchange
- Delisted security
- Missing market cap
- Invalid sector mapping

Errors are logged for investigation while allowing processing of remaining securities.

---

# Integration

The Universe Builder integrates with:

- Data Pipeline
- Factor Engine
- Alpha Engine
- Portfolio Optimizer
- Risk Engine
- Dashboard
- Reporting

---

# Future Enhancements

Planned capabilities

- Dynamic universe construction
- ESG screening
- Sustainability filters
- Country-specific universes
- Multi-asset support
- Theme-based universes
- AI-assisted eligibility rules

---

# Related Documents

- Alpha Engine
- Factor Engine
- Regime Detection
- Scoring Engine
- Portfolio Optimizer
- Risk Engine

---

End of Document