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

TARGET_HOLDINGS = 40

MIN_POSITION_WEIGHT= 0.0025

BASE_MAX_POSITION_WEIGHT = 0.05

MAX_POSITION_WEIGHT = 0.05

STRONG_BUY_WEIGHT = 0.04

BUY_WEIGHT = 0.03

MIN_ORDER_CHANGE = 0.005

# =========================================================
# TURNOVER
# =========================================================

PORTFOLIO_VALUE = 100000000

MAX_PORTFOLIO_TURNOVER = 0.40

# =========================================================
# RISK LIMITS
# =========================================================

MAX_SECTOR_DRIFT = 0.15

MAX_TRACKING_ERROR = 0.15

MAX_MARKET_CAP_DRIFT = 0.10

MAX_LIQUIDITY_DRIFT = 0.10

MAX_HHI = 0.05

MIN_EFFECTIVE_HOLDINGS = 20

MAX_POSITION_RISK = 0.20

MAX_SECTOR_WEIGHT = 0.30

RETENTION_MULTIPLIER = 0.10

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

# =====================================
# BLACK LITTERMAN
# =====================================

BL_ALPHA_WEIGHT = 0.90

BL_MARKET_WEIGHT = 0.10

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

BETA_FILE = ROOT / "data/risk/beta_master.csv"

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

def enforce_position_caps(
    df,
    MAX_POSITION_WEIGHT
):

    for _ in range(20):

        excess = (
            df["Target_Weight"]
            > MAX_POSITION_WEIGHT
        )

        if not excess.any():
            break

        overflow = (

            df.loc[
                excess,
                "Target_Weight"
            ]

            - MAX_POSITION_WEIGHT

        ).sum()

        df.loc[
            excess,
            "Target_Weight"
        ] = MAX_POSITION_WEIGHT

        remaining = ~excess

        df.loc[
            remaining,
            "Target_Weight"
        ] += (

            overflow

            *

            df.loc[
                remaining,
                "Target_Weight"
            ]

            /

            df.loc[
                remaining,
                "Target_Weight"
            ].sum()

        )

    return normalize_weights(df)

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

# =====================================
# STEP 19 - REGIME RISK BUDGET
# =====================================

if "BULL" in regime_name:

    REGIME_RISK_MULTIPLIER = 1.15

elif "BEAR" in regime_name:

    REGIME_RISK_MULTIPLIER = 0.75

else:

    REGIME_RISK_MULTIPLIER = 1.00

