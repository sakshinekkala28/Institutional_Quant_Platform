"""
=========================================================
OPTIMIZER ENGINE
=========================================================

Purpose:
Institutional Portfolio Optimization

Strategies:
1. Minimum Variance
2. Risk Parity
3. Maximum Sharpe
4. Institutional Model Portfolio

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIGURATION
# =========================================================

ENGINE_VERSION = "1.0.0"

TRADING_DAYS = 252

RISK_FREE_RATE = 0.06

MIN_POSITION_WEIGHT = 0.00

MAX_POSITION_WEIGHT = 0.05

MIN_ACTIVE_WEIGHT = 0.0005

TARGET_PORTFOLIO_SIZE = 50

TOP_MOMENTUM_UNIVERSE = 500

USE_SHRINKAGE_COVARIANCE = True

EXPECTED_RETURN_LOOKBACK = 252

MIN_HISTORY_REQUIRED = 126

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

RISK_DIR = (
    ROOT
    / "data"
    / "risk"
)

PORTFOLIO_DIR = (
    ROOT
    / "data"
    / "portfolios"
)

LOG_DIR = (
    ROOT
    / "data"
    / "logs"
)

PORTFOLIO_DIR.mkdir(
    parents=True,
    exist_ok=True
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# INPUT FILES
# =========================================================

RETURNS_FILE = (
    RISK_DIR
    / "returns_matrix.parquet"
)

COVARIANCE_FILE = (
    RISK_DIR
    / "covariance_matrix.parquet"
)

SHRINKAGE_FILE = (
    RISK_DIR
    / "shrinkage_covariance.parquet"
)

# =========================================================
# OUTPUT FILES
# =========================================================

SUMMARY_FILE = (
    PORTFOLIO_DIR
    / "optimizer_summary.csv"
)

AUDIT_FILE = (
    LOG_DIR
    / "optimizer_audit.csv"
)

# =========================================================
# LOAD INPUTS
# =========================================================

print(
    "\n📥 Loading Optimization Inputs..."
)

if not RETURNS_FILE.exists():

    raise FileNotFoundError(
        RETURNS_FILE
    )

returns_matrix = pd.read_parquet(
    RETURNS_FILE
)

if USE_SHRINKAGE_COVARIANCE:

    covariance_file = SHRINKAGE_FILE

else:

    covariance_file = COVARIANCE_FILE

if not covariance_file.exists():

    raise FileNotFoundError(
        covariance_file
    )

covariance_matrix = pd.read_parquet(
    covariance_file
)

# =========================================================
# VALIDATION
# =========================================================

print(
    "✔ Validating Inputs..."
)

if returns_matrix.empty:

    raise ValueError(
        "Returns matrix empty."
    )

if covariance_matrix.empty:

    raise ValueError(
        "Covariance matrix empty."
    )

returns_matrix.columns = (

    returns_matrix.columns

    .astype(str)

    .str.upper()

    .str.strip()
)

covariance_matrix.index = (

    covariance_matrix.index

    .astype(str)

    .str.upper()

    .str.strip()
)

covariance_matrix.columns = (

    covariance_matrix.columns

    .astype(str)

    .str.upper()

    .str.strip()
)

# =========================================================
# ALIGN UNIVERSE
# =========================================================

common_symbols = sorted(

    set(
        returns_matrix.columns
    )

    &

    set(
        covariance_matrix.columns
    )
)

if len(
    common_symbols
) == 0:

    raise ValueError(
        "No common optimization universe."
    )

returns_matrix = (

    returns_matrix[
        common_symbols
    ]

    .copy()
)

covariance_matrix = (

    covariance_matrix

    .loc[
        common_symbols,
        common_symbols
    ]

    .copy()
)

print(
    f"Optimization Universe : "
    f"{len(common_symbols):,}"
)

# =========================================================
# COVERAGE FILTER
# =========================================================

coverage = (

    1

    -

    returns_matrix
    .isna()
    .mean()
)

eligible_symbols = coverage[
    coverage >= 0.75
].index.tolist()

returns_matrix = (

    returns_matrix[
        eligible_symbols
    ]

    .copy()
)

covariance_matrix = (

    covariance_matrix

    .loc[
        eligible_symbols,
        eligible_symbols
    ]
)

print(
    f"Eligible Securities : "
    f"{len(eligible_symbols):,}"
)

# =========================================================
# EXPECTED RETURNS
# =========================================================

print(
    "📈 Building Expected Returns..."
)

recent_returns = (

    returns_matrix

    .tail(
        EXPECTED_RETURN_LOOKBACK
    )
)

# =========================================================
# WINSORIZE EXTREME RETURNS
# =========================================================

recent_returns = recent_returns.clip(

    lower=recent_returns.quantile(
        0.01
    ),

    upper=recent_returns.quantile(
        0.99
    ),

    axis=1
)

# =========================================================
# MOMENTUM EXPECTED RETURN MODEL
# =========================================================

# =========================================================
# 12-1 MOMENTUM FORECAST
# =========================================================

momentum_12m = (

    (1 + returns_matrix.tail(252))

    .prod()

    - 1
)

momentum_1m = (

    (1 + returns_matrix.tail(21))

    .prod()

    - 1
)

expected_returns = (
    momentum_12m
    -
    momentum_1m
)

expected_returns = expected_returns.clip(
    lower=-0.50,
    upper=0.75
)

print("\nForecast Quantiles")

print(
    expected_returns.quantile(
        [
            0.01,
            0.05,
            0.10,
            0.25,
            0.50,
            0.75,
            0.90,
            0.95,
            0.99
        ]
    )
)

print("\nExpected Return Distribution:")

print(
    expected_returns.describe()
)

print(
    "\nPositive Forecasts :",
    (expected_returns > 0).sum()
)

print(
    "Negative Forecasts :",
    (expected_returns < 0).sum()
)

volatility = (

    recent_returns

    .std(skipna=True)

    *

    np.sqrt(
        TRADING_DAYS
    )
)

expected_return_table = pd.DataFrame({

    "Symbol":
    expected_returns.index,

    "Expected_Return":
    expected_returns.values,

    "Volatility":
    volatility.values
})

# =========================================================
# MOMENTUM UNIVERSE FILTER
# =========================================================

expected_return_table = (
    expected_return_table
    .sort_values(
        "Expected_Return",
        ascending=False
    )
    .head(TOP_MOMENTUM_UNIVERSE)
    .copy()
)

# =========================================================
# HISTORY FILTER
# =========================================================

history_count = (

    returns_matrix

    .count()
)

history_filter = (

    history_count

    >=

    MIN_HISTORY_REQUIRED
)

valid_symbols = list(
    set(
        history_filter[
            history_filter
        ].index
    )
    &
    set(
        expected_return_table[
            "Symbol"
        ]
    )
)

expected_return_table = (

    expected_return_table[
        expected_return_table[
            "Symbol"
        ]
        .isin(
            valid_symbols
        )
    ]

    .copy()
)

returns_matrix = (

    returns_matrix[
        valid_symbols
    ]

    .copy()
)

covariance_matrix = (

    covariance_matrix

    .loc[
        valid_symbols,
        valid_symbols
    ]
)

print(
    f"Tradable Universe : "
    f"{len(valid_symbols):,}"
)

print(
    "\nFiltered Expected Return Distribution:"
)

print(
    expected_return_table[
        "Expected_Return"
    ].describe()
)

# =========================================================
# NUMPY OPTIMIZATION INPUTS
# =========================================================

mu = (

    expected_return_table

    .set_index(
        "Symbol"
    )

    .loc[
        valid_symbols,
        "Expected_Return"
    ]

    .values
)

Sigma = (
    covariance_matrix
    .values
)

asset_symbols = (
    valid_symbols
)

num_assets = len(
    asset_symbols
)

print(
    f"Assets Loaded : "
    f"{num_assets:,}"
)

# =========================================================
# BASIC DIAGNOSTICS
# =========================================================

print(
    "\nOptimization Diagnostics:"
)

print(
    f"Mean Return : "
    f"{expected_return_table['Expected_Return'].mean():.2%}"
)

print(
    f"Mean Volatility : "
    f"{volatility.mean():.2%}"
)

print(
    f"Covariance Shape : "
    f"{Sigma.shape}"
)

# =========================================================
# AUDIT CONTAINER
# =========================================================

audit_metrics = {}

audit_metrics[
    "Universe_Size"
] = len(
    common_symbols
)

audit_metrics[
    "Tradable_Universe"
] = num_assets

audit_metrics[
    "Risk_Free_Rate"
] = RISK_FREE_RATE

audit_metrics[
    "Engine_Version"
] = ENGINE_VERSION

# =========================================================
# PART 2 STARTS HERE
# =========================================================

#
# Minimum Variance Portfolio
#
# Risk Parity Portfolio
#
# =========================================================

# =========================================================
# MINIMUM VARIANCE PORTFOLIO
# =========================================================

print(
    "\n🏗 Building Minimum Variance Portfolio..."
)

diag = np.diag(Sigma)

diag = np.maximum(
    diag,
    1e-12
)

inverse_variance = (
    1.0 / diag
)

min_var_weights = (

    inverse_variance

    /

    inverse_variance.sum()
)

min_var_weights = np.clip(

    min_var_weights,

    MIN_POSITION_WEIGHT,

    MAX_POSITION_WEIGHT
)

min_var_weights = (

    min_var_weights

    /

    min_var_weights.sum()
)

# =========================================================
# REMOVE DUST POSITIONS
# =========================================================

min_var_weights = np.where(

    min_var_weights >= MIN_ACTIVE_WEIGHT,

    min_var_weights,

    0
)

min_var_weights = (

    min_var_weights

    /

    min_var_weights.sum()
)

# =========================================================
# MIN VAR PORTFOLIO METRICS
# =========================================================

min_var_variance = float(

    min_var_weights.T

    @

    Sigma

    @

    min_var_weights
)

min_var_volatility = np.sqrt(
    min_var_variance
)

min_var_return = float(

    mu

    @

    min_var_weights
)

min_var_sharpe = (

    min_var_return

    -

    RISK_FREE_RATE

) / max(
    min_var_volatility,
    1e-12
)

print(
    f"Volatility : "
    f"{min_var_volatility:.2%}"
)

print(
    f"Return     : "
    f"{min_var_return:.2%}"
)

# =========================================================
# MIN VAR PORTFOLIO TABLE
# =========================================================

min_var_portfolio = pd.DataFrame({

    "Symbol":
    asset_symbols,

    "Weight":
    min_var_weights
})

min_var_portfolio = (

    min_var_portfolio

    .sort_values(
        "Weight",
        ascending=False
    )

    .head(
        TARGET_PORTFOLIO_SIZE
    )

    .reset_index(
        drop=True
    )
)

min_var_portfolio[
    "Weight"
] = (

    min_var_portfolio[
        "Weight"
    ]

    /

    min_var_portfolio[
        "Weight"
    ].sum()
)

# =========================================================
# MIN VAR RISK CONTRIBUTIONS
# =========================================================

min_var_marginal = (

    Sigma

    @

    min_var_weights
)

min_var_component = (

    min_var_weights

    *

    min_var_marginal

    /

    max(
        min_var_volatility,
        1e-12
    )
)

min_var_hhi = np.sum(
    (
        min_var_weights
    ) ** 2
)

min_var_effective_holdings = (

    1

    /

    max(
        min_var_hhi,
        1e-12
    )
)

# =========================================================
# RISK PARITY PORTFOLIO
# =========================================================

print(
    "\n⚖ Building Risk Parity Portfolio..."
)

asset_volatility = np.sqrt(
    np.diag(Sigma)
)

asset_volatility = np.maximum(
    asset_volatility,
    1e-12
)

risk_parity_weights = (

    1.0

    /

    asset_volatility
)

risk_parity_weights = (

    risk_parity_weights

    /

    risk_parity_weights.sum()
)

risk_parity_weights = np.clip(

    risk_parity_weights,

    MIN_POSITION_WEIGHT,

    MAX_POSITION_WEIGHT
)

risk_parity_weights = (

    risk_parity_weights

    /

    risk_parity_weights.sum()
)

risk_parity_weights = np.where(

    risk_parity_weights >= MIN_ACTIVE_WEIGHT,

    risk_parity_weights,

    0
)

risk_parity_weights = (

    risk_parity_weights

    /

    risk_parity_weights.sum()
)

# =========================================================
# RISK PARITY METRICS
# =========================================================

risk_parity_variance = float(

    risk_parity_weights.T

    @

    Sigma

    @

    risk_parity_weights
)

risk_parity_volatility = np.sqrt(
    risk_parity_variance
)

risk_parity_return = float(

    mu

    @

    risk_parity_weights
)

risk_parity_sharpe = (

    risk_parity_return

    -

    RISK_FREE_RATE

) / max(
    risk_parity_volatility,
    1e-12
)

print(
    f"Volatility : "
    f"{risk_parity_volatility:.2%}"
)

print(
    f"Return     : "
    f"{risk_parity_return:.2%}"
)

# =========================================================
# RISK PARITY TABLE
# =========================================================

risk_parity_portfolio = pd.DataFrame({

    "Symbol":
    asset_symbols,

    "Weight":
    risk_parity_weights
})

risk_parity_portfolio = (

    risk_parity_portfolio

    .sort_values(
        "Weight",
        ascending=False
    )

    .head(
        TARGET_PORTFOLIO_SIZE
    )

    .reset_index(
        drop=True
    )
)

risk_parity_portfolio[
    "Weight"
] = (

    risk_parity_portfolio[
        "Weight"
    ]

    /

    risk_parity_portfolio[
        "Weight"
    ].sum()
)

# =========================================================
# RISK PARITY CONTRIBUTIONS
# =========================================================

risk_parity_marginal = (

    Sigma

    @

    risk_parity_weights
)

risk_parity_component = (

    risk_parity_weights

    *

    risk_parity_marginal

    /

    max(
        risk_parity_volatility,
        1e-12
    )
)

risk_parity_hhi = np.sum(
    (
        risk_parity_weights
    ) ** 2
)

risk_parity_effective_holdings = (

    1

    /

    max(
        risk_parity_hhi,
        1e-12
    )
)

# =========================================================
# STRATEGY COMPARISON
# =========================================================

strategy_comparison = pd.DataFrame({

    "Strategy": [

        "Minimum_Variance",

        "Risk_Parity"
    ],

    "Expected_Return": [

        min_var_return,

        risk_parity_return
    ],

    "Volatility": [

        min_var_volatility,

        risk_parity_volatility
    ],

    "Sharpe": [

        min_var_sharpe,

        risk_parity_sharpe
    ],

    "Effective_Holdings": [

        min_var_effective_holdings,

        risk_parity_effective_holdings
    ]
})

# =========================================================
# OUTPUT FILES
# =========================================================

MIN_VAR_FILE = (
    PORTFOLIO_DIR
    / "min_variance_portfolio.csv"
)

RISK_PARITY_FILE = (
    PORTFOLIO_DIR
    / "risk_parity_portfolio.csv"
)

# =========================================================
# SAVE INTERMEDIATE RESULTS
# =========================================================

min_var_portfolio.to_csv(

    MIN_VAR_FILE,

    index=False
)

risk_parity_portfolio.to_csv(

    RISK_PARITY_FILE,

    index=False
)

# =========================================================
# AUDIT METRICS
# =========================================================

audit_metrics[
    "MinVar_Return"
] = float(
    min_var_return
)

audit_metrics[
    "MinVar_Volatility"
] = float(
    min_var_volatility
)

audit_metrics[
    "RiskParity_Return"
] = float(
    risk_parity_return
)

audit_metrics[
    "RiskParity_Volatility"
] = float(
    risk_parity_volatility
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================

#
# Maximum Sharpe Portfolio
#
# Institutional Portfolio
#
# Portfolio Ranking
#
# =========================================================

# =========================================================
# MAXIMUM SHARPE PORTFOLIO
# =========================================================

print(
    "\n📈 Building Maximum Sharpe Portfolio..."
)

excess_returns = (
    mu
    -
    RISK_FREE_RATE
)

try:

    inv_sigma = np.linalg.pinv(
        Sigma
    )

except Exception:

    inv_sigma = np.linalg.pinv(
        Sigma + (
            np.eye(
                len(Sigma)
            )
            * 1e-8
        )
    )

max_sharpe_weights = (

    inv_sigma

    @

    excess_returns
)

max_sharpe_weights = np.maximum(
    max_sharpe_weights,
    0
)

if max_sharpe_weights.sum() <= 0:

    max_sharpe_weights = np.ones(
        len(asset_symbols)
    )

max_sharpe_weights = (

    max_sharpe_weights

    /

    max_sharpe_weights.sum()
)

max_sharpe_weights = np.clip(

    max_sharpe_weights,

    MIN_POSITION_WEIGHT,

    MAX_POSITION_WEIGHT
)

max_sharpe_weights = (

    max_sharpe_weights

    /

    max_sharpe_weights.sum()
)

# =========================================================
# REMOVE DUST POSITIONS
# =========================================================

max_sharpe_weights = np.where(

    max_sharpe_weights >= MIN_ACTIVE_WEIGHT,

    max_sharpe_weights,

    0
)

max_sharpe_weights = (

    max_sharpe_weights

    /

    max_sharpe_weights.sum()
)

# =========================================================
# MAX SHARPE METRICS
# =========================================================

max_sharpe_return = float(

    mu

    @

    max_sharpe_weights
)

max_sharpe_variance = float(

    max_sharpe_weights.T

    @

    Sigma

    @

    max_sharpe_weights
)

max_sharpe_volatility = np.sqrt(
    max_sharpe_variance
)

max_sharpe_ratio = (

    max_sharpe_return

    -

    RISK_FREE_RATE

) / max(
    max_sharpe_volatility,
    1e-12
)

print(
    f"Sharpe Ratio : "
    f"{max_sharpe_ratio:.2f}"
)

print(
    f"Volatility   : "
    f"{max_sharpe_volatility:.2%}"
)

# =========================================================
# MAX SHARPE PORTFOLIO
# =========================================================

max_sharpe_portfolio = pd.DataFrame({

    "Symbol":
    asset_symbols,

    "Weight":
    max_sharpe_weights
})

max_sharpe_portfolio = (

    max_sharpe_portfolio

    .sort_values(
        "Weight",
        ascending=False
    )

    .head(
        TARGET_PORTFOLIO_SIZE
    )

    .reset_index(
        drop=True
    )
)

max_sharpe_portfolio[
    "Weight"
] = (

    max_sharpe_portfolio[
        "Weight"
    ]

    /

    max_sharpe_portfolio[
        "Weight"
    ].sum()
)

# =========================================================
# INSTITUTIONAL PORTFOLIO
# =========================================================

print(
    "\n🏛 Building Institutional Portfolio..."
)

institutional_weights = (

    0.20 * min_var_weights

    +

    0.20 * risk_parity_weights

    +

    0.60 * max_sharpe_weights
)

institutional_weights = np.maximum(

    institutional_weights,

    0
)

institutional_weights = (

    institutional_weights

    /

    institutional_weights.sum()
)

institutional_weights = np.clip(

    institutional_weights,

    MIN_POSITION_WEIGHT,

    MAX_POSITION_WEIGHT
)

institutional_weights = (

    institutional_weights

    /

    institutional_weights.sum()
)

institutional_weights = np.where(

    institutional_weights >= MIN_ACTIVE_WEIGHT,

    institutional_weights,

    0
)

institutional_weights = (

    institutional_weights

    /

    institutional_weights.sum()
)

# =========================================================
# INSTITUTIONAL METRICS
# =========================================================

institutional_return = float(

    mu

    @

    institutional_weights
)

institutional_variance = float(

    institutional_weights.T

    @

    Sigma

    @

    institutional_weights
)

institutional_volatility = np.sqrt(
    institutional_variance
)

institutional_sharpe = (

    institutional_return

    -

    RISK_FREE_RATE

) / max(
    institutional_volatility,
    1e-12
)

print(
    f"Portfolio Volatility : "
    f"{institutional_volatility:.2%}"
)

print(
    f"Portfolio Return     : "
    f"{institutional_return:.2%}"
)

# =========================================================
# INSTITUTIONAL PORTFOLIO TABLE
# =========================================================

institutional_portfolio = pd.DataFrame({

    "Symbol":
    asset_symbols,

    "Weight":
    institutional_weights
})

institutional_portfolio = (

    institutional_portfolio

    .sort_values(
        "Weight",
        ascending=False
    )

    .head(
        TARGET_PORTFOLIO_SIZE
    )

    .reset_index(
        drop=True
    )
)

institutional_portfolio[
    "Weight"
] = (

    institutional_portfolio[
        "Weight"
    ]

    /

    institutional_portfolio[
        "Weight"
    ].sum()
)

# =========================================================
# STRATEGY RANKING
# =========================================================

strategy_comparison = pd.concat([

    strategy_comparison,

    pd.DataFrame({

        "Strategy": [

            "Maximum_Sharpe",

            "Institutional"
        ],

        "Expected_Return": [

            max_sharpe_return,

            institutional_return
        ],

        "Volatility": [

            max_sharpe_volatility,

            institutional_volatility
        ],

        "Sharpe": [

            max_sharpe_ratio,

            institutional_sharpe
        ],

        "Effective_Holdings": [

            1 / np.sum(
                max_sharpe_weights ** 2
            ),

            1 / np.sum(
                institutional_weights ** 2
            )
        ]
    })
])

strategy_comparison = (

    strategy_comparison

    .sort_values(
        "Sharpe",
        ascending=False
    )

    .reset_index(
        drop=True
    )
)

best_strategy = str(

    strategy_comparison

    .iloc[0]

    ["Strategy"]
)

print(
    f"Best Strategy : "
    f"{best_strategy}"
)

# =========================================================
# OUTPUT FILES
# =========================================================

MAX_SHARPE_FILE = (
    PORTFOLIO_DIR
    / "max_sharpe_portfolio.csv"
)

INSTITUTIONAL_FILE = (
    PORTFOLIO_DIR
    / "institutional_model_portfolio.csv"
)

STRATEGY_FILE = (
    PORTFOLIO_DIR
    / "strategy_comparison.csv"
)

# =========================================================
# SAVE RESULTS
# =========================================================

max_sharpe_portfolio.to_csv(

    MAX_SHARPE_FILE,

    index=False
)

institutional_portfolio.to_csv(

    INSTITUTIONAL_FILE,

    index=False
)

strategy_comparison.to_csv(

    STRATEGY_FILE,

    index=False
)

# =========================================================
# AUDIT METRICS
# =========================================================

audit_metrics[
    "MaxSharpe_Return"
] = float(
    max_sharpe_return
)

audit_metrics[
    "MaxSharpe_Volatility"
] = float(
    max_sharpe_volatility
)

audit_metrics[
    "MaxSharpe_Sharpe"
] = float(
    max_sharpe_ratio
)

audit_metrics[
    "Institutional_Return"
] = float(
    institutional_return
)

audit_metrics[
    "Institutional_Volatility"
] = float(
    institutional_volatility
)

audit_metrics[
    "Institutional_Sharpe"
] = float(
    institutional_sharpe
)

audit_metrics[
    "Best_Strategy"
] = best_strategy

# =========================================================
# PART 4 STARTS HERE
# =========================================================

#
# Optimizer Summary
# Audit Report
# Final Validation
# Export Layer
#
# =========================================================

# =========================================================
# OPTIMIZER SUMMARY
# =========================================================

print(
    "\n📊 Building Optimizer Summary..."
)

optimizer_summary = pd.DataFrame({

    "Strategy": [

        "Minimum_Variance",

        "Risk_Parity",

        "Maximum_Sharpe",

        "Institutional"
    ],

    "Expected_Return": [

        min_var_return,

        risk_parity_return,

        max_sharpe_return,

        institutional_return
    ],

    "Volatility": [

        min_var_volatility,

        risk_parity_volatility,

        max_sharpe_volatility,

        institutional_volatility
    ],

    "Sharpe": [

        min_var_sharpe,

        risk_parity_sharpe,

        max_sharpe_ratio,

        institutional_sharpe
    ]
})

optimizer_summary[
    "Return_to_Risk"
] = (

    optimizer_summary[
        "Expected_Return"
    ]

    /

    np.maximum(
        optimizer_summary[
            "Volatility"
        ],
        1e-12
    )
)

# =========================================================
# PORTFOLIO DIAGNOSTICS
# =========================================================

print(
    "🔍 Building Diagnostics..."
)

institutional_hhi = np.sum(
    institutional_weights ** 2
)

institutional_effective_holdings = (

    1

    /

    max(
        institutional_hhi,
        1e-12
    )
)

top10_weight = (

    institutional_portfolio

    .head(10)

    ["Weight"]

    .sum()
)

top5_weight = (

    institutional_portfolio

    .head(5)

    ["Weight"]

    .sum()
)

portfolio_diagnostics = pd.DataFrame({

    "Metric": [

        "Assets",

        "Effective_Holdings",

        "Top5_Weight",

        "Top10_Weight",

        "Portfolio_Return",

        "Portfolio_Volatility",

        "Portfolio_Sharpe"
    ],

    "Value": [

        len(asset_symbols),

        institutional_effective_holdings,

        top5_weight,

        top10_weight,

        institutional_return,

        institutional_volatility,

        institutional_sharpe
    ]
})

# =========================================================
# FINAL VALIDATION
# =========================================================

print(
    "✔ Running Final Validation..."
)

validation_errors = []

for portfolio_name, weights_vector in [

    (
        "Minimum_Variance",
        min_var_weights
    ),

    (
        "Risk_Parity",
        risk_parity_weights
    ),

    (
        "Maximum_Sharpe",
        max_sharpe_weights
    ),

    (
        "Institutional",
        institutional_weights
    )

]:

    weight_sum = float(
        weights_vector.sum()
    )

    if not np.isclose(
        weight_sum,
        1.0,
        atol=1e-6
    ):

        validation_errors.append(
            f"{portfolio_name}: "
            f"weights != 1"
        )

    if np.any(
        weights_vector < -1e-9
    ):

        validation_errors.append(
            f"{portfolio_name}: "
            f"negative weights"
        )

if validation_errors:

    raise ValueError(
        "\n".join(
            validation_errors
        )
    )

# =========================================================
# BEST PORTFOLIO
# =========================================================

best_portfolio = (

    optimizer_summary

    .sort_values(
        "Sharpe",
        ascending=False
    )

    .iloc[0]
)

best_strategy = str(
    best_portfolio[
        "Strategy"
    ]
)

best_sharpe = float(
    best_portfolio[
        "Sharpe"
    ]
)

# =========================================================
# AUDIT REPORT
# =========================================================

audit_metrics[
    "Best_Strategy"
] = best_strategy

audit_metrics[
    "Best_Sharpe"
] = best_sharpe

audit_metrics[
    "Institutional_Return"
] = float(
    institutional_return
)

audit_metrics[
    "Institutional_Volatility"
] = float(
    institutional_volatility
)

audit_metrics[
    "Institutional_Effective_Holdings"
] = float(
    institutional_effective_holdings
)

audit_metrics[
    "Run_Date"
] = datetime.now().strftime(
    "%Y-%m-%d"
)

audit_report = pd.DataFrame({

    "Metric":
    list(
        audit_metrics.keys()
    ),

    "Value":
    list(
        audit_metrics.values()
    )
})

# =========================================================
# SAVE OUTPUTS
# =========================================================

print(
    "💾 Saving Outputs..."
)

optimizer_summary.to_csv(

    SUMMARY_FILE,

    index=False
)

portfolio_diagnostics.to_csv(

    PORTFOLIO_DIR
    / "portfolio_diagnostics.csv",

    index=False
)

audit_report.to_csv(

    AUDIT_FILE,

    index=False
)

# =========================================================
# COMPLETION REPORT
# =========================================================

print(
    "\n=========================================================="
)

print(
    "🏁 OPTIMIZER ENGINE COMPLETE"
)

print(
    "=========================================================="
)

print(
    f"Universe Size          : "
    f"{num_assets:,}"
)

print(
    f"Best Strategy          : "
    f"{best_strategy}"
)

print(
    f"Best Sharpe            : "
    f"{best_sharpe:.2f}"
)

print(
    f"Institutional Return   : "
    f"{institutional_return:.2%}"
)

print(
    f"Institutional Vol      : "
    f"{institutional_volatility:.2%}"
)

print(
    f"Effective Holdings     : "
    f"{institutional_effective_holdings:.2f}"
)

print(
    f"Top 5 Weight           : "
    f"{top5_weight:.2%}"
)

print(
    f"Top 10 Weight          : "
    f"{top10_weight:.2%}"
)

print(
    "\nOutput Directory:"
)

print(
    PORTFOLIO_DIR
)

print(
    "=========================================================="
)