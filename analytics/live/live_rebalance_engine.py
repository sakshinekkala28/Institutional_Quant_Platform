# =========================================================
# LIVE REBALANCE ENGINE V3.0
# PART 1 - CONFIGURATION
# =========================================================

from pathlib import Path
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

# =========================================================
# ENGINE
# =========================================================

ENGINE_VERSION = "3.0.0"

# =========================================================
# PORTFOLIO SETTINGS
# =========================================================

TARGET_HOLDINGS = 50

MAX_POSITION_WEIGHT = 0.04

STRONG_BUY_WEIGHT = 0.04

BUY_WEIGHT = 0.025

MIN_ORDER_CHANGE = 0.005

# =========================================================
# TURNOVER
# =========================================================

MAX_PORTFOLIO_TURNOVER = 0.35

# =========================================================
# RISK LIMITS
# =========================================================

MAX_SECTOR_DRIFT = 0.10

MAX_MARKET_CAP_DRIFT = 0.07

MAX_LIQUIDITY_DRIFT = 0.08

MAX_HHI = 0.05

MIN_EFFECTIVE_HOLDINGS = 30

MAX_POSITION_RISK = 0.15

MAX_SECTOR_WEIGHT = 0.20
RETENTION_MULTIPLIER = 20

# =========================================================
# BETA LIMITS
# =========================================================

DEFAULT_BETA = 1.0

MIN_PORTFOLIO_BETA = 0.80

MAX_PORTFOLIO_BETA = 1.20

BENCHMARK_BETA = 1.0

# =========================================================
# VOLATILITY
# =========================================================

DEFAULT_VOLATILITY = 0.25

# =========================================================
# EXECUTION
# =========================================================

MAX_ADV_USAGE = 0.10

MAX_NEW_POSITIONS = 10

MAX_EXIT_POSITIONS = 10

TOP_TRADE_BUCKET = 10

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT / "data/portfolios/live_portfolio.csv"
SIGNAL_FILE = ROOT / "data/signals/signal_master.csv"

REGIME_FILE = ROOT / "data/regime/market_regime.csv"

RISK_FILE = ROOT / "data/risk/risk_budget.csv"

CAPACITY_FILE = ROOT / "data/capacity/capacity_summary.csv"

COST_FILE = ROOT / "data/execution/portfolio_cost_summary.csv"

SECURITY_MASTER_FILE = ROOT / "data/raw/security_master.csv"

VOL_FILE = ROOT / "data/risk/stock_volatility.csv"

BETA_FILE = ROOT / "data/risk/stock_beta.csv"

COV_FILE = ROOT / "data/risk/shrinkage_covariance.parquet"

OUTPUT_DIR = ROOT / "data/live"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# PART 2 - UTILITIES
# =========================================================

def safe_load_csv(path):

    try:

        df = pd.read_csv(path)

        print(f"✓ Loaded: {path.name}")

        return df

    except Exception as e:

        print(
            f"⚠ Failed: {path.name} | {e}"
        )

        return pd.DataFrame()


def normalize_weights(df):

    total = df["Target_Weight"].sum()

    if total > 0:

        df["Target_Weight"] /= total

    return df


def validate_columns(
    df,
    required,
    file_name
):

    missing = [

        c

        for c in required

        if c not in df.columns

    ]

    if missing:

        raise ValueError(
            f"{file_name} missing {missing}"
        )


def calculate_hhi(weights):

    return (weights ** 2).sum()


def calculate_effective_holdings(weights):

    hhi = calculate_hhi(weights)

    return 1 / max(hhi, 1e-9)

# =========================================================
# PART 3 - DRIFT FUNCTIONS
# =========================================================

def calculate_market_cap_drift(
    portfolio,
    target
):

    current_mc = (

        portfolio["Weight"]

        * portfolio["Market_Cap"]

    ).sum()

    target_mc = (

        target["Target_Weight"]

        * target["Market_Cap"]

    ).sum()

    if current_mc <= 0:

        return np.nan

    return (
        target_mc
        /
        current_mc
    ) - 1


def calculate_liquidity_drift(
    portfolio,
    target
):

    current_adv = (
        portfolio["Weight"]
        *
        portfolio["ADV_20D"]
    ).sum()

    target_adv = (
        target["Target_Weight"]
        *
        target["ADV_20D"]
    ).sum()

    if current_adv <= 0:
        return np.nan

    return (
        target_adv
        /
        current_adv
    ) - 1

def calculate_drifts(
    portfolio,
    target
):

    return (

        calculate_market_cap_drift(
            portfolio,
            target
        ),

        calculate_liquidity_drift(
            portfolio,
            target
        )

    )

# =========================================================
# PART 4 - LOAD DATA
# =========================================================

print("\n📥 Loading Inputs...")

portfolio = safe_load_csv(
    PORTFOLIO_FILE
)

signals = safe_load_csv(
    SIGNAL_FILE
)

regime = safe_load_csv(
    REGIME_FILE
)

risk_budget = safe_load_csv(
    RISK_FILE
)

capacity = safe_load_csv(
    CAPACITY_FILE
)

cost = safe_load_csv(
    COST_FILE
)

security_master = safe_load_csv(
    SECURITY_MASTER_FILE
)


if "ADV" in security_master.columns and "ADV_20D" not in security_master.columns:
    security_master["ADV_20D"] = security_master["ADV"]
    

vol_df = safe_load_csv(
    VOL_FILE
)

portfolio = portfolio.merge(
    security_master[
        [
            "Symbol",
            "Sector",
            "Market_Cap",
            "ADV_20D"
        ]
    ],
    on="Symbol",
    how="left"
)

# ----------------------------------
# STANDARDIZE PORTFOLIO COLUMNS
# ----------------------------------

if "Sector_x" in portfolio.columns:
    portfolio["Sector"] = (
        portfolio["Sector_x"]
        .fillna(portfolio.get("Sector_y"))
    )

elif "Sector_y" in portfolio.columns:
    portfolio["Sector"] = portfolio["Sector_y"]

if "Market_Cap_x" in portfolio.columns:
    portfolio["Market_Cap"] = (
        portfolio["Market_Cap_x"]
        .fillna(portfolio.get("Market_Cap_y"))
    )

elif "Market_Cap_y" in portfolio.columns:
    portfolio["Market_Cap"] = portfolio["Market_Cap_y"]

if "ADV_20D_x" in portfolio.columns:
    portfolio["ADV_20D"] = (
        portfolio["ADV_20D_x"]
        .fillna(portfolio.get("ADV_20D_y"))
    )

elif "ADV_20D_y" in portfolio.columns:
    portfolio["ADV_20D"] = portfolio["ADV_20D_y"]

try:

    beta_df = pd.read_csv(
        BETA_FILE
    )

except:

    beta_df = pd.DataFrame(
        columns=[
            "Symbol",
            "Beta"
        ]
    )

validate_columns(
    portfolio,
    ["Symbol","Weight"],
    "Portfolio"
)

validate_columns(
    signals,
    [
        "Symbol",
        "Signal",
        "Signal_Score"
    ],
    "Signals"
)

# =========================================================
# PART 5 - PORTFOLIO BUILDER
# =========================================================

print("\n⚙ Building Target Portfolio...")

# ---------------------------------------------------------
# CURRENT PORTFOLIO
# ---------------------------------------------------------

current_weights = (

    portfolio[
        ["Symbol", "Weight"]
    ]

    .rename(
        columns={
            "Weight":
            "Current_Weight"
        }
    )

)

# ---------------------------------------------------------
# SIGNAL UNIVERSE
# ---------------------------------------------------------

target = signals.merge(

    current_weights,

    on="Symbol",

    how="left"

)

target["Current_Weight"] = (

    target["Current_Weight"]

    .fillna(0)

)

target["In_Portfolio"] = (

    target["Current_Weight"]

    > 0

)

# ---------------------------------------------------------
# SECURITY MASTER
# ---------------------------------------------------------

master_cols = [

    "Symbol",
    "Company_Name",
    "Sector",
    "Market_Cap",
    "ADV_20D"

]

target = target.merge(

    security_master[master_cols],

    on="Symbol",

    how="left",

    suffixes=("", "_master")

)

# ---------------------------------------------------------
# COLUMN STANDARDIZATION
# ---------------------------------------------------------

if "Sector_master" in target.columns:

    target["Sector"] = target["Sector"].fillna(
        target["Sector_master"]
    )

if "Market_Cap_master" in target.columns:

    target["Market_Cap"] = target["Market_Cap"].fillna(
        target["Market_Cap_master"]
    )

if "ADV_20D_master" in target.columns:

    target["ADV_20D"] = target["ADV_20D"].fillna(
        target["ADV_20D_master"]
    )

# Drop duplicate columns

target = target.loc[
    :,
    ~target.columns.str.endswith("_master")
]

# ---------------------------------------------------------
# VOLATILITY
# ---------------------------------------------------------

if len(vol_df) > 0:

    vol_cols = [

        c

        for c in vol_df.columns

        if "vol" in c.lower()

    ]

    if vol_cols:

        target = target.merge(

            vol_df[
                [
                    "Symbol",
                    vol_cols[0]
                ]
            ],

            on="Symbol",

            how="left"

        )

        target.rename(

            columns={
                vol_cols[0]:
                "Volatility_252D"
            },

            inplace=True

        )

else:

    target["Volatility_252D"] = (

        DEFAULT_VOLATILITY

    )

target["Volatility_252D"] = (

    target["Volatility_252D"]

    .fillna(
        DEFAULT_VOLATILITY
    )

)

# ---------------------------------------------------------
# BETA
# ---------------------------------------------------------

if len(beta_df) > 0:

    target = target.merge(

        beta_df,

        on="Symbol",

        how="left"

    )

else:

    target["Beta"] = DEFAULT_BETA

target["Beta"] = (

    target["Beta"]

    .fillna(
        DEFAULT_BETA
    )

)

# ---------------------------------------------------------
# COVERAGE CHECK
# ---------------------------------------------------------

print("\nDATA COVERAGE CHECK")

print(

    "Sector Coverage:",

    target["Sector"]
    .notna()
    .sum(),

    "/",

    len(target)

)

print(

    "Market Cap Coverage:",

    target["Market_Cap"]
    .notna()
    .sum(),

    "/",

    len(target)

)

print(

    "ADV Coverage:",

    target["ADV_20D"]
    .notna()
    .sum(),

    "/",

    len(target)

)

# =========================================================
# PART 6 - SCORE ENGINE
# =========================================================

print("\n📊 Calculating Scores...")

# ---------------------------------------------------------
# RISK ADJUSTED SCORE
# ---------------------------------------------------------

adv_rank = (
    target["ADV_20D"]
    .rank(pct=True)
)

target["Liquidity_Score"] = (
    adv_rank.clip(lower=0.10)
)

target["Risk_Adjusted_Score"] = (
    target["Signal_Score"]
    *
    target["Liquidity_Score"]
    *
    (target["Market_Cap"].rank(pct=True) ** 0.25)
    /
    target["Volatility_252D"]
)


target["Risk_Adjusted_Score"] = (

    target["Risk_Adjusted_Score"]

    .replace(
        [np.inf, -np.inf],
        np.nan
    )

    .fillna(0)

)

# ---------------------------------------------------------
# SELECTION SCORE
# ---------------------------------------------------------

target["Selection_Score"] = (
    target["Risk_Adjusted_Score"]
    +
    target["Current_Weight"] * RETENTION_MULTIPLIER
)

# ---------------------------------------------------------
# RANK
# ---------------------------------------------------------

MIN_ADV = (
    target["ADV_20D"]
    .quantile(0.25)
)

target = target[
    target["ADV_20D"]
    >= MIN_ADV
].copy()

target = target.sort_values(

    "Selection_Score",

    ascending=False

)

target["Rank"] = (

    np.arange(
        1,
        len(target) + 1
    )

)

# ---------------------------------------------------------
# TOP CANDIDATES
# ---------------------------------------------------------

target = target.head(

    TARGET_HOLDINGS

).copy()

print(

    f"Selected Holdings: "

    f"{len(target)}"

)

# =========================================================
# PART 7 - INITIAL WEIGHTS
# =========================================================

print("\n⚖ Assigning Weights...")

# ---------------------------------------------------------
# RAW SCORE WEIGHTS
# ---------------------------------------------------------

target["Risk_Adjusted_Score"] = (
    target["Selection_Score"]
    /
    target["Volatility_252D"]
)

target["Risk_Adjusted_Score"] = (
    target["Risk_Adjusted_Score"]
    .clip(lower=0)
)

target["Target_Weight"] = (
    target["Risk_Adjusted_Score"]
    /
    target["Risk_Adjusted_Score"].sum()
)

MAX_WEIGHT = 0.03

target["Target_Weight"] = np.minimum(
    target["Target_Weight"],
    MAX_WEIGHT
)

target["Target_Weight"] = (
    target["Target_Weight"]
    /
    target["Target_Weight"].sum()
)

# ---------------------------------------------------------
# MAX POSITION CAP
# ---------------------------------------------------------

target["Target_Weight"] = (

    target["Target_Weight"]

    .clip(

        upper=
        MAX_POSITION_WEIGHT

    )

)

target = normalize_weights(
    target
)

# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

print("\nLargest Positions")

print(

    target[
        [
            "Symbol",
            "Target_Weight"
        ]
    ]

    .sort_values(

        "Target_Weight",

        ascending=False

    )

    .head(10)

)

print(

    "\nPortfolio Weight:",

    round(

        target[
            "Target_Weight"
        ].sum(),

        4

    )

)

print(

    "Max Weight:",

    round(

        target[
            "Target_Weight"
        ].max(),

        4

    )

)

# =========================================================
# PART 8 - REGIME OVERLAY
# =========================================================

print("\n📈 Applying Regime Overlay...")

regime_name = "UNKNOWN"

if len(regime) > 0:

    regime_name = (

        regime.iloc[-1]

        .get(
            "Regime",
            "UNKNOWN"
        )

    )

print(

    "Current Regime:",

    regime_name

)

# ---------------------------------------------------------
# BEAR MARKET
# ---------------------------------------------------------

if "BEAR" in regime_name:

    target["Target_Weight"] *= 0.80

# ---------------------------------------------------------
# HIGH VOL
# ---------------------------------------------------------

elif "HIGH_VOL" in regime_name:

    target["Target_Weight"] *= 0.90

# ---------------------------------------------------------
# BULL
# ---------------------------------------------------------

elif "BULL" in regime_name:

    target["Target_Weight"] *= 1.05

target = normalize_weights(
    target
)

# =========================================================
# PART 9 - CAPACITY OVERLAY
# =========================================================

print("\n📦 Applying Capacity Overlay...")

capacity_score = 100

if len(capacity) > 0:

    capacity_score = (

        capacity.iloc[-1]

        .get(
            "Capacity_Score",
            100
        )

    )

print(

    "Capacity Score:",

    round(
        capacity_score,
        2
    )

)

# ---------------------------------------------------------
# CAPACITY SCALING
# ---------------------------------------------------------

if capacity_score < 50:

    scaling_factor = 0.80

elif capacity_score < 70:

    scaling_factor = 0.90

else:

    scaling_factor = 1.00

target["Target_Weight"] *= scaling_factor

target = normalize_weights(
    target
)

# =========================================================
# PART 10 - COST OVERLAY
# =========================================================

sector_weights = (
    target
    .groupby("Sector")
    ["Target_Weight"]
    .sum()
)

for sector in sector_weights.index:

    if sector_weights[sector] > MAX_SECTOR_WEIGHT:

        scale = (
            MAX_SECTOR_WEIGHT
            /
            sector_weights[sector]
        )

        mask = (
            target["Sector"]
            ==
            sector
        )

        target.loc[
            mask,
            "Target_Weight"
        ] *= scale

target["Target_Weight"] /= (
    target["Target_Weight"].sum()
)

print("\n💰 Applying Cost Overlay...")

avg_cost_bps = 0

if len(cost) > 0:

    avg_cost_bps = (

        cost.iloc[-1]

        .get(
            "Average_Cost_Bps",
            0
        )

    )

print(

    "Average Cost (bps):",

    round(
        avg_cost_bps,
        2
    )
)

# ---------------------------------------------------------
# COST PENALTY
# ---------------------------------------------------------

if avg_cost_bps > 50:

    target["Target_Weight"] *= 0.90

elif avg_cost_bps > 25:

    target["Target_Weight"] *= 0.95

target = normalize_weights(
    target
)

# =========================================================
# PART 11 - RISK BUDGET OVERLAY
# =========================================================

print("\n🛡 Applying Risk Budget Overlay...")

# ---------------------------------------------------------
# VOLATILITY ADJUSTMENT
# ---------------------------------------------------------

vol_rank = (
    target["Volatility_252D"]
    .rank(pct=True)
)

target["Risk_Budget_Score"] = (
    target["Target_Weight"]
    *
    (1 - 0.50 * vol_rank)
)

target["Risk_Budget_Score"] = (
    target["Risk_Budget_Score"]
    .clip(lower=0.0001)
)

target["Target_Weight"] = (
    target["Risk_Budget_Score"]
    /
    target["Risk_Budget_Score"].sum()
)

# =========================================================
# PART 12 - POSITION LIMITS
# =========================================================

print("\n📏 Applying Position Limits...")

for _ in range(10):

    excess = (

        target["Target_Weight"]

        > MAX_POSITION_WEIGHT

    )

    if not excess.any():

        break

    overflow = (

        target.loc[
            excess,
            "Target_Weight"
        ]

        - MAX_POSITION_WEIGHT

    ).sum()

    target.loc[
        excess,
        "Target_Weight"
    ] = MAX_POSITION_WEIGHT

    remaining = (

        ~excess
    )

    target.loc[
        remaining,
        "Target_Weight"
    ] += (

        overflow

        *

        target.loc[
            remaining,
            "Target_Weight"
        ]

        /

        target.loc[
            remaining,
            "Target_Weight"
        ].sum()

    )

target = normalize_weights(
    target
)

print(

    "Max Position:",

    round(

        target["Target_Weight"]

        .max(),

        4

    )

)


if "Sector" not in portfolio.columns:

    print("WARNING: Sector missing in portfolio")

    portfolio["Sector"] = "UNKNOWN"

if "Sector" not in target.columns:

    print("WARNING: Sector missing in target")

    target["Sector"] = "UNKNOWN"

# =========================================================
# PART 13 - SECTOR CONSTRAINT ENGINE
# =========================================================

print("\n🏛 Applying Sector Constraints...")

sector_weights = (

    target

    .groupby(
        "Sector"
    )["Target_Weight"]

    .sum()

)


for sector in sector_weights.index:

    sector_weight = (

        sector_weights[
            sector
        ]
    )

    if sector_weight > MAX_SECTOR_WEIGHT:

        scale = (

            MAX_SECTOR_WEIGHT

            /

            sector_weight

        )

        mask = (

            target["Sector"]

            == sector

        )

        target.loc[
            mask,
            "Target_Weight"
        ] *= scale

target = normalize_weights(
    target
)

benchmark_sector = (
    portfolio
    .groupby("Sector")["Weight"]
    .sum()
)

target_sector = (
    target.groupby("Sector")
    ["Target_Weight"]
    .sum()
)

for sector in target_sector.index:

    current_sector_weight = (
        benchmark_sector.get(
            sector,
            0
        )
    )

    desired = min(
        current_sector_weight + 0.05,
        MAX_SECTOR_WEIGHT
    )

    actual = (
        target_sector[sector]
    )

    if actual > desired:

        scale = (
            desired
            /
            actual
        )

        mask = (
            target["Sector"]
            == sector
        )

        target.loc[
            mask,
            "Target_Weight"
        ] *= scale

target = normalize_weights(
    target
)

benchmark_sector = (
    portfolio.groupby("Sector")["Weight"]
    .sum()
)

for sector in target_sector.index:

    benchmark = benchmark_sector.get(
        sector,
        0
    )

    upper_limit = benchmark + MAX_SECTOR_DRIFT

    actual = target_sector[sector]

    if actual > upper_limit:

        scale = upper_limit / actual

        target.loc[
            target["Sector"] == sector,
            "Target_Weight"
        ] *= scale

target = normalize_weights(target)

violating_sectors = []

for sector in target_sector.index:

    benchmark = benchmark_sector.get(sector, 0)

    drift = target_sector[sector] - benchmark

    if drift > MAX_SECTOR_DRIFT:

        violating_sectors.append(sector)

        scale = (
            (benchmark + MAX_SECTOR_DRIFT)
            / target_sector[sector]
        )

        target.loc[
            target["Sector"] == sector,
            "Target_Weight"
        ] *= scale

        drift_found = True

for _ in range(10):

    target_sector = (
        target.groupby("Sector")
        ["Target_Weight"]
        .sum()
    )

    drift_found = False

    for sector in target_sector.index:

        benchmark = benchmark_sector.get(
            sector,
            0
        )

        drift = (
            target_sector[sector]
            -
            benchmark
        )

        if drift > MAX_SECTOR_DRIFT:

            scale = (
                (benchmark + MAX_SECTOR_DRIFT)
                /
                target_sector[sector]
            )

            target.loc[
                target["Sector"] == sector,
                "Target_Weight"
            ] *= scale

            drift_found = True

    remaining_mask = ~target["Sector"].isin(
        violating_sectors
    )

    remaining_total = target.loc[
        remaining_mask,
        "Target_Weight"
    ].sum()

    target.loc[
        remaining_mask,
        "Target_Weight"
    ] *= (
        1.0 -
        target.loc[
            ~remaining_mask,
            "Target_Weight"
        ].sum()
    ) / remaining_total

    if not drift_found:
        break

# =========================================================
# PART 14 - MARKET CAP CONSTRAINT
# =========================================================

print("\n🏢 Applying Market Cap Constraint...")

for _ in range(20):

    market_cap_drift, _ = (

        calculate_drifts(
            portfolio,
            target
        )

    )

    if (

        abs(
            market_cap_drift
        )

        <=

        MAX_MARKET_CAP_DRIFT

    ):

        break

    large_caps = (

        target

        .nlargest(
            10,
            "Market_Cap"
        )

        .index

    )

    small_caps = (

        target

        .nsmallest(
            10,
            "Market_Cap"
        )

        .index

    )

    if market_cap_drift > 0:

        target.loc[
            large_caps,
            "Target_Weight"
        ] *= 0.80

        target.loc[
            small_caps,
            "Target_Weight"
        ] *= 1.20

    else:

        target.loc[
            large_caps,
            "Target_Weight"
        ] *= 1.05

        target.loc[
            small_caps,
            "Target_Weight"
        ] *= 0.95

    target = normalize_weights(
        target
    )

current_mc = (
    portfolio["Weight"]
    * portfolio["Market_Cap"]
).sum()

target_mc = (
    target["Target_Weight"]
    * target["Market_Cap"]
).sum()

print("\nMC DEBUG")
print("Current MC :", current_mc)
print("Target MC  :", target_mc)

print(

    "Market Cap Drift:",

    round(
        market_cap_drift * 100,
        2
    ),

    "%"
)

# =========================================================
# PART 15 - LIQUIDITY CONSTRAINT
# =========================================================

print("\n💧 Applying Liquidity Constraint...")

target["Liquidity_Adjustment"] = (
    target["ADV_20D"]
    /
    target["ADV_20D"].median()
)

target["Liquidity_Adjustment"] = (
    target["Liquidity_Adjustment"]
    .clip(0.7, 1.3)
)

target["Target_Weight"] *= (
    target["Liquidity_Adjustment"]
)

target = normalize_weights(target)

_, liquidity_drift = calculate_drifts(
    portfolio,
    target
)

print(
    "Liquidity Drift:",
    round(
        liquidity_drift * 100,
        2
    ),
    "%"
)


print("\nDEBUG TARGET PORTFOLIO")

print(
    target[
        [
            "Symbol",
            "Target_Weight",
            "Market_Cap",
            "ADV_20D",
            "Volatility_252D"
        ]
    ]
    .sort_values(
        "Target_Weight",
        ascending=False
    )
    .head(20)
)

print(
    "\nHHI PRE-RISK:",
    round(
        (target["Target_Weight"]**2).sum(),
        4
    )
)

print("\n🔒 FINAL POSITION LIMIT CHECK")

for _ in range(20):

    excess = (
        target["Target_Weight"] > MAX_POSITION_WEIGHT
    )

    if not excess.any():
        break

    overflow = (
        target.loc[excess, "Target_Weight"]
        - MAX_POSITION_WEIGHT
    ).sum()

    target.loc[
        excess,
        "Target_Weight"
    ] = MAX_POSITION_WEIGHT

    remaining = ~excess

    target.loc[
        remaining,
        "Target_Weight"
    ] += (
        overflow
        *
        target.loc[
            remaining,
            "Target_Weight"
        ]
        /
        target.loc[
            remaining,
            "Target_Weight"
        ].sum()
    )

target = normalize_weights(target)

print(
    "Final Max Weight:",
    round(
        target["Target_Weight"].max(),
        4
    )
)

# =========================================================
# PART 16 - TRADE GENERATION
# =========================================================

print("\n🔄 Generating Trades...")

trades = target.merge(
    current_weights,
    on="Symbol",
    how="left",
    suffixes=("","_Old")
)

trades["Current_Weight"] = (
    trades["Current_Weight"]
    .fillna(0)
)

trades["Weight_Change"] = (
    trades["Target_Weight"]
    -
    trades["Current_Weight"]
)

# ---------------------------------------------------------
# ACTION
# ---------------------------------------------------------

trades["Action"] = np.where(

    trades["Weight_Change"] > MIN_ORDER_CHANGE,

    "BUY",

    np.where(

        trades["Weight_Change"] < -MIN_ORDER_CHANGE,

        "SELL",

        "HOLD"

    )

)

# ====================================================
# TRANSACTION COST MODEL
# ====================================================

print("\n💸 Calculating Transaction Costs...")

trades["Trading_Cost_Bps"] = (
    5
    + trades["Weight_Change"].abs() * 10000 * 0.10
)

portfolio_cost_bps = (
    trades["Trading_Cost_Bps"]
    * trades["Weight_Change"].abs()
).sum()

print(
    f"Estimated Trading Cost: "
    f"{portfolio_cost_bps:.2f} bps"
)

# ---------------------------------------------------------
# TURNOVER
# ---------------------------------------------------------

portfolio_turnover = (

    trades["Weight_Change"]

    .abs()

    .sum()

    / 2

)

print(

    "Portfolio Turnover:",

    round(
        portfolio_turnover * 100,
        2
    ),

    "%"

)

# =========================================================
# PART 17 - TRADE PRIORITIZATION
# =========================================================

print("\n🎯 Prioritizing Trades...")

trades["Priority_Score"] = (

    trades["Signal_Score"]

    *

    trades["Weight_Change"]

    .abs()

)

trades["Execution_Rank"] = (

    trades["Priority_Score"]

    .rank(

        ascending=False,

        method="dense"

    )

)

trade_list = (

    trades

    .sort_values(

        "Priority_Score",

        ascending=False

    )

)

print(

    trade_list[

        [
            "Execution_Rank",
            "Symbol",
            "Action",
            "Priority_Score"
        ]

    ]

    .head(10)

)


# ---------------------------------------------------------
# TURNOVER REDUCTION FILTER
# ---------------------------------------------------------

if portfolio_turnover > MAX_PORTFOLIO_TURNOVER:

    threshold = (
        trades["Priority_Score"]
        .quantile(0.75)
    )

    low_priority = (
        trades["Priority_Score"]
        < threshold
    )

    trades.loc[
        low_priority,
        "Target_Weight"
    ] = trades.loc[
        low_priority,
        "Current_Weight"
    ]


trades["Weight_Change"] = (
    trades["Target_Weight"]
    -
    trades["Current_Weight"]
)

target = trades.copy()

target["Target_Weight"] /= (
    target["Target_Weight"].sum()
)

trades["Target_Weight"] = (
    target["Target_Weight"]
)

trades["Weight_Change"] = (
    trades["Target_Weight"]
    -
    trades["Current_Weight"]
)

portfolio_turnover = (
    trades["Weight_Change"]
    .abs()
    .sum()
    / 2
)

print(
    "Reduced Turnover:",
    round(portfolio_turnover * 100, 2),
    "%"
)

active_trades = trades[
    trades["Action"] != "HOLD"
]

print(
    "Trades Remaining:",
    len(active_trades)
)

for _ in range(10):

    excess = (
        target["Target_Weight"]
        > MAX_POSITION_WEIGHT
    )

    if not excess.any():
        break

    overflow = (
        target.loc[
            excess,
            "Target_Weight"
        ] - MAX_POSITION_WEIGHT
    ).sum()

    target.loc[
        excess,
        "Target_Weight"
    ] = MAX_POSITION_WEIGHT

    target.loc[
        ~excess,
        "Target_Weight"
    ] += (
        overflow
        *
        target.loc[
            ~excess,
            "Target_Weight"
        ]
        /
        target.loc[
            ~excess,
            "Target_Weight"
        ].sum()
    )

target = normalize_weights(target)

trade_list = (
    trades
    .sort_values(
        "Priority_Score",
        ascending=False
    )
)

# =========================================================
# PART 18 - COVARIANCE MODEL
# =========================================================

print("\n📈 Loading Covariance Model...")

target["Yahoo_Symbol"] = (
    target["Symbol"]
    .astype(str)
    .str.strip()
    + ".NS"
)

cov_matrix = None

try:

    cov_matrix = pd.read_parquet(
        COV_FILE
    )

    print(
        "✓ Covariance Loaded"
    )

except:

    print(
        "⚠ Covariance Missing"
    )

# =========================================================
# PART 19 - PORTFOLIO VOLATILITY
# =========================================================

portfolio_volatility = np.nan

if cov_matrix is not None:

    available = [

        s

        for s in target["Yahoo_Symbol"]

        if s in cov_matrix.index

    ]

    coverage = (

        len(available)

        /

        len(target)

    )

    print(

        "Covariance Coverage:",

        round(
            coverage * 100,
            2
        ),

        "%"

    )

    if len(available) >= 20:

        weights = (

            target

            .set_index(
                "Yahoo_Symbol"
            )

            .loc[
                available,
                "Target_Weight"
            ]

            .values

        )

        cov_sub = (

            cov_matrix

            .loc[
                available,
                available
            ]

            .values

        )

        variance = (

            weights.T

            @

            cov_sub

            @

            weights

        )

        portfolio_volatility = (

            np.sqrt(
                variance
            )
        )

if pd.isna(portfolio_volatility):

    portfolio_volatility = (

        np.sqrt(

            np.sum(

                (

                    target["Target_Weight"]

                    *

                    target["Volatility_252D"]

                ) ** 2

            )

        )

    )

print(

    "Portfolio Volatility:",

    round(
        portfolio_volatility * 100,
        2
    ),

    "%"

)

# =========================================================
# PART 20 - RISK CONTRIBUTIONS
# =========================================================

print("\n🛡 Calculating Risk Contributions...")

target["Risk_Contribution"] = (
    (
        target["Target_Weight"]
        *
        target["Volatility_252D"]
    ) ** 2
)

target["Risk_Contribution_Pct"] = (
    target["Risk_Contribution"]
    /
    target["Risk_Contribution"].sum()
)

total_risk = (

    target["Risk_Contribution"]

    .sum()
)

target["Risk_Contribution_Pct"] = (

    target["Risk_Contribution"]

    /

    total_risk

)

top_risk = (

    target

    .sort_values(

        "Risk_Contribution_Pct",

        ascending=False

    )

)

print(

    top_risk[
        [
            "Symbol",
            "Risk_Contribution_Pct"
        ]
    ]

    .head(10)

)

# =========================================================
# PART 21 - PORTFOLIO BETA
# =========================================================

portfolio_beta = (

    target["Target_Weight"]

    *

    target["Beta"]

).sum()

beta_drift = (

    portfolio_beta

    -

    BENCHMARK_BETA

)

beta_alignment = (

    max(

        0,

        100

        -

        abs(beta_drift)

        * 100

    )

)

print(

    "\nPortfolio Beta:",

    round(
        portfolio_beta,
        2
    )

)

print(

    "Beta Drift:",

    round(
        beta_drift,
        2
    )

)

# =========================================================
# PART 22 - EXPECTED RETURN
# =========================================================

target["Expected_Alpha"] = (
    target["Signal_Score"]
    / 100
) * 0.15

expected_return = (
    target["Target_Weight"]
    *
    target["Expected_Alpha"]
).sum()

if portfolio_volatility > 0:

    information_ratio = (

        expected_return

        /

        portfolio_volatility

    )

else:

    information_ratio = 0

print(

    "Expected Return:",

    round(
        expected_return * 100,
        2
    ),

    "%"

)

print(

    "Information Ratio:",

    round(
        information_ratio,
        2
    )

)

# =========================================================
# PART 23 - GOVERNANCE ENGINE
# =========================================================

print("\n🏛 Running Governance Checks...")

hhi = calculate_hhi(
    target["Target_Weight"]
)

effective_holdings = (
    calculate_effective_holdings(
        target["Target_Weight"]
    )
)

governance_status = "PASS"

if hhi > MAX_HHI:
    governance_status = "FAIL"

if (
    effective_holdings < MIN_EFFECTIVE_HOLDINGS
    and hhi > 0.04
):
    governance_status = "FAIL"

print(
    "Portfolio HHI:",
    round(hhi, 4)
)

print(
    "Effective Holdings:",
    round(effective_holdings, 2)
)

print(
    "Governance Status:",
    governance_status
)

target = normalize_weights(target)

target_sector = (
    target
    .groupby("Sector")
    ["Target_Weight"]
    .sum()
)

benchmark_sector = (
    portfolio
    .groupby("Sector")
    ["Weight"]
    .sum()
)

for _ in range(20):

    drift = (
        target_sector
        .sub(benchmark_sector, fill_value=0)
        .abs()
    )

    max_drift = drift.max()

    if max_drift <= MAX_SECTOR_DRIFT:
        break

    worst_sector = drift.idxmax()

    benchmark = benchmark_sector.get(
        worst_sector,
        0
    )

    actual = target_sector[worst_sector]

    scale = (
        benchmark + MAX_SECTOR_DRIFT
    ) / actual

    target.loc[
        target["Sector"] == worst_sector,
        "Target_Weight"
    ] *= scale

    target = normalize_weights(target)

    target_sector = (
        target
        .groupby("Sector")
        ["Target_Weight"]
        .sum()
    )

# Reapply final stock cap

for _ in range(20):

    excess = (
        target["Target_Weight"]
        > MAX_POSITION_WEIGHT
    )

    if not excess.any():
        break

    overflow = (
        target.loc[
            excess,
            "Target_Weight"
        ] - MAX_POSITION_WEIGHT
    ).sum()

    target.loc[
        excess,
        "Target_Weight"
    ] = MAX_POSITION_WEIGHT

    remaining = ~excess

    target.loc[
        remaining,
        "Target_Weight"
    ] += (
        overflow
        *
        target.loc[
            remaining,
            "Target_Weight"
        ]
        /
        target.loc[
            remaining,
            "Target_Weight"
        ].sum()
    )

target = normalize_weights(target)

print(
    "MAX TARGET WEIGHT DEBUG:",
    target["Target_Weight"].max()
)


# =========================================================
# DIVERSIFICATION REPAIR
# =========================================================

if (
    effective_holdings < MIN_EFFECTIVE_HOLDINGS
    and hhi > 0.04
):

    print("\n🔧 Repairing Diversification...")

    target["Target_Weight"] = np.minimum(
        target["Target_Weight"],
        0.035
    )

    target = normalize_weights(target)

    hhi = calculate_hhi(
        target["Target_Weight"]
    )

    effective_holdings = (
        calculate_effective_holdings(
            target["Target_Weight"]
        )
    )

    print(
        "Repaired Effective Holdings:",
        round(effective_holdings,2)
    )

# =========================================================
# PART 24 - RISK FLAGS
# =========================================================

print("\n🚨 Building Risk Flags...")

risk_flags = []

# ---------------------------------------------------------
# BETA
# ---------------------------------------------------------

if portfolio_beta > MAX_PORTFOLIO_BETA:

    risk_flags.append(
        "HIGH_BETA"
    )

if portfolio_beta < MIN_PORTFOLIO_BETA:

    risk_flags.append(
        "LOW_BETA"
    )

# ---------------------------------------------------------
# SECTOR
# ---------------------------------------------------------

current_sector = (
    portfolio.groupby("Sector")["Weight"]
    .sum()
)

target_sector = (
    target.groupby("Sector")["Target_Weight"]
    .sum()
)

sector_compare = pd.concat(
    [current_sector, target_sector],
    axis=1
).fillna(0)

sector_compare.columns = [
    "Current",
    "Target"
]

sector_compare["Drift"] = (
    sector_compare["Target"]
    -
    sector_compare["Current"]
).abs()

print("\nSECTOR DRIFT DEBUG")

print(
    sector_compare
    .sort_values(
        "Drift",
        ascending=False
    )
)

largest_sector_drift = (
    sector_compare["Drift"].max()
)

if largest_sector_drift > MAX_SECTOR_DRIFT:
    risk_flags.append("SECTOR_DRIFT")


if target["Target_Weight"].max() > (
    MAX_POSITION_WEIGHT + 1e-6
):

    risk_flags.append(
        "SINGLE_STOCK_RISK"
    )
    
# ---------------------------------------------------------
# MARKET CAP
# ---------------------------------------------------------

if abs(market_cap_drift) > MAX_MARKET_CAP_DRIFT:

    risk_flags.append(
        "MARKET_CAP_DRIFT"
    )

# ---------------------------------------------------------
# LIQUIDITY
# ---------------------------------------------------------

if abs(liquidity_drift) > MAX_LIQUIDITY_DRIFT:

    risk_flags.append(
        "LIQUIDITY_DRIFT"
    )

# ---------------------------------------------------------
# CONCENTRATION
# ---------------------------------------------------------

if hhi > MAX_HHI:

    risk_flags.append(
        "CONCENTRATION"
    )

if (
    effective_holdings < MIN_EFFECTIVE_HOLDINGS
    and hhi > 0.04
):

    risk_flags.append(
        "LOW_DIVERSIFICATION"
    )

# ---------------------------------------------------------
# POSITION RISK
# ---------------------------------------------------------

print(
    "Max Risk Contribution:",
    round(
        top_risk["Risk_Contribution_Pct"].max(),
        4
    )
)

print(
    "Risk Limit:",
    MAX_POSITION_RISK
)

if (

    top_risk[
        "Risk_Contribution_Pct"
    ].max()

    >

    MAX_POSITION_RISK

):

    risk_flags.append(
        "SINGLE_STOCK_RISK"
    )

print(
    "Risk Flags:",
    risk_flags
)

# =========================================================
# PART 25 - APPROVAL WORKFLOW
# =========================================================

print("\n📋 Approval Workflow...")

RISK_PENALTIES = {
    "SECTOR_DRIFT": 5,
    "MARKET_CAP_DRIFT": 10,
    "LIQUIDITY_DRIFT": 10,
    "CONCENTRATION": 20,
    "LOW_DIVERSIFICATION": 10,
    "SINGLE_STOCK_RISK": 15,
    "HIGH_BETA": 10,
    "LOW_BETA": 10
}

approval_score = 100

for flag in risk_flags:
    approval_score -= RISK_PENALTIES.get(flag, 5)

approval_score -= (

    max(
        0,
        portfolio_turnover
        -
        MAX_PORTFOLIO_TURNOVER
    ) * 100
)

approval_score = max(
    approval_score,
    0
)

# ----------------------------------
# GOVERNANCE OVERRIDE
# ----------------------------------

if governance_status == "FAIL":

    approval_status = "CONDITIONAL_APPROVAL"

    if approval_score < 70:
        approval_status = "REJECTED"

# ----------------------------------
# HARD TURNOVER CHECK
# ----------------------------------

if governance_status != "FAIL":

    if portfolio_turnover > MAX_PORTFOLIO_TURNOVER * 1.20:

        approval_status = "REJECTED"

    elif portfolio_turnover > MAX_PORTFOLIO_TURNOVER:

        approval_status = "CONDITIONAL_APPROVAL"

    else:

        if approval_score >= 85:

            approval_status = "APPROVED"

        elif approval_score >= 70:

            approval_status = "CONDITIONAL_APPROVAL"

        else:

            approval_status = "REJECTED"

print(
    "Approval Score:",
    round(
        approval_score,
        0
    )
)

print(
    "Approval Status:",
    approval_status
)
# =========================================================
# PART 26 - DASHBOARD DATA
# =========================================================

print("\n📊 Building Dashboard...")

dashboard = pd.DataFrame({

    "Metric": [

        "Portfolio Beta",
        "Portfolio Volatility",
        "Expected Return",
        "Information Ratio",
        "Turnover",
        "HHI",
        "Effective Holdings",
        "Approval Score"

    ],

    "Value": [

        portfolio_beta,

        portfolio_volatility,

        expected_return,

        information_ratio,

        portfolio_turnover,

        hhi,

        effective_holdings,

        approval_score

    ]

})

# =========================================================
# PART 27 - SAVE OUTPUTS
# =========================================================

print("\n💾 Saving Outputs...")

target.to_csv(

    OUTPUT_DIR
    /
    "target_portfolio.csv",

    index=False

)

trade_list.to_csv(

    OUTPUT_DIR
    /
    "trade_list.csv",

    index=False

)

dashboard.to_csv(

    OUTPUT_DIR
    /
    "rebalance_dashboard.csv",

    index=False

)

summary = pd.DataFrame({

    "Metric": [

        "Approval_Status",
        "Approval_Score",
        "Risk_Flag_Count",
        "Portfolio_Beta",
        "Portfolio_Volatility",
        "Expected_Return"

    ],

    "Value": [

        approval_status,

        approval_score,

        len(risk_flags),

        portfolio_beta,

        portfolio_volatility,

        expected_return

    ]

})

summary.to_csv(

    OUTPUT_DIR
    /
    "rebalance_summary.csv",

    index=False

)

print(
    "✓ Outputs Saved"
)

# =========================================================
# PART 28 - FINAL SUMMARY
# =========================================================

print("\n" + "=" * 80)
print("🏁 LIVE REBALANCE ENGINE V3 COMPLETE")
print("=" * 80)

print(
    f"Engine Version      : {ENGINE_VERSION}"
)

print(
    f"Target Holdings     : {len(target)}"
)

print(
    f"Portfolio Beta      : {portfolio_beta:.2f}"
)

print(
    f"Portfolio Volatility: {portfolio_volatility:.2%}"
)

print(
    f"Expected Return     : {expected_return:.2%}"
)

print(
    f"Information Ratio   : {information_ratio:.2f}"
)

print(
    f"Portfolio Turnover  : {portfolio_turnover:.2%}"
)

print(
    f"HHI                 : {hhi:.4f}"
)

print(
    f"Effective Holdings  : {effective_holdings:.2f}"
)

print(
    f"Approval Score      : {approval_score:.0f}"
)

print(
    f"Approval Status     : {approval_status}"
)

print(
    f"Risk Flags          : {len(risk_flags)}"
)

print(
    f"Output Directory    : {OUTPUT_DIR}"
)

print("=" * 80)