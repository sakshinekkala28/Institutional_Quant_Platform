"""
=========================================================
OPTIMIZER V2
=========================================================

Purpose:
Institutional Portfolio Optimization Engine

Features:
- Alpha Optimization
- Risk Penalty
- Sector Constraints
- Liquidity Constraints
- Capacity Constraints
- Turnover Constraints
- Efficient Frontier

Inputs:
data/factors/factor_master.csv
data/research/factor_rankings.csv
data/portfolios/live_portfolio.csv
data/portfolios/portfolio_history.csv
data/liquidity/capacity_analysis.csv

Outputs:
data/portfolios/optimized_portfolio_v2.csv
data/portfolios/optimizer_dashboard.csv
data/portfolios/optimizer_scorecard.csv
data/portfolios/optimizer_constraints.csv
data/portfolios/efficient_frontier.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIGURATION
# =========================================================

ENGINE_VERSION = "2.0.0"

TARGET_PORTFOLIO_SIZE = 50

MIN_WEIGHT = 0.01
MAX_WEIGHT = 0.05

MAX_SECTOR_WEIGHT = 0.20

MAX_TURNOVER = 0.30

TURNOVER_PENALTY_WEIGHT = 0.10

SECTOR_TOLERANCE = 0.001

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

FACTOR_MASTER_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_master.csv"
)

FACTOR_RANK_FILE = (
    ROOT
    / "data"
    / "research"
    / "factor_rankings.csv"
)

LIVE_PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "live_portfolio.csv"
)

PORTFOLIO_HISTORY_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "portfolio_history.csv"
)

CAPACITY_FILE = (
    ROOT
    / "data"
    / "liquidity"
    / "capacity_analysis.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "portfolios"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "optimizer_v2_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD DATA
# =========================================================

print(
    "\n📥 Loading Inputs..."
)

factor_master = pd.read_csv(
    FACTOR_MASTER_FILE
)

factor_rankings = pd.read_csv(
    FACTOR_RANK_FILE
)

live_portfolio = pd.read_csv(
    LIVE_PORTFOLIO_FILE
)

capacity_analysis = pd.read_csv(
    CAPACITY_FILE
)

# =========================================================
# OPTIONAL HISTORY
# =========================================================

if PORTFOLIO_HISTORY_FILE.exists():

    portfolio_history = pd.read_csv(
        PORTFOLIO_HISTORY_FILE
    )

else:

    portfolio_history = pd.DataFrame()

# =========================================================
# VALIDATION
# =========================================================

required_factor_master = [

    "Symbol",

    "Sector",

    "Market_Cap",

    "Momentum_1M",

    "Momentum_3M",

    "Momentum_6M",

    "Momentum_12M",

    "Volatility_20D",

    "Volatility_60D",

    "ADV_20D",

    "Dollar_Volume",
]

for col in required_factor_master:

    if col not in factor_master.columns:

        raise ValueError(
            f"Missing Factor Column: {col}"
        )

required_capacity = [
    "Symbol"
]

optional_capacity = [

    "Capacity_Multiple",

    "Capacity_NAV",

    "Crowding_Risk"
]

for col in required_capacity:

    if col not in capacity_analysis.columns:

        raise ValueError(
            f"Missing Capacity Column: {col}"
        )

# =========================================================
# BUILD UNIVERSE
# =========================================================

print(
    "\n🏗 Building Optimization Universe..."
)

universe = factor_master.copy()

# =========================================================
# FACTOR RANK MERGE
# =========================================================

if (

    not factor_rankings.empty

    and

    "Symbol"
    in factor_rankings.columns

):

    rank_cols = [

        c

        for c in factor_rankings.columns

        if c != "Symbol"
    ]

    universe = universe.merge(

        factor_rankings[
            ["Symbol"]
            +
            rank_cols
        ],

        on="Symbol",

        how="left"
    )

# =========================================================
# CAPACITY MERGE
# =========================================================

capacity_cols = [

    c

    for c in capacity_analysis.columns

    if c != "Symbol"
]

universe = universe.merge(

    capacity_analysis[
        ["Symbol"]
        +
        capacity_cols
    ],

    on="Symbol",

    how="left"
)

# ==========================================
# REMOVE DUPLICATE MERGE COLUMNS
# ==========================================

for col in universe.columns:

    if col.endswith("_x"):

        base_col = col[:-2]

        if base_col + "_y" in universe.columns:

            universe[base_col] = universe[col]

# Drop duplicate suffix columns

universe = universe[[
    c
    for c in universe.columns
    if not c.endswith("_x")
    and not c.endswith("_y")
]]

# =========================================================
# CLEANING
# =========================================================

numeric_cols = [

    "Market_Cap",

    "Momentum_1M",

    "Momentum_3M",

    "Momentum_6M",

    "Momentum_12M",

    "Volatility_20D",

    "Volatility_60D",

    "ADV_20D",

    "Dollar_Volume",
]

for col in numeric_cols:

    if col in universe.columns:

        universe[col] = pd.to_numeric(
            universe[col],
            errors="coerce"
        )

universe = universe.dropna(

    subset=[

        "Market_Cap",

        "ADV_20D",

        "Dollar_Volume",
    ]
)

# =========================================================
# ELIGIBILITY FILTERS
# =========================================================

print(
    "\n🔍 Applying Eligibility Rules..."
)

universe = universe[

    universe[
        "ADV_20D"
    ] > 0
]

universe = universe[

    universe[
        "Dollar_Volume"
    ] > 0
]

universe = universe[

    universe[
        "Market_Cap"
    ] > 0
]

# =========================================================
# CURRENT HOLDINGS
# =========================================================

current_symbols = set()

if (

    not live_portfolio.empty

    and

    "Symbol"
    in live_portfolio.columns

):

    current_symbols = set(

        live_portfolio[
            "Symbol"
        ]
    )

universe[
    "Current_Holding"
] = universe[
    "Symbol"
].isin(
    current_symbols
)

# =========================================================
# TURNOVER HISTORY
# =========================================================

historical_symbols = set()

if (

    not portfolio_history.empty

    and

    "Symbol"
    in portfolio_history.columns

):

    historical_symbols = set(

        portfolio_history[
            "Symbol"
        ]
    )

universe[
    "Historical_Holding"
] = universe[
    "Symbol"
].isin(
    historical_symbols
)

# =========================================================
# STORAGE
# =========================================================

optimizer_results = []

constraint_results = []

frontier_results = []

print(
    f"Universe Size : "
    f"{len(universe):,}"
)

print(
    f"Current Holdings : "
    f"{len(current_symbols):,}"
)

print(
    f"Historical Holdings : "
    f"{len(historical_symbols):,}"
)

# =========================================================
# PART 2 STARTS HERE
# =========================================================
#
# Next:
#
# Alpha Model
# Risk Model
# Composite Score
# Optimization Objective
#
# =========================================================

# =========================================================
# ALPHA MODEL
# =========================================================

print(
    "\n📈 Building Alpha Model..."
)

# ---------------------------------------------------------
# MOMENTUM SCORE
# ---------------------------------------------------------

universe[
    "Momentum_Score"
] = (

    universe[
        "Momentum_1M"
    ] * 0.10

    +

    universe[
        "Momentum_3M"
    ] * 0.20

    +

    universe[
        "Momentum_6M"
    ] * 0.30

    +

    universe[
        "Momentum_12M"
    ] * 0.40
)

# ---------------------------------------------------------
# RANK SCORE
# ---------------------------------------------------------

if "Alpha_Adjusted" in universe.columns:

    universe[
        "Rank_Score"
    ] = universe[
        "Alpha_Adjusted"
    ]

elif "Alpha_Score" in universe.columns:

    universe[
        "Rank_Score"
    ] = universe[
        "Alpha_Score"
    ]

elif "Rank" in universe.columns:

    universe[
        "Rank_Score"
    ] = (

        universe["Rank"].max()

        -

        universe["Rank"]

        +

        1
    )

else:

    universe[
        "Rank_Score"
    ] = (
        universe[
            "Momentum_Score"
        ]
    )

# ---------------------------------------------------------
# NORMALIZE ALPHA
# ---------------------------------------------------------

rank_std = max(
    universe[
        "Rank_Score"
    ].std(),
    1e-9
)

universe[
    "Alpha_Z"
] = (

    universe[
        "Rank_Score"
    ]

    -

    universe[
        "Rank_Score"
    ].mean()

) / rank_std

universe["Alpha_Z"] = (
    universe["Alpha_Z"]
    .clip(
        lower=-3,
        upper=3
    )
)

# =========================================================
# RISK MODEL
# =========================================================

print(
    "⚠ Building Risk Model..."
)

# ---------------------------------------------------------
# VOLATILITY SCORE
# ---------------------------------------------------------

universe[
    "Risk_Volatility"
] = (

    universe[
        "Volatility_20D"
    ]

    +

    universe[
        "Volatility_60D"
    ]

) / 2

# ---------------------------------------------------------
# DRAWDOWN SCORE
# ---------------------------------------------------------

if (
    "Max_Drawdown_252D"
    in universe.columns
):

    universe[
        "Risk_Drawdown"
    ] = (

        universe[
            "Max_Drawdown_252D"
        ]

        .abs()
    )

else:

    universe[
        "Risk_Drawdown"
    ] = 0

# ---------------------------------------------------------
# TOTAL RISK SCORE
# ---------------------------------------------------------

universe[
    "Risk_Score"
] = (

    universe[
        "Risk_Volatility"
    ] * 0.70

    +

    universe[
        "Risk_Drawdown"
    ] * 0.30
)

risk_std = max(
    universe[
        "Risk_Score"
    ].std(),
    1e-9
)

universe[
    "Risk_Z"
] = (

    universe[
        "Risk_Score"
    ]

    -

    universe[
        "Risk_Score"
    ].mean()

) / risk_std

# =========================================================
# LIQUIDITY MODEL
# =========================================================

print(
    "💧 Building Liquidity Model..."
)

universe[
    "Liquidity_Score"
] = (

    np.log1p(
        universe[
            "ADV_20D"
        ]
    )

    +

    np.log1p(
        universe[
            "Dollar_Volume"
        ]
    )

) / 2

liq_std = max(
    universe[
        "Liquidity_Score"
    ].std(),
    1e-9
)

universe[
    "Liquidity_Z"
] = (

    universe[
        "Liquidity_Score"
    ]

    -

    universe[
        "Liquidity_Score"
    ].mean()

) / liq_std

# =========================================================
# CAPACITY MODEL
# =========================================================

print(
    "🏭 Building Capacity Model..."
)

if "Capacity_Multiple" in universe.columns:

    print(
        universe[
            "Capacity_Multiple"
        ].describe()
    )

if (
    "Capacity_Multiple"
    in universe.columns
):

    universe[
        "Capacity_Score"
    ] = universe[
        "Capacity_Multiple"
    ]

else:

    universe[
        "Capacity_Score"
    ] = 1

cap_std = max(
    universe[
        "Capacity_Score"
    ].std(),
    1e-9
)

universe[
    "Capacity_Z"
] = (

    universe[
        "Capacity_Score"
    ]

    -

    universe[
        "Capacity_Score"
    ].mean()

) / cap_std

# =========================================================
# TURNOVER MODEL
# =========================================================

print(
    "🔄 Building Turnover Model..."
)

universe[
    "Turnover_Penalty"
] = np.where(

    universe[
        "Current_Holding"
    ],

    0,

    1
)

if len(
    historical_symbols
) > 0:

    universe[
        "Turnover_Penalty"
    ] += np.where(

        universe[
            "Historical_Holding"
        ],

        0,

        1
    )

# =========================================================
# PENALTIES
# =========================================================

universe[
    "Turnover_Cost"
] = (

    universe[
        "Turnover_Penalty"
    ]

    *

    TURNOVER_PENALTY_WEIGHT
)

# =========================================================
# OPTIMIZATION SCORE
# =========================================================

print(
    "\n🎯 Building Optimization Score..."
)

universe["Optimization_Score"] = (

    universe["Alpha_Z"]

    - 0.50 * universe["Risk_Z"]

    + 0.20 * universe["Liquidity_Z"]

    + 0.15 * universe["Capacity_Z"]

    - universe["Turnover_Cost"]

)

# =========================================================
# RANKING
# =========================================================

universe = (

    universe

    .sort_values(

        "Optimization_Score",

        ascending=False

    )

    .reset_index(
        drop=True
    )
)

universe[
    "Optimizer_Rank"
] = (
    universe.index + 1
)

# =========================================================
# CANDIDATE PORTFOLIO
# =========================================================

candidate_portfolio = (

    universe

    .head(
        TARGET_PORTFOLIO_SIZE
    )

    .copy()
)

# =========================================================
# SCORE DIAGNOSTICS
# =========================================================

print(
    f"Top Candidate : "
    f"{candidate_portfolio.iloc[0]['Symbol']}"
)

print(
    f"Best Score    : "
    f"{candidate_portfolio.iloc[0]['Optimization_Score']:.4f}"
)

print(
    f"Candidates    : "
    f"{len(candidate_portfolio)}"
)

# =========================================================
# FACTOR SUMMARY
# =========================================================

optimizer_factor_summary = pd.DataFrame({

    "Metric": [

        "Average_Alpha_Z",

        "Average_Risk_Z",

        "Average_Liquidity_Z",

        "Average_Capacity_Z",

        "Average_Optimization_Score",
    ],

    "Value": [

        candidate_portfolio[
            "Alpha_Z"
        ].mean(),

        candidate_portfolio[
            "Risk_Z"
        ].mean(),

        candidate_portfolio[
            "Liquidity_Z"
        ].mean(),

        candidate_portfolio[
            "Capacity_Z"
        ].mean(),

        candidate_portfolio[
            "Optimization_Score"
        ].mean(),
    ]
})

def enforce_sector_caps(df):

    tolerance = 1e-4

    for _ in range(100):

        sector_weights = (
            df.groupby("Sector")["Weight"]
            .sum()
        )

        max_sector = sector_weights.max()

        if max_sector <= (
            MAX_SECTOR_WEIGHT + tolerance
        ):
            break

        breached_sector = (
            sector_weights.idxmax()
        )

        mask = (
            df["Sector"]
            == breached_sector
        )

        excess = (
            max_sector
            - MAX_SECTOR_WEIGHT
        )

        sector_weight = (
            sector_weights[
                breached_sector
            ]
        )

        reduction_factor = (
            excess
            /
            sector_weight
        )

        df.loc[
            mask,
            "Weight"
        ] *= (
            1 - reduction_factor
        )

        remaining = (
            ~mask
        )

        redistribution = (
            excess
            *
            df.loc[
                remaining,
                "Weight"
            ]
            /
            df.loc[
                remaining,
                "Weight"
            ].sum()
        )

        df.loc[
            remaining,
            "Weight"
        ] += redistribution

    return df
def enforce_position_caps(df):

    max_iterations = 100

    for _ in range(max_iterations):

        max_weight = (
            df["Weight"].max()
        )

        if max_weight <= MAX_WEIGHT:
            break

        capped_mask = (
            df["Weight"]
            > MAX_WEIGHT
        )

        excess = (

            df.loc[
                capped_mask,
                "Weight"
            ]

            - MAX_WEIGHT

        ).sum()

        df.loc[
            capped_mask,
            "Weight"
        ] = MAX_WEIGHT

        remaining_mask = (
            ~capped_mask
        )

        redistribution = (

            excess

            *

            df.loc[
                remaining_mask,
                "Weight"
            ]

            /

            df.loc[
                remaining_mask,
                "Weight"
            ].sum()

        )

        df.loc[
            remaining_mask,
            "Weight"
        ] += redistribution

    return df

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Weight Optimization
# Sector Constraints
# Liquidity Constraints
# Capacity Constraints
# Turnover Constraints
#
# =========================================================

# =========================================================
# WEIGHT OPTIMIZATION
# =========================================================

print(
    "\n⚖ Building Optimized Weights..."
)

# ---------------------------------------------------------
# POSITIVE SCORE FILTER
# ---------------------------------------------------------

candidate_portfolio = (

    candidate_portfolio[
        candidate_portfolio[
            "Optimization_Score"
        ] > 0
    ]

    .copy()
)

if len(candidate_portfolio) < 20:

    raise ValueError(
        "Insufficient qualified candidates."
    )

# ---------------------------------------------------------
# RAW WEIGHTS
# ---------------------------------------------------------

candidate_portfolio[
    "Raw_Weight"
] = (

    candidate_portfolio[
        "Optimization_Score"
    ]

    /

    candidate_portfolio[
        "Optimization_Score"
    ].sum()
)

# =========================================================
# POSITION LIMITS
# =========================================================

candidate_portfolio[
    "Weight"
] = (

    candidate_portfolio[
        "Raw_Weight"
    ]

    .clip(

        lower=MIN_WEIGHT,

        upper=MAX_WEIGHT
    )
)

candidate_portfolio[
    "Weight"
] = (

    candidate_portfolio[
        "Weight"
    ]

    /

    candidate_portfolio[
        "Weight"
    ].sum()
)

# =========================================================
# SECTOR CONSTRAINTS
# =========================================================

print(
    "🏭 Applying Sector Constraints..."
)

sector_weights = (

    candidate_portfolio

    .groupby(
        "Sector"
    )

    [
        "Weight"
    ]

    .sum()
)

for sector in sector_weights.index:

    mask = (
        candidate_portfolio["Sector"]
        == sector
    )

    sector_total = (
        candidate_portfolio.loc[
            mask,
            "Weight"
        ].sum()
    )

    if sector_total > MAX_SECTOR_WEIGHT:

        candidate_portfolio.loc[
            mask,
            "Weight"
        ] *= (

            MAX_SECTOR_WEIGHT
            /
            sector_total

        )

# =========================================================
# FLOOR CHECK
# =========================================================

candidate_portfolio[
    "Weight"
] = (

    candidate_portfolio[
        "Weight"
    ]

    .clip(
        lower=MIN_WEIGHT
    )
)

candidate_portfolio[
    "Weight"
] = (

    candidate_portfolio[
        "Weight"
    ]

    /

    candidate_portfolio[
        "Weight"
    ].sum()
)

# =========================================================
# LIQUIDITY CONSTRAINTS
# =========================================================

print(
    "💧 Applying Liquidity Constraints..."
)

adv_cutoff = (

    candidate_portfolio[
        "ADV_20D"
    ]

    .quantile(
        0.20
    )
)

candidate_portfolio[
    "Liquidity_Flag"
] = (

    candidate_portfolio[
        "ADV_20D"
    ]

    <

    adv_cutoff
)

candidate_portfolio.loc[

    candidate_portfolio[
        "Liquidity_Flag"
    ],

    "Weight"

] *= 0.75

candidate_portfolio[
    "Weight"
] = (

    candidate_portfolio[
        "Weight"
    ]

    /

    candidate_portfolio[
        "Weight"
    ].sum()
)

# =========================================================
# CAPACITY CONSTRAINTS
# =========================================================

print(
    "🏭 Applying Capacity Constraints..."
)

if (
    "Capacity_Multiple"
    in candidate_portfolio.columns
):

    capacity_cutoff = (

        candidate_portfolio[
            "Capacity_Multiple"
        ]

        .quantile(
            0.20
        )
    )

    candidate_portfolio[
        "Capacity_Flag"
    ] = (

        candidate_portfolio[
            "Capacity_Multiple"
        ]

        <

        capacity_cutoff
    )

    candidate_portfolio.loc[

        candidate_portfolio[
            "Capacity_Flag"
        ],

        "Weight"

    ] *= 0.80

    candidate_portfolio[
        "Weight"
    ] = (

        candidate_portfolio[
            "Weight"
        ]

        /

        candidate_portfolio[
            "Weight"
        ].sum()
    )

else:

    candidate_portfolio[
        "Capacity_Flag"
    ] = False

# =========================================================
# TURNOVER CONSTRAINTS
# =========================================================

print(
    "🔄 Applying Turnover Controls..."
)

candidate_portfolio[
    "New_Position"
] = ~(

    candidate_portfolio[
        "Current_Holding"
    ]
)

new_weight = (

    candidate_portfolio.loc[

        candidate_portfolio[
            "New_Position"
        ],

        "Weight"

    ].sum()
)

if new_weight > MAX_TURNOVER:

    scaling_factor = (

        MAX_TURNOVER

        /

        new_weight
    )

    candidate_portfolio.loc[

        candidate_portfolio[
            "New_Position"
        ],

        "Weight"

    ] *= scaling_factor

    candidate_portfolio[
        "Weight"
    ] = (

        candidate_portfolio[
            "Weight"
        ]

        /

        candidate_portfolio[
            "Weight"
        ].sum()
    )

# =========================================================
# FINAL WEIGHT CLEANUP
# =========================================================

candidate_portfolio[
    "Weight"
] = (

    candidate_portfolio[
        "Weight"
    ]

    .clip(

        lower=MIN_WEIGHT,

        upper=MAX_WEIGHT
    )
)

candidate_portfolio[
    "Weight"
] = (

    candidate_portfolio[
        "Weight"
    ]

    /

    candidate_portfolio[
        "Weight"
    ].sum()
)

candidate_portfolio = (
    enforce_sector_caps(
        candidate_portfolio
    )
)

sector_summary = (

    candidate_portfolio

    .groupby("Sector")["Weight"]

    .sum()
)

print(
    sector_summary
    .sort_values(
        ascending=False
    )
)

# ==========================================
# FINAL CONSTRAINT PASS
# ==========================================

candidate_portfolio = (
    enforce_position_caps(
        candidate_portfolio
    )
)

# =========================================================
# SECTOR SUMMARY
# =========================================================

sector_summary = (

    candidate_portfolio

    .groupby(
        "Sector"
    )

    .agg({

        "Weight":
        "sum",

        "Symbol":
        "count"
    })

    .reset_index()

    .rename(columns={

        "Symbol":
        "Holdings"
    })
)

print(
    sector_summary
    .sort_values(
        "Weight",
        ascending=False
    )
    .head(10)
)

# =========================================================
# CONSTRAINT CHECKS
# =========================================================

constraint_results = pd.DataFrame({

    "Constraint": [

        "Min Weight",

        "Max Weight",

        "Sector Cap",

        "Turnover Cap",
    ],

    "Configured": [

        MIN_WEIGHT,

        MAX_WEIGHT,

        MAX_SECTOR_WEIGHT,

        MAX_TURNOVER,
    ],

    "Actual": [

        candidate_portfolio[
            "Weight"
        ].min(),

        candidate_portfolio[
            "Weight"
        ].max(),

        sector_summary[
            "Weight"
        ].max(),

        new_weight,
    ]
})

# =========================================================
# PORTFOLIO STATS
# =========================================================

expected_alpha = (

    candidate_portfolio[
        "Alpha_Z"
    ]

    .mean()
)

expected_risk = (
    candidate_portfolio[
        "Risk_Score"
    ]
    .mean()
)

expected_liquidity = (

    candidate_portfolio[
        "Liquidity_Z"
    ]

    .mean()
)

print(
    f"Final Holdings : "
    f"{len(candidate_portfolio)}"
)

print(
    f"Max Sector Weight : "
    f"{sector_summary['Weight'].max():.2%}"
)

print(
    f"Expected Alpha : "
    f"{expected_alpha:.4f}"
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# Efficient Frontier
# Portfolio Scorecard
# Dashboard
# Save Outputs
# Final Reporting
#
# =========================================================

# =========================================================
# EFFICIENT FRONTIER
# =========================================================

print(
    "\n📈 Building Efficient Frontier..."
)

frontier_results = []

base_return = max(
    expected_alpha,
    0.01
)

base_risk = max(
    abs(expected_risk),
    0.01
)

for risk_target in np.linspace(
    0.50,
    1.50,
    25
):

    portfolio_return = (
        base_return
        * risk_target
    )

    portfolio_volatility = (
        base_risk
        * risk_target
    )

    sharpe = (

        portfolio_return

        /

        max(
            portfolio_volatility,
            1e-9
        )
    )

    frontier_results.append({

        "Risk_Target":
        risk_target,

        "Expected_Return":
        portfolio_return,

        "Expected_Volatility":
        portfolio_volatility,

        "Expected_Sharpe":
        sharpe,
    })

efficient_frontier = pd.DataFrame(
    frontier_results
)

print(
    "\nNew Positions:"
)

print(

    candidate_portfolio[
        "New_Position"
    ]

    .value_counts()
)

# =========================================================
# PORTFOLIO METRICS
# =========================================================

portfolio_turnover = (

    candidate_portfolio.loc[

        candidate_portfolio[
            "New_Position"
        ],

        "Weight"

    ]

    .sum()
)

liquidity_score = (

    candidate_portfolio[
        "Liquidity_Z"
    ]

    .mean()
)

# =========================================================
# DIVERSIFICATION SCORE
# =========================================================

weight_hhi = (

    candidate_portfolio[
        "Weight"
    ]

    ** 2

).sum()

effective_positions = (

    1

    /

    max(
        weight_hhi,
        1e-9
    )
)

diversification_score = (

    effective_positions

    /

    TARGET_PORTFOLIO_SIZE

    * 100
)

diversification_score = min(
    diversification_score,
    100
)

# =========================================================
# CONCENTRATION SCORE
# =========================================================

concentration_score = (

    100

    -

    diversification_score
)

# =========================================================
# SECTOR CONCENTRATION
# =========================================================

sector_hhi = (

    sector_summary[
        "Weight"
    ]

    ** 2

).sum()

effective_sectors = (

    1

    /

    max(
        sector_hhi,
        1e-9
    )
)

# =========================================================
# OPTIMIZER SCORE
# =========================================================

Capacity_Score = (
    candidate_portfolio[
        "Capacity_Multiple"
    ]
    .rank(pct=True)
    .mean()
    * 100
)

optimizer_score = np.mean([

    diversification_score,

    100 - concentration_score,

    (liquidity_score + 3) / 6 * 100,

    Capacity_Score

])

optimizer_score = np.clip(
    optimizer_score,
    0,
    100
)

# =========================================================
# PORTFOLIO SCORECARD
# =========================================================

optimizer_scorecard = pd.DataFrame({

    "Metric": [

        "Expected_Alpha",

        "Expected_Risk",

        "Expected_Liquidity",

        "Expected_Capacity",

        "Portfolio_Turnover",

        "Effective_Positions",

        "Effective_Sectors",

        "Diversification_Score",

        "Concentration_Score",

        "Optimizer_Score",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        expected_alpha,

        expected_risk,

        expected_liquidity,

        Capacity_Score,

        portfolio_turnover,

        effective_positions,

        effective_sectors,

        diversification_score,

        concentration_score,

        optimizer_score,

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# OPTIMIZER DASHBOARD
# =========================================================

optimizer_dashboard = pd.DataFrame({

    "Category": [

        "Alpha",

        "Risk",

        "Liquidity",

        "Capacity",

        "Diversification",

        "Optimizer",
    ],

    "Score": [

        expected_alpha,

        expected_risk,

        liquidity_score,

        Capacity_Score,

        diversification_score,

        optimizer_score,
    ]
})

# =========================================================
# FINAL PORTFOLIO
# =========================================================

optimized_portfolio = (

    candidate_portfolio[[

        "Symbol",

        "Sector",

        "Weight",

        "Optimization_Score",

        "Alpha_Z",

        "Risk_Z",

        "Liquidity_Z",

        "Capacity_Z",

        "Current_Holding",
    ]]

    .copy()
)

optimized_portfolio = (

    optimized_portfolio

    .sort_values(
        "Weight",
        ascending=False
    )

    .reset_index(
        drop=True
    )
)

print(

    candidate_portfolio[
        [

            "Symbol",

            "Market_Cap",

            "Alpha_Z",

            "Risk_Score",

            "Weight"

        ]

    ]

    .head(10)
)

weight_sum = (
    candidate_portfolio["Weight"]
    .sum()
)

if abs(weight_sum - 1) > 1e-6:

    raise ValueError(
        f"Portfolio weights sum to {weight_sum}"
    )

if (
    sector_summary["Weight"].max()
    > MAX_SECTOR_WEIGHT + 0.001
):
    raise ValueError(
        "Sector cap breach detected."
    )


if (
    candidate_portfolio["Weight"].max()
    > MAX_WEIGHT + 0.001
):
    raise ValueError(
        "Position cap breach detected."
    )

# =========================================================
# SAVE OUTPUTS
# =========================================================

optimized_portfolio.to_csv(

    OUTPUT_DIR
    / "optimized_portfolio_v2.csv",

    index=False
)

optimizer_scorecard.to_csv(

    OUTPUT_DIR
    / "optimizer_scorecard.csv",

    index=False
)

optimizer_dashboard.to_csv(

    OUTPUT_DIR
    / "optimizer_dashboard.csv",

    index=False
)

constraint_results.to_csv(

    OUTPUT_DIR
    / "optimizer_constraints.csv",

    index=False
)

efficient_frontier.to_csv(

    OUTPUT_DIR
    / "efficient_frontier.csv",

    index=False
)

sector_summary.to_csv(

    OUTPUT_DIR
    / "optimizer_sector_summary.csv",

    index=False
)

optimizer_factor_summary.to_csv(

    OUTPUT_DIR
    / "optimizer_factor_summary.csv",

    index=False
)

optimizer_scorecard.to_csv(

    REPORT_FILE,

    index=False
)

# =========================================================
# FINAL REPORT
# =========================================================

print(
    "\n"
    + "=" * 70
)

print(
    "🏁 OPTIMIZER V2 COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Portfolio Holdings    : "
    f"{len(optimized_portfolio)}"
)

print(
    f"Expected Alpha        : "
    f"{expected_alpha:.4f}"
)

print(
    f"Expected Risk         : "
    f"{expected_risk:.4f}"
)

print(
    f"Liquidity Score       : "
    f"{liquidity_score:.4f}"
)

print(
    f"Capacity Score        : "
    f"{Capacity_Score:.4f}"
)

print(
    f"Portfolio Turnover    : "
    f"{portfolio_turnover:.2%}"
)

print(
    f"Effective Positions   : "
    f"{effective_positions:.2f}"
)

print(
    f"Effective Sectors     : "
    f"{effective_sectors:.2f}"
)

print(
    f"Diversification Score : "
    f"{diversification_score:.2f}"
)

print(
    f"Optimizer Score       : "
    f"{optimizer_score:.2f}"
)

print(
    f"\nLargest Position      : "
    f"{optimized_portfolio.iloc[0]['Symbol']}"
)

print(
    f"Largest Weight        : "
    f"{optimized_portfolio.iloc[0]['Weight']:.2%}"
)

print(
    f"\nOutput Directory:"
)

print(
    OUTPUT_DIR
)

print(
    "=" * 70
)