print(
    "Regime Risk Multiplier:",
    REGIME_RISK_MULTIPLIER
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

factor_master = pd.read_csv(
    ROOT
    / "data"
    / "factors"
    / "factor_master.csv"
)

print(
    "✓ Loaded: factor_master.csv"
)

fundamental_factor_master = pd.read_csv(

    ROOT
    / "data"
    / "factors"
    / "fundamental_factor_master.csv"

)

print(
    "✓ Loaded: fundamental_factor_master.csv"
)

MAX_POSITION_WEIGHT = (
    BASE_MAX_POSITION_WEIGHT
    * REGIME_RISK_MULTIPLIER
)

MAX_POSITION_RISK = (
    0.15
    * REGIME_RISK_MULTIPLIER
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

    print("\nBETA FILE LOADED")

    print(BETA_FILE)

    print(
        "\nBETA FILE EXISTS:",
        BETA_FILE.exists()
    )

    print(
        "BETA ROWS:",
        len(beta_df)
    )

    print(
        "BETA COLUMNS:",
        beta_df.columns.tolist()
    )

    print(beta_df.head())

    print(beta_df["Beta"].describe())

    print(
        "Unique Betas:",
        beta_df["Beta"].nunique()
    )

except Exception as e:

    print(
        "\nBETA LOAD FAILED"
    )

    print(e)

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


print("\nBETA DF CHECK")

print(
    beta_df.head()
)

print(
    beta_df["Beta"].describe()
)

print(
    "Unique Betas:",
    beta_df["Beta"].nunique()
)

print(
    "\nTARGET SYMBOLS"
)

print(
    target["Symbol"]
    .head(20)
)

#----------------------------------------------------------
# BETA
# ---------------------------------------------------------

if len(beta_df) > 0:

    target = target.merge(

        beta_df,

        on="Symbol",

        how="left"

    )

    print(
        "\nMERGED BETA SAMPLE"
    )

    print(

        target[
            [
                "Symbol",
                "Beta"
            ]
        ]

        .head(20)

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


target = target.merge(

    factor_master,

    on="Symbol",

    how="left"

)

target = target.merge(

    fundamental_factor_master,

    on="Symbol",

    how="left"

)

# =====================================
# STANDARDIZE FACTOR MERGE COLUMNS
# =====================================

if "ADV_20D_x" in target.columns:

    target["ADV_20D"] = (
        target["ADV_20D_x"]
        .fillna(target["ADV_20D_y"])
    )

if "Market_Cap_x" in target.columns:

    target["Market_Cap"] = (
        target["Market_Cap_x"]
        .fillna(target["Market_Cap_y"])
    )

if "Sector_x" in target.columns:

    target["Sector"] = (
        target["Sector_x"]
        .fillna(target["Sector_y"])
    )

target = target.drop(
    columns=[
        c
        for c in [
            "ADV_20D_x",
            "ADV_20D_y",
            "Market_Cap_x",
            "Market_Cap_y",
            "Sector_x",
            "Sector_y"
        ]
        if c in target.columns
    ]
)

# =========================================================
# PART 6 - SCORE ENGINE
# =========================================================

print("\n📊 Calculating Scores...")

# =====================================================
# SIGNAL FRESHNESS
# =====================================================

if "Signal_Date" in target.columns:

    target["Signal_Date"] = pd.to_datetime(
        target["Signal_Date"],
        errors="coerce"
    )

    signal_age = (
        pd.Timestamp.today()
        -
        target["Signal_Date"]
    ).dt.days

    target["Freshness_Factor"] = np.exp(
        -signal_age / 90
    )

else:

    target["Freshness_Factor"] = 1.0


# =====================================================
# MOMENTUM FACTOR
# =====================================================

momentum_cols = [

    "Momentum_1M",

    "Momentum_3M",

    "Momentum_6M",

    "Momentum_12M"

]

available_momentum = [

    c

    for c in momentum_cols

    if c in target.columns

]

if available_momentum:

    target["Momentum_Factor"] = (

        target[available_momentum]

        .rank(pct=True)

        .mean(axis=1)

    )

else:

    target["Momentum_Factor"] = 0.5


print("\nFACTOR MASTER CHECK")

print(

    target[
        [
            "Symbol",
            "Momentum_1M",
            "Momentum_3M",
            "Momentum_6M"
        ]
    ]

    .head()

)

print("\nTOP MOMENTUM STOCKS")

print(
    target[
        ["Symbol", "Momentum_Factor"]
    ]
    .sort_values(
        "Momentum_Factor",
        ascending=False
    )
    .head(10)
)

# =====================================================
# QUALITY FACTOR
# =====================================================
quality_cols = [

    "ROE",

    "ROCE",

    "Operating_Margin"

]

available_quality = [

    c

    for c in quality_cols

    if c in target.columns

    and

    target[c].notna().sum() > 20

]

if available_quality:

    target["Quality_Factor"] = (

        target[available_quality]

        .rank(pct=True)

        .mean(axis=1)

    )

else:

    target["Quality_Factor"] = 0.5

print("\nTOP QUALITY STOCKS")

print(
    target[
        ["Symbol", "Quality_Factor"]
    ]
    .sort_values(
        "Quality_Factor",
        ascending=False
    )
    .head(10)
)

# =====================================================
# VALUE FACTOR
# =====================================================

if "PE" in target.columns:

    valid_pe = target["PE"].where(
        target["PE"] > 0
    )

    inverse_pe = (
        1 / valid_pe
    )

    inverse_pe = inverse_pe.clip(
        lower=inverse_pe.quantile(0.01),
        upper=inverse_pe.quantile(0.99)
    )

    target["Value_Factor"] = (

        inverse_pe

        .rank(
            pct=True
        )

        .fillna(0.5)

    )

else:

    target["Value_Factor"] = 0.5

# =====================================================
# GROWTH FACTOR
# =====================================================

growth_cols = [

    "Revenue_Growth",

    "EPS_Growth",

    "Profit_Growth"

]

available_growth = [

    c

    for c in growth_cols

    if c in target.columns

]

if available_growth:

    target["Growth_Factor"] = (

        target[available_growth]

        .rank(pct=True)

        .mean(axis=1)

    )

else:

    target["Growth_Factor"] = 0.5

print("\nTOP GROWTH STOCKS")

print(

    target[
        ["Symbol", "Growth_Factor"]
    ]

    .sort_values(
        "Growth_Factor",
        ascending=False
    )

    .head(10)

)

print("\nAVAILABLE FACTOR COLUMNS")

print("\nFACTOR MASTER COLUMNS")

print(
    sorted(
        factor_master.columns.tolist()
    )
)

print(
    sorted(
        target.columns.tolist()
    )
)

# =====================================================
# FACTOR NORMALIZATION
# =====================================================

target["Signal_Factor"] = (
    target["Signal_Score"]
    .rank(pct=True)
)

target["Volatility_Factor"] = (
    1 -
    target["Volatility_252D"]
    .rank(pct=True)
)

# =====================================================
# BUILD MISSING FACTORS
# =====================================================

if "Liquidity_Score" not in target.columns:

    target["Liquidity_Score"] = (

        target["ADV_20D"]

        .rank(pct=True)

    )

if "Volatility_Factor" not in target.columns:

    target["Volatility_Factor"] = (

        1

        -

        target["Volatility_252D"]

        .rank(pct=True)

    )
    
# =====================================================
# FACTOR EXPOSURE FILE
# =====================================================

factor_exposures = target[[
    "Symbol",
    "Beta",
    "Momentum_Factor",
    "Quality_Factor",
    "Value_Factor",
    "Growth_Factor",
    "Liquidity_Score",
    "Volatility_Factor",
    "Sector"
]].copy()

factor_exposures.to_csv(

    ROOT
    / "data"
    / "risk"
    / "factor_exposures.csv",

    index=False

)

print(
    "✓ Saved factor_exposures.csv"
)

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

target["Liquidity_Penalty"] = (

    target["ADV_20D"]

    /

    target["ADV_20D"].quantile(0.75)

).clip(
    upper=1
)

target["Adjusted_Liquidity_Score"] = target["Liquidity_Score"] 

target["Adjusted_Liquidity_Score"] *= (

    target["Liquidity_Penalty"]

)

# =====================================
# REGIME FACTOR ROTATION
# =====================================

if "BULL" in regime_name:

    SIGNAL_W   = 0.20
    MOMENTUM_W = 0.25
    QUALITY_W  = 0.10
    VALUE_W    = 0.10
    GROWTH_W   = 0.25
    VOL_W      = 0.10

elif "BEAR" in regime_name:

    SIGNAL_W   = 0.20
    MOMENTUM_W = 0.10
    QUALITY_W  = 0.25
    VALUE_W    = 0.20
    GROWTH_W   = 0.10
    VOL_W      = 0.15

else:   # SIDEWAYS

    SIGNAL_W   = 0.25
    MOMENTUM_W = 0.20
    QUALITY_W  = 0.15
    VALUE_W    = 0.15
    GROWTH_W   = 0.15
    VOL_W      = 0.10

target["Composite_Alpha"] = (

      SIGNAL_W
      * target["Signal_Factor"]

    + MOMENTUM_W
      * target["Momentum_Factor"]

    + QUALITY_W
      * target["Quality_Factor"]

    + VALUE_W
      * target["Value_Factor"]

    + GROWTH_W
      * target["Growth_Factor"]

    + VOL_W
      * target["Volatility_Factor"]

)

#sector_mean = (
    #target.groupby("Sector")
    #["Composite_Alpha"]
    #.transform("mean")
#)

#target["Composite_Alpha"] = (
    #target["Composite_Alpha"]
    #-
    #sector_mean
#)

target["Composite_Alpha"] = (
    target["Composite_Alpha"]
    .rank(pct=True)
)

alpha_cutoff = (
    target["Composite_Alpha"]
    .quantile(0.50)
)

target = target[
    target["Composite_Alpha"]
    >= alpha_cutoff
].copy()


print(
    "\nALPHA BREADTH"
)

print(

    "Unique Alpha Scores:",

    target["Composite_Alpha"]

    .nunique()

)

print(
    "\n🎯 ALPHA CONCENTRATION"
)

print(

    "Alpha Std Dev:",

    round(

        target["Composite_Alpha"]

        .std(),

        4

    )

)

print(
    "\n🚀 TOP ALPHA STOCKS"
)

print(

    target[
        [
            "Symbol",
            "Composite_Alpha"
        ]
    ]

    .sort_values(
        "Composite_Alpha",
        ascending=False
    )

    .head(20)

)


# =====================================================
# SECTOR ALPHA ROTATION
# =====================================================

sector_alpha = (

    target
    .groupby("Sector")
    ["Composite_Alpha"]
    .mean()
)

sector_alpha = (

    sector_alpha
    .rank(pct=True)
)

target["Sector_Alpha"] = (
    target["Sector"]
    .map(sector_alpha)
)

print("\nTOP SECTOR ALPHA")

print(
    sector_alpha
    .sort_values(
        ascending=False
    )
)

sector_vol = (
    target
    .groupby("Sector")
    ["Volatility_252D"]
    .mean()
)

sector_risk_parity = (

    sector_alpha

    /

    np.sqrt(
        sector_vol
    )

)

sector_risk_parity = (
    sector_risk_parity
    /
    sector_risk_parity.sum()
)

print("\nSECTOR RISK PARITY")
print(
    sector_risk_parity
    .sort_values(
        ascending=False
    )
)

print("\n🏛 SECTOR CONCENTRATION CHECK")

sector_weights = (
    target.groupby("Sector")
    ["Market_Cap"]
    .count()
)

sector_hhi = (
    (
        sector_weights
        /
        sector_weights.sum()
    ) ** 2
).sum()

print(
    "Sector HHI:",
    round(
        sector_hhi,
        4
    )
)

target["Risk_Adjusted_Score"] = (

      target["Composite_Alpha"]

    * target["Liquidity_Score"]

    * (target["Market_Cap"].rank(pct=True) ** 0.25)

    * (0.80 + 0.40 * target["Sector_Alpha"])

)

target["Risk_Adjusted_Score"] = (

    target["Risk_Adjusted_Score"]

    .replace(
        [np.inf, -np.inf],
        np.nan
    )

    .fillna(0)

)

print("\nTOP COMPOSITE ALPHA")

print("\nFACTOR CORRELATION")

factor_cols = [

    "Momentum_Factor",

    "Quality_Factor",

    "Value_Factor",

    "Growth_Factor"

]

print(

    target[
        factor_cols
    ]

    .corr()

)

print("\nSECTOR DISTRIBUTION")

print(

    target
    .groupby("Sector")
    ["Composite_Alpha"]
    .mean()
    .sort_values(
        ascending=False
    )

)

print(
    target[
        ["Symbol","Composite_Alpha"]
    ]
    .sort_values(
        "Composite_Alpha",
        ascending=False
    )
    .head(15)
)

# ---------------------------------------------------------
# SELECTION SCORE
# ---------------------------------------------------------

# Sector diversification bonus

sector_count = (
    target["Sector"]
    .map(target["Sector"].value_counts())
)

target["Sector_Diversification_Bonus"] = (
    1 / np.sqrt(sector_count)
)

target["Selection_Score"] = (
    target["Risk_Adjusted_Score"]
    *
    target["Sector_Diversification_Bonus"]
    +
    target["Current_Weight"]
    * RETENTION_MULTIPLIER
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

# ==========================================
# PURE ALPHA SELECTION
# ==========================================

target = (

    target

    .sort_values(
        "Selection_Score",
        ascending=False
    )

    .head(
        TARGET_HOLDINGS
    )

    .copy()

)

if len(target) < TARGET_HOLDINGS:

    remaining = signals[
        ~signals["Symbol"].isin(target["Symbol"])
    ]

    remaining = remaining.merge(
        security_master,
        on="Symbol",
        how="left"
    )

    remaining = remaining.sort_values(
        "Signal_Score",
        ascending=False
    )

    needed = TARGET_HOLDINGS - len(target)

    target = pd.concat([
        target,
        remaining.head(needed)
    ])

target = (
    target
    .sort_values(
        "Selection_Score",
        ascending=False
    )
    .head(TARGET_HOLDINGS)
    .copy()
)


print(

    f"Selected Holdings: "

    f"{len(target)}"

)

# =========================================================
# PART 7 - INITIAL WEIGHTS
# =========================================================

print("\n⚖ Assigning Weights...")

# ==========================================
# VOLATILITY ADJUSTED ALPHA
# ==========================================

target["Risk_Adjusted_Score"] = (

    target["Selection_Score"]

    /

    np.sqrt(
        target["Volatility_252D"]
    )

)

# =====================================================
# LIQUIDITY SCALER
# =====================================================

target["Liquidity_Capacity"] = (

    target["ADV_20D"]

    /

    target["ADV_20D"].median()

)

target["Liquidity_Capacity"] = (

    target["Liquidity_Capacity"]

    .clip(
        lower=0.50,
        upper=2.00
    )

)

target["Risk_Adjusted_Score"] *= (

    target["Liquidity_Capacity"] ** 0.25

)

print("\nTOP WEIGHT CANDIDATES")

print(
    target[
        [
            "Symbol",
            "ADV_20D",
            "Liquidity_Capacity",
            "Selection_Score",
            "Volatility_252D",
            "Risk_Adjusted_Score"
        ]
    ]
    .sort_values(
        "Risk_Adjusted_Score",
        ascending=False
    )
    .head(15)
)

target["Risk_Adjusted_Score"] = (
    target["Risk_Adjusted_Score"]
    .clip(lower=0)
)

target["Risk_Parity_Score"] = (
    target["Risk_Adjusted_Score"]
    /
    target["Volatility_252D"]
)

target["Sector_Risk_Parity"] = (
    target["Sector"]
    .map(sector_risk_parity)
)

target["Risk_Parity_Score"] = (
    target["Risk_Parity_Score"]
    *
    target["Sector_Risk_Parity"]
)

target["Target_Weight"] = (
    target["Risk_Parity_Score"]
    /
    target["Risk_Parity_Score"].sum()
)

target["Position_Cap"] = np.where(
    target["Volatility_252D"] >
    target["Volatility_252D"].median(),
    0.05,
    0.07
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


# ---------------------------------------------------------
# PART 8 - BEAR MARKET
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

target = enforce_position_caps(
    target,
    MAX_POSITION_WEIGHT
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

target_sector = (
    target.groupby("Sector")
    ["Target_Weight"]
    .sum()
)

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


# =====================================================
# SECTOR DRIFT REPAIR
# =====================================================

if "Sector" in target.columns:

    sector_weights = (
        target.groupby("Sector")["Target_Weight"]
        .sum()
    )

    for sector in sector_weights.index:

        if sector_weights[sector] > MAX_SECTOR_WEIGHT:

            reduction_factor = (
                MAX_SECTOR_WEIGHT
                /
                sector_weights[sector]
            )

            target.loc[
                target["Sector"] == sector,
                "Target_Weight"
            ] *= reduction_factor

    target = normalize_weights(target)

    target_sector = (
        target.groupby("Sector")
        ["Target_Weight"]
        .sum()
    )

    print(
        "Max Sector Weight:",
        round(
            target.groupby("Sector")[
                "Target_Weight"
            ].sum().max(),
            4
        )
    )

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
    .clip(0.95, 1.05)
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

# =====================================================
# LIQUIDITY DRIFT REPAIR
# =====================================================

for _ in range(20):

    _, liquidity_drift = calculate_drifts(
        portfolio,
        target
    )

    if abs(liquidity_drift) <= MAX_LIQUIDITY_DRIFT:
        break

    liquid = (
        target
        .nlargest(10, "ADV_20D")
        .index
    )

    illiquid = (
        target
        .nsmallest(10, "ADV_20D")
        .index
    )

    if liquidity_drift > 0:

        target.loc[
            liquid,
            "Target_Weight"
        ] *= 0.95

        target.loc[
            illiquid,
            "Target_Weight"
        ] *= 1.05

    else:

        target.loc[
            liquid,
            "Target_Weight"
        ] *= 1.05

        target.loc[
            illiquid,
            "Target_Weight"
        ] *= 0.95

    target = normalize_weights(target)

target = enforce_position_caps(
    target,
    MAX_POSITION_WEIGHT
)

print(
    "Repaired Liquidity Drift:",
    round(liquidity_drift * 100, 2),
    "%"
)


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

print(
    "Final Max Weight:",
    round(
        target["Target_Weight"].max(),
        4
    )
)

print("\n📦 PORTFOLIO CAPACITY ANALYTICS")


target["Capacity_Days"] = (

    target["Target_Weight"]

    * PORTFOLIO_VALUE

    /

    (

        target["ADV_20D"]

        * MAX_ADV_USAGE

    )

)

print(
    "Median Exit Days:",
    round(
        target["Capacity_Days"].median(),
        2
    )
)

print(
    "Max Exit Days:",
    round(
        target["Capacity_Days"].max(),
        2
    )
)

print(
    target[
        [
            "Symbol",
            "Target_Weight",
            "ADV_20D",
            "Capacity_Days"
        ]
    ]
    .sort_values(
        "Capacity_Days",
        ascending=False
    )
    .head(10)
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

    # =====================================
    # COVARIANCE SHRINKAGE
    # =====================================

    diag = np.diag(
        np.diag(cov_matrix.values)
    )

    cov_matrix = pd.DataFrame(

        0.90 * cov_matrix.values

        +

        0.10 * diag,

        index=cov_matrix.index,
        columns=cov_matrix.columns

    )

    print(
        "✓ Covariance Loaded"
    )

except:

    print(
        "⚠ Covariance Missing"
    )
# =====================================
# STEP 17 - PSD COVARIANCE REPAIR
# =====================================

if cov_matrix is not None:

    eigvals, eigvecs = np.linalg.eigh(
        cov_matrix.values
    )

    eigvals = np.maximum(
        eigvals,
        1e-5
    )

    cov_matrix = pd.DataFrame(
        eigvecs
        @ np.diag(eigvals)
        @ eigvecs.T,
        index=cov_matrix.index,
        columns=cov_matrix.columns
    )

    print(
        "PSD Min Eigenvalue:",
        np.min(
            np.linalg.eigvals(
                cov_matrix.values
            )
        )
    )
    
# =========================================================
# PART 19 - PORTFOLIO VOLATILITY
# =========================================================

portfolio_volatility = 0.0

if cov_matrix is not None:

    available = []
    missing_cov = []

    for s in target["Yahoo_Symbol"]:

        if s in cov_matrix.index:

            available.append(s)

        else:

            missing_cov.append(s)

    # =====================================
    # SYNTHETIC COVARIANCE REPAIR
    # =====================================

    for s in missing_cov:

        if len(cov_matrix.index) > 0:

            proxy = (
                target
                .set_index("Yahoo_Symbol")
                .loc[s, "Volatility_252D"]
            )

            nearest = (

                target
                .loc[
                    target["Yahoo_Symbol"].isin(
                        cov_matrix.index
                    )
                ]

                .assign(
                    VolGap=lambda x:
                    abs(
                        x["Volatility_252D"]
                        - proxy
                    )
                )

                .sort_values(
                    "VolGap"
                )

                .iloc[0]

                ["Yahoo_Symbol"]

            )

            cov_matrix.loc[s] = (
                cov_matrix.loc[nearest]
            )

            cov_matrix[s] = (
                cov_matrix[nearest]
            )

            available.append(s)

    missing_cov = [
        s
        for s in target["Yahoo_Symbol"]
        if s not in available
    ]

    print(
        "\nMissing Covariance Stocks:",
        len(missing_cov)
    )

    if len(missing_cov) > 0:

        print(
            pd.Series(missing_cov).head(20)
        )

    coverage = (

        len(set(available))

        /

        len(target)

    )

    if coverage < 0.98:

        print(
            "\nWARNING: Covariance Coverage Below Institutional Threshold"
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

        diag_vol = np.sqrt(
            np.diag(cov_sub)
        )

        print(
            "Average Diagonal Vol:",
            diag_vol.mean()
        )

        print(
            "Max Diagonal Vol:",
            diag_vol.max()
        )

        print(
            "Min Diagonal Vol:",
            diag_vol.min()
        )

        portfolio_volatility = np.sqrt(variance)


target["Tail_Risk"] = (

    target["Volatility_252D"]

    *

    (
        1
        -
        target["Quality_Factor"]
    )

)

target["Target_Weight"] *= (

    1
    -
    0.20
    *
    target["Tail_Risk"]
)

target = normalize_weights(target)

# =====================================
# MARKET CAP EQUILIBRIUM WEIGHTS
# =====================================

market_weights = (

    target["Market_Cap"]

    /

    target["Market_Cap"].sum()

)

target["Market_Weight"] = market_weights

target_sector = (
    target.groupby("Sector")
    ["Target_Weight"]
    .sum()
)

print("\n⚙ Running Mean-Variance Optimizer...")


target["Diversification_Penalty"] = (

    target["Target_Weight"]

    ** 2

)

target["Risk_Parity_Score"] *= (

    1
    -
    target["Diversification_Penalty"]
)

target["Risk_Parity_Score"] = (
    target["Risk_Parity_Score"]
    .clip(lower=0)
)

# =====================================================
# MEAN VARIANCE OPTIMIZER
# =====================================================

if cov_matrix is not None and len(available) >= 20:

    # =====================================
    # BLACK-LITTERMAN EQUILIBRIUM RETURNS
    # =====================================

    RISK_AVERSION = 2.5

    market_weights = (

        target
        .set_index("Yahoo_Symbol")
        .loc[available, "Market_Weight"]
        .values

    )

    pi = (

        RISK_AVERSION

        *

        cov_sub

        @

        market_weights

    )

    alpha_vector = (

        target
        .set_index("Yahoo_Symbol")
        .loc[available, "Composite_Alpha"]
        .values

    )

    expected_returns = (

        BL_MARKET_WEIGHT * pi

        +

        BL_ALPHA_WEIGHT * alpha_vector

    )

    # =====================================
    # SECTOR CONCENTRATION PENALTY
    # =====================================

    sector_weights = (
        target.groupby("Sector")
        ["Market_Weight"]
        .transform("sum")
    )

    sector_concentration_penalty = (
        sector_weights
        .rank(pct=True)
    )

    expected_returns = (

        expected_returns

        -

        0.05
        * sector_concentration_penalty.values

    )

    # =====================================
    # BL CONFIDENCE SCALING
    # =====================================

    BL_CONFIDENCE = 1.0

    expected_returns = (

        pi

        +

        BL_CONFIDENCE

        *

        (

            expected_returns

            -

            pi

        )

    )

    inv_cov = np.linalg.pinv(cov_sub)

    risk_aversion = 5.0

    mv_weights = (
        inv_cov
        @
        expected_returns
    )

    mv_weights = (
        mv_weights
        /
        risk_aversion
    )

    mv_weights = np.maximum(
        mv_weights,
        0
    )

    print("\nBLACK-LITTERMAN PI RETURNS")

    print(
        pd.Series(
            pi,
            index=available
        )
        .sort_values(
            ascending=False
        )
        .head(15)
    )

    if mv_weights.sum() > 0:

        mv_weights = (
            mv_weights
            /
            mv_weights.sum()
        )

        mv_series = pd.Series(
            mv_weights,
            index=available
        )

        target["MV_Weight"] = (
            target["Yahoo_Symbol"]
            .map(mv_series)
            .fillna(0)
        )

        target["Market_Weight"] = (
            target["Market_Weight"]
            .fillna(0)
        )

        target["MV_Weight"] = (
            target["MV_Weight"]
            .fillna(0)
        )

        target["Target_Weight"] = (

            BL_MARKET_WEIGHT
            * target["Market_Weight"]

            +

            BL_ALPHA_WEIGHT
            * target["MV_Weight"]

        )

        target["Target_Weight"] = (
            target["Target_Weight"]
            .fillna(0)
        )

        target["Target_Weight"] = np.maximum(
            target["Target_Weight"],
            MIN_POSITION_WEIGHT
        )

        target = enforce_position_caps(
            target,
            MAX_POSITION_WEIGHT
        )

        print(
            "BL Holdings:",
            len(target)
        )

        # =====================================
        # MINIMUM POSITION FLOOR
        # =====================================

        print(
            "NaN Target Weights:",
            target["Target_Weight"]
            .isna()
            .sum()
        )

        print(
            "NaN MV Weights:",
            target["MV_Weight"]
            .isna()
            .sum()
        )

        print(
            "NaN Market Weights:",
            target["Market_Weight"]
            .isna()
            .sum()
        )

        print("\nBLACK-LITTERMAN TOP WEIGHTS")

        print(
            target[
                ["Symbol",
                 "Market_Weight",
                 "MV_Weight",
                 "Target_Weight"]
            ]
            .sort_values(
                "Target_Weight",
                ascending=False
            )
            .head(15)
        )

        print(
            "✓ Mean-Variance Optimization Applied"
        )
# =====================================================
# TRACKING ERROR CONSTRAINT
# =====================================================

print("\n🎯 Applying Tracking Error Constraint...")

benchmark_weights = (
    portfolio
    .set_index("Symbol")["Weight"]
)

target["Benchmark_Weight"] = (
    target["Symbol"]
    .map(benchmark_weights)
    .fillna(0)
)

weight_diff = (
    target["Target_Weight"]
    -
    target["Benchmark_Weight"]
)

active_weights = weight_diff.values

cov_te = (
    cov_matrix
    .loc[
        target["Yahoo_Symbol"],
        target["Yahoo_Symbol"]
    ]
    .values
)

tracking_error = np.sqrt(
    active_weights.T
    @ cov_te
    @ active_weights
)

print(
    "Pre-Constraint Tracking Error:",
    round(tracking_error * 100, 2),
    "%"
)

if tracking_error > MAX_TRACKING_ERROR:

    blend = (
        MAX_TRACKING_ERROR
        /
        tracking_error
    )

    for _ in range(50):

        if tracking_error <= MAX_TRACKING_ERROR:
            break

        target["Target_Weight"] = (

            blend
            * target["Target_Weight"]

            +

            (1 - blend)
            * target["Benchmark_Weight"]

        )

        target = normalize_weights(
            target
        )

        blend *= 0.95

print(
    "Post-Constraint Tracking Error:",
    round(tracking_error * 100, 2),
    "%"
)

# =====================================================
# FINAL INSTITUTIONAL CONSTRAINT PASS
# =====================================================

print("\n🏦 Final Constraint Pass...")

print(
    "Final Max Weight:",
    round(
        target["Target_Weight"].max(),
        4
    )
)


# =========================================================
# PART 20 - RISK CONTRIBUTIONS
# =========================================================

available = [
    s
    for s in target["Yahoo_Symbol"]
    if s in cov_matrix.index
]

cov_sub = (
    cov_matrix
    .loc[available, available]
    .values
)

weights = (
    target
    .set_index("Yahoo_Symbol")
    .loc[available, "Target_Weight"]
    .values
)

weights = np.nan_to_num(
    weights,
    nan=0.0
)

weights = np.maximum(
    weights,
    0
)

if weights.sum() > 0:

    weights = (
        weights
        /
        weights.sum()
    )

print(
    "Weight Sum:",
    weights.sum()
)

print(
    "NaN Weights:",
    np.isnan(weights).sum()
)

print(
    "Min Weight:",
    weights.min()
)

print(
    "Max Weight:",
    weights.max()
)

eigvals, eigvecs = np.linalg.eigh(
    cov_sub
)

eigvals = np.maximum(
    eigvals,
    1e-5
)

cov_sub = (

    eigvecs
    @
    np.diag(eigvals)
    @
    eigvecs.T
)

portfolio_var = (
    weights.T
    @ cov_sub
    @ weights
)


print("\n🛡 Calculating Risk Contributions...")

# =====================================
# TRUE COVARIANCE RISK CONTRIBUTION
# =====================================

if cov_matrix is not None and len(available) >= 20:

    weights = (

        target
        .set_index("Yahoo_Symbol")
        .loc[available, "Target_Weight"]
        .values

    )

    target["Target_Weight"] = (
        target["Target_Weight"]
        .fillna(0)
    )

    #target = target[
        #target["Target_Weight"] > 0
    #].copy()
    
    valid_available = [

        s

        for s in available

        if s in target["Yahoo_Symbol"].values

    ]

    risk_weights_df = (

        target
        .set_index("Yahoo_Symbol")
        .loc[
            valid_available,
            ["Symbol", "Target_Weight"]
        ]

    )

    nan_count = (
        risk_weights_df["Target_Weight"]
        .isna()
        .sum()
    )

    print(
        "Risk Weight NaNs:",
        nan_count
    )

    weights = np.nan_to_num(
        weights,
        nan=0.0
    )

    weights = np.maximum(
        weights,
        0
    )

    weights = (
        target
        .set_index("Yahoo_Symbol")
        .loc[valid_available, "Target_Weight"]
        .values
    )

    cov_sub = (
        cov_matrix
        .loc[valid_available, valid_available]
        .values
    )

    eigvals, eigvecs = np.linalg.eigh(
        cov_sub
    )

    eigvals = np.maximum(
        eigvals,
        1e-5
    )

    cov_sub = (
        eigvecs
        @
        np.diag(eigvals)
        @
        eigvecs.T
    )

    portfolio_var = (
        weights.T
        @ cov_sub
        @ weights
    )

    portfolio_vol = np.sqrt(
        portfolio_var
    )

    portfolio_volatility = portfolio_vol

    print(
        portfolio_volatility
    )

    print(
        "Portfolio Variance:",
        portfolio_var
    )

    print(
        "Portfolio Vol:",
        portfolio_vol
    )

    print(
        "NaNs In Covariance:",
        np.isnan(cov_sub).sum()
    )

    print(
        "NaNs In Weights:",
        np.isnan(weights).sum()
    )

    eigvals = np.linalg.eigh(
        cov_sub
    )[0]

    print(
        "Min Eigenvalue:",
        float(
            eigvals.min()
        )
    )
    
    marginal_risk = (
        cov_sub @ weights
    ) / portfolio_vol

    component_risk = (
        weights * marginal_risk
    )

    total_risk = component_risk.sum()

    if total_risk <= 0:

        risk_pct = np.repeat(
            1 / len(component_risk),
            len(component_risk)
        )

    else:

        risk_pct = component_risk / total_risk

    rc_df = pd.DataFrame({

        "Yahoo_Symbol": valid_available,
        "Risk_Contribution_Pct": risk_pct

    })

    target = target.merge(
        rc_df,
        on="Yahoo_Symbol",
        how="left"
    )
    # =====================================
    # STEP 15 - COVARIANCE RISK VALIDATION
    # =====================================

    print(
        "\n🔍 RISK MODEL VALIDATION"
    )

    coverage_symbols = set(
        target["Yahoo_Symbol"]
    )

    coverage = (

        len(
            coverage_symbols.intersection(
                set(cov_matrix.index)
            )
        )

        /

        len(coverage_symbols)

    )

    print(
        "Covariance Coverage:",
        round(
            coverage * 100,
            2
        ),
        "%"
    )

    print(
        "Weight Sum:",
        round(
            weights.sum(),
            6
        )
    )

    print(
        "Portfolio Volatility:",
        round(
            portfolio_vol * 100,
            2
        ),
        "%"
    )

    print(
        "Max Risk Contribution:",
        round(
            target["Risk_Contribution_Pct"]
            .max()
             * 100,
             2
        ),
        "%"
    )

else:

    target["Risk_Contribution_Pct"] = (
        (
            target["Target_Weight"]
            *
            target["Volatility_252D"]
        ) ** 2
    )

    target["Risk_Contribution_Pct"] /= (
        target["Risk_Contribution_Pct"].sum()
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

# =====================================================
# RISK CONTRIBUTION REBALANCER
# =====================================================

# Recalculate final risk contribution

max_risk_contribution = (
    target["Risk_Contribution_Pct"]
    .max()
)

print(
    "Max Risk Contribution:",
    round(
        max_risk_contribution,
        4
    )
)

# =====================================
# RISK CONTRIBUTION REBALANCER
# =====================================

print("\nFINAL BETA CHECK")

print(
    target[
        [
            "Symbol",
            "Beta",
            "Target_Weight"
        ]
    ]
    .head(20)
)

print(
    target["Beta"].describe()
)

print(
    "Unique Betas:",
    target["Beta"].nunique()
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
        4
    )

)

print(

    "Beta Drift:",

    round(
        beta_drift,
        2
    )

)

if portfolio_beta > MAX_PORTFOLIO_BETA:

    target["Target_Weight"] *= (
        1
        -
        (
            target["Beta"]
            /
            target["Beta"].max()
        )
        * 0.05
    )

elif portfolio_beta < MIN_PORTFOLIO_BETA:

    target["Target_Weight"] *= (
        1
        +
        (
            target["Beta"]
            /
            target["Beta"].max()
        )
        * 0.05
    )

target = normalize_weights(target)

# =========================================================
# PART 22 - EXPECTED RETURN
# =========================================================

target["Expected_Alpha"] = (

      0.04 * target["Signal_Factor"]

    + 0.03 * target["Momentum_Factor"]

    + 0.02 * target["Quality_Factor"]

    + 0.02 * target["Growth_Factor"]

    + 0.01 * target["Value_Factor"]

)

expected_return = (
    target["Target_Weight"]
    *
    target["Expected_Alpha"]
).sum()

expected_return = (
    expected_return
    *
    REGIME_RISK_MULTIPLIER
)

print(
    "IR VOL INPUT:",
    portfolio_volatility
)

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

print("\n🚨 TAIL RISK ANALYTICS")

portfolio_returns = (

    target["Expected_Alpha"].fillna(0)

    -

    target["Volatility_252D"].fillna(
        DEFAULT_VOLATILITY
    )

)

var95 = np.percentile(
    portfolio_returns,
    5
)

cvar95 = portfolio_returns[
    portfolio_returns <= var95
].mean()

print(
    "VaR 95%:",
    round(
        var95 * 100,
        2
    ),
    "%"
)

print(
    "CVaR 95%:",
    round(
        cvar95 * 100,
        2
    ),
    "%"
)

# =====================================
# STEP 16 - ACTIVE SHARE ANALYTICS
# =====================================

benchmark_weights = (

    target["Benchmark_Weight"]

    .fillna(0)

)

active_share = (

    0.5

    *

    np.abs(

        target["Target_Weight"]

        -

        benchmark_weights

    ).sum()

)

active_weight = (

    np.abs(

        target["Target_Weight"]

        -

        benchmark_weights

    ).sum()

)

conviction_score = (

    active_share

    *

    information_ratio

)

print(
    "\n📈 ACTIVE SHARE ANALYTICS"
)

print(
    "Active Share:",
    round(
        active_share * 100,
        2
    ),
    "%"
)

print(
    "Active Weight:",
    round(
        active_weight * 100,
        2
    ),
    "%"
)

print(
    "Conviction Score:",
    round(
        conviction_score,
        2
    )
)

# =====================================
# STEP 13 - FACTOR EXPOSURE ANALYTICS
# =====================================

print("\n📊 FACTOR EXPOSURES")

factor_summary = pd.DataFrame({

    "Factor": [

        "Signal",

        "Momentum",

        "Quality",

        "Value",

        "Growth",

        "Low Vol"

    ],

    "Exposure": [

        (

            target["Signal_Factor"]

            *

            target["Target_Weight"]

        ).sum(),

        (

            target["Momentum_Factor"]

            *

            target["Target_Weight"]

        ).sum(),

        (

            target["Quality_Factor"]

            *

            target["Target_Weight"]

        ).sum(),

        (

            target["Value_Factor"]

            *

            target["Target_Weight"]

        ).sum(),

        (

            target["Growth_Factor"]

            *

            target["Target_Weight"]

        ).sum(),

        (

            (

                1

                -

                target["Volatility_252D"]

            )

            *

            target["Target_Weight"]

        ).sum()

    ]

})

print(
    factor_summary
)

# =====================================
# STEP 21 - FACTOR HEALTH CHECK
# =====================================

print(
    "\n🩺 FACTOR HEALTH CHECK"
)

factor_cols = [

    "Signal_Factor",

    "Momentum_Factor",

    "Quality_Factor",

    "Value_Factor",

    "Growth_Factor"

]

factor_health = []

for factor in factor_cols:

    factor_health.append({

        "Factor": factor,

        "Coverage_%": round(

            target[factor]

            .notna()

            .mean()

            * 100,

            2

        ),

        "Unique_Values": (

            target[factor]

            .nunique()

        ),

        "Std_Dev": round(

            target[factor]

            .std(),

            4

        )

    })

factor_health = pd.DataFrame(
    factor_health
)

print(
    factor_health
)

# =====================================
# STEP 18 - FACTOR RISK ATTRIBUTION
# =====================================

print(
    "\n🛡 FACTOR RISK ATTRIBUTION"
)

factor_risk = pd.DataFrame({

    "Factor": [

        "Signal",

        "Momentum",

        "Quality",

        "Value",

        "Growth",

        "Low Vol"

    ],

    "Exposure": [

        (

            target["Signal_Factor"]

            *

            target["Target_Weight"]

        ).sum(),

        (

            target["Momentum_Factor"]

            *

            target["Target_Weight"]

        ).sum(),

        (

            target["Quality_Factor"]

            *

            target["Target_Weight"]

        ).sum(),

        (

            target["Value_Factor"]

            *

            target["Target_Weight"]

        ).sum(),

        (

            target["Growth_Factor"]

            *

            target["Target_Weight"]

        ).sum(),

        (

            (

                1

                -

                target["Volatility_252D"]

            )

            *

            target["Target_Weight"]

        ).sum()

    ]

})

total_exposure = factor_risk["Exposure"].sum()

if total_exposure > 0:

    factor_risk["Risk_Contribution"] = (

        factor_risk["Exposure"]

        /

        total_exposure

    )

else:

    factor_risk["Risk_Contribution"] = 0

print(
    factor_risk
)

# =====================================
# STEP 14 - SECTOR ALPHA ATTRIBUTION
# =====================================

print(
    "\n🏛 SECTOR ALPHA ATTRIBUTION"
)

sector_alpha = (

    target

    .groupby(
        "Sector"
    )

    .apply(

        lambda x:

        (

            x["Composite_Alpha"]

            *

            x["Target_Weight"]

        ).sum()

    )

    .sort_values(
        ascending=False
    )

)

print(

    sector_alpha
    .head(10)

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

    actual = target_sector.get(
        worst_sector,
        0
    )

    scale = (
        benchmark + MAX_SECTOR_DRIFT
    ) / actual

    target.loc[
        target["Sector"] == worst_sector,
        "Target_Weight"
    ] *= scale

    target = normalize_weights(target)

# Reapply final stock cap

target = enforce_position_caps(
    target,
    MAX_POSITION_WEIGHT
)

target = normalize_weights(target)

# =========================================================
# DIVERSIFICATION REPAIR
# =========================================================

if (
    effective_holdings < MIN_EFFECTIVE_HOLDINGS
    and hhi > 0.04
):

    print("\n🔧 Repairing Diversification...")

    #target["Target_Weight"] = np.minimum(
        #target["Target_Weight"],
        #0.05
    #)

    target = normalize_weights(target)

    hhi = calculate_hhi(
        target["Target_Weight"]
    )

    effective_holdings = (
        calculate_effective_holdings(
            target["Target_Weight"]
        )
    )

    if (
        effective_holdings >= MIN_EFFECTIVE_HOLDINGS
        and hhi <= MAX_HHI
    ):
        governance_status = "PASS"

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

current_max_risk = (
    target["Risk_Contribution_Pct"]
    .max()
)

if current_max_risk > MAX_POSITION_RISK:
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


if len(target) < TARGET_HOLDINGS:

    print(
        f"WARNING: Holdings below target ({len(target)})"
    )

print(
    "\nFINAL MAX WEIGHT:",
    round(
        target["Target_Weight"].max(),
        4
    )
)

# =====================================
# FINAL HOLDINGS REPAIR
# =====================================

if len(target) < TARGET_HOLDINGS:

    missing = TARGET_HOLDINGS - len(target)

    print(
        f"Final Repair: Adding {missing} holdings..."
    )

    repair_candidates = (

        signals[
            ~signals["Symbol"].isin(
                target["Symbol"]
            )
        ]

        .sort_values(
            "Signal_Score",
            ascending=False
        )

        .head(missing)

        .copy()

    )

    repair_candidates["Target_Weight"] = 0.0025

    for col in target.columns:

        if col not in repair_candidates.columns:
            repair_candidates[col] = np.nan

    repair_candidates = repair_candidates[
        target.columns
    ]

    target = pd.concat(
        [target, repair_candidates],
        ignore_index=True
    )

    target["Target_Weight"] = (
        target["Target_Weight"]
        /
        target["Target_Weight"].sum()
    )

    print(
        "Final Holdings:",
        len(target)
    )

print(
    "\nFINAL HOLDING COUNT:",
    len(target)
)


for _ in range(5):

    target["Target_Weight"] = np.maximum(

        target["Target_Weight"],

        MIN_POSITION_WEIGHT

    )

    target["Target_Weight"] = (

        target["Target_Weight"]

        /

        target["Target_Weight"].sum()

    )

print(
    "Minimum Weight:",
    target["Target_Weight"].min()
)

print(

    target[
        target["Target_Weight"] <= (MIN_POSITION_WEIGHT- 1e-8)
    ][
        [
            "Symbol",
            "Target_Weight"
        ]
    ]

)

target = target[
    target["Target_Weight"] > 0
].copy()

target = normalize_weights(target)


print(
    "ZERO WEIGHT STOCKS:",
    (
        np.isclose(
            target["Target_Weight"],
            0,
            atol=1e-10
        )
    ).sum()
)

diagnostics = pd.DataFrame({

    "Metric":[

        "Portfolio_Beta",
        "Portfolio_Volatility",
        "Expected_Return",
        "Information_Ratio",
        "Turnover",
        "HHI",
        "Effective_Holdings",
        "Active_Share"

    ],

    "Value":[

        portfolio_beta,
        portfolio_volatility,
        expected_return,
        information_ratio,
        portfolio_turnover,
        hhi,
        effective_holdings,
        active_share

    ]

})

diagnostics.to_csv(

    OUTPUT_DIR
    / "portfolio_diagnostics.csv",

    index=False

)

# =====================================
# FINAL SECTOR CAP PASS
# =====================================

for _ in range(10):

    sector_weights = (
        target.groupby("Sector")
        ["Target_Weight"]
        .sum()
    )

    max_sector = sector_weights.max()

    if max_sector <= MAX_SECTOR_WEIGHT + 1e-6:
        break

    violating = sector_weights[
        sector_weights > MAX_SECTOR_WEIGHT
    ]

    for sector, weight in violating.items():

        scale = MAX_SECTOR_WEIGHT / weight

        target.loc[
            target["Sector"] == sector,
            "Target_Weight"
        ] *= scale

    target["Target_Weight"] /= (
        target["Target_Weight"].sum()
    )

target = enforce_position_caps(
    target,
    MAX_POSITION_WEIGHT
)

print("\nFINAL ASSERT CHECK")

print(
    "Weight Sum:",
    target["Target_Weight"].sum()
)

print(
    "Max Position:",
    target["Target_Weight"].max()
)

print(
    "Max Sector:",
    target.groupby("Sector")
    ["Target_Weight"]
    .sum()
    .max()
)

print(
    "Holding Count:",
    len(target)
)

print("\nSECTOR BREAKDOWN")

print(
    target.groupby("Sector")
    ["Target_Weight"]
    .sum()
    .sort_values(ascending=False)
)
print("\nASSERT DEBUG")

print(
    "Sector Max:",
    target.groupby("Sector")
    ["Target_Weight"]
    .sum()
    .max()
)

print(
    "Sector Limit:",
    MAX_SECTOR_WEIGHT
)

print(
    "Weight Sum:",
    target["Target_Weight"].sum()
)

print(
    "Max Position:",
    target["Target_Weight"].max()
)

print(
    "Position Limit:",
    MAX_POSITION_WEIGHT
)

print(
    "Holdings:",
    len(target)
)

print(
    "Target Holdings:",
    TARGET_HOLDINGS
)

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
    f"Portfolio Beta      : {portfolio_beta:.4f}"
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
    f"Active Share        : "
    f"{active_share:.2%}"
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