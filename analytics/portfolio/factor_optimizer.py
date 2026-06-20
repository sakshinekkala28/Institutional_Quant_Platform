from pathlib import Path
import pandas as pd
import numpy as np
import cvxpy as cp

# =====================================================
# CONFIG
# =====================================================

TARGET_HOLDINGS = 30

PRESELECT_UNIVERSE = 200

MAX_POSITION_WEIGHT = 0.05

MIN_POSITION_WEIGHT = 0.0025

MAX_SECTOR_WEIGHT = 0.25

MAX_TRACKING_ERROR = 0.10

RISK_AVERSION = 3.0

TURNOVER_PENALTY = 0.01

FACTOR_LIMIT = 1.5

RISK_PREMIUM = 0.06
TAU = 0.80

# =====================================================
# PATHS
# =====================================================

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_RETURNS_FILE = (
    ROOT
    / "data"
    / "risk"
    / "factor_expected_returns.parquet"
)

RISK_MODEL_FILE = (
    ROOT
    / "data"
    / "risk"
    / "factor_risk_covariance.parquet"
)

FACTOR_MASTER_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_master.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "optimized_portfolio.parquet"
)

CURRENT_PORTFOLIO_FILE = (

    ROOT
    / "data"
    / "portfolio"
    / "current_portfolio.parquet"

)

# =====================================================
# LOAD DATA
# =====================================================

print("\nLoading Inputs...")

factor_exposures = pd.read_parquet(
    ROOT
    / "data"
    / "risk"
    / "factor_exposure_matrix.parquet"
)

expected_returns = pd.read_parquet(
    EXPECTED_RETURNS_FILE
)

factor_master = pd.read_csv(
    FACTOR_MASTER_FILE
)

risk_cov = pd.read_parquet(
    RISK_MODEL_FILE
)

try:

    current_portfolio = pd.read_parquet(
        CURRENT_PORTFOLIO_FILE
    )

except Exception:

    current_portfolio = pd.DataFrame(
        columns=[
            "Symbol",
            "Weight"
        ]
    )

# =====================================================
# PRE-SELECTION
# =====================================================

universe = (

    expected_returns

    .sort_values(
        "Expected_Return",
        ascending=False
    )

    .head(
        PRESELECT_UNIVERSE
    )

)

# =====================================================
# LIQUIDITY DATA
# =====================================================

adv_map = (
    factor_master[
        ["Symbol", "ADV_20D"]
    ]
)

universe = universe.merge(
    adv_map,
    on="Symbol",
    how="left"
)

MIN_ADV = 5_000_000

universe = universe[
    universe["ADV_20D"].fillna(0)
    >= MIN_ADV
]


symbols = universe["Symbol"].tolist()

current_weights = (

    current_portfolio

    .set_index("Symbol")

    .reindex(symbols)

    ["Weight"]

    .fillna(0)

    .values

)

# =====================================================
# ALIGN DATA
# =====================================================

mu = (

    universe

    ["Expected_Return"]

    .values
)

Sigma = (

    risk_cov

    .loc[
        symbols,
        symbols
    ]

    .values
)

print(
    "\nCovariance Diagnostics"
)

print(
    "Average Variance:",
    np.mean(np.diag(Sigma))
)

print(
    "Average Daily Vol:",
    np.mean(np.sqrt(np.diag(Sigma)))
)

market_caps = (
    factor_master
    .set_index("Symbol")
    .reindex(symbols)
    ["Market_Cap"]
    .fillna(0)
)

market_weights = (

    market_caps

    /

    market_caps.sum()

).values


pi = (

    RISK_PREMIUM

    *

    Sigma

    @

    market_weights

)

alpha_z = (
    universe["Expected_Return_Z"]
    .fillna(0)
)

alpha_views = (
    alpha_z.values * 0.03
)

alpha_confidence = (
    alpha_z.abs()
    /
    alpha_z.abs().max()
)

alpha_views = (
    alpha_views
    * alpha_confidence.values
)

bl_mu = (
    (1 - TAU) * pi
    +
    TAU * alpha_views
)

mu = bl_mu


benchmark = (
    market_caps
    /
    market_caps.sum()
).values

sector_map = (

    factor_master

    [["Symbol", "Sector"]]

)

# =====================================================
# SECTOR DATA
# =====================================================

sector_map = (
    factor_master[
        ["Symbol", "Sector"]
    ]
)

universe = universe.merge(
    sector_map,
    on="Symbol",
    how="left"
)

factor_cols = [

    "Momentum",
    "Quality",
    "Value",
    "Growth",
    "Size",
    "Liquidity",
    "LowVol"

]

universe = universe.merge(

    factor_exposures[
        ["Symbol"] + factor_cols
    ],

    on="Symbol",

    how="left"

)

# =====================================================
# OPTIMIZATION VARIABLES
# =====================================================

n = len(universe)

w = cp.Variable(n)

# =====================================================
# OBJECTIVE
# =====================================================

expected_return_term = (

    mu
    @
    w

)

risk_term = cp.quad_form(
    w,
    Sigma
)

concentration_penalty = cp.sum_squares(w)

turnover_term = cp.norm1(

    w

    -

    current_weights

)

transaction_cost = (

    1

    /

    np.sqrt(

        universe["ADV_20D"]

        .fillna(

            universe["ADV_20D"]

            .median()

        )

    )

)

tc_term = (

    transaction_cost.values

    @

    w

)

sector_penalty = 0

objective = cp.Maximize(

    expected_return_term

    -

    RISK_AVERSION * risk_term

    -

    TURNOVER_PENALTY * turnover_term

    -

    0.05 * tc_term

    -

    0.10 * concentration_penalty

)

tracking_error = cp.quad_form(

    w

    -

    benchmark,

    Sigma

)


# =====================================================
# CONSTRAINTS
# =====================================================

constraints = [

    cp.sum(w) == 1,

    w >= 0,

    w <= MAX_POSITION_WEIGHT

]

constraints.append(

    cp.sum_squares(w)

    <=

    1 / 25

)

constraints.append(

    tracking_error

    <=

    MAX_TRACKING_ERROR ** 2

)


# =====================================================
# SECTOR CAPS
# =====================================================

for sector in universe["Sector"].dropna().unique():

    idx = np.where(
        universe["Sector"]
        == sector
    )[0]

    constraints.append(

        cp.sum(
            w[idx]
        )

        <=

        MAX_SECTOR_WEIGHT

    )


for factor in factor_cols:

    exposure_vector = (
        universe[factor]
        .fillna(0)
        .values
    )

    constraints.append(
        exposure_vector @ w <= FACTOR_LIMIT
    )

    constraints.append(
        exposure_vector @ w >= -FACTOR_LIMIT
    )

constraints.append(

    universe["Momentum"].fillna(0).values @ w

    <=

    0.80

)

constraints.append(

    universe["Growth"].fillna(0).values @ w

    <=

    0.80

)

# =====================================================
# SOLVE
# =====================================================

problem = cp.Problem(
    objective,
    constraints
)

problem.solve(

    solver=cp.CLARABEL,

    verbose=False

)

print(
    "\nSolver Status:",
    problem.status
)

print(
    "Objective Value:",
    problem.value
)

if problem.status != "optimal":

    raise RuntimeError(
        "Optimizer failed."
    )

# =====================================================
# RESULTS
# =====================================================

universe["Weight"] = np.maximum(
    w.value,
    0
)

# =====================================================
# FACTOR EXPOSURE ANALYSIS
# =====================================================

factor_cols = [

    "Momentum",
    "Quality",
    "Value",
    "Growth",
    "Size",
    "Liquidity",
    "LowVol"

]

factor_exposure_matrix = (

    factor_exposures

    .set_index("Symbol")

    .reindex(
        universe["Symbol"]
    )

    [factor_cols]

    .fillna(0)

)

portfolio_factor_exposure = pd.Series({

    factor:

    (

        universe["Weight"].values

        @

        factor_exposure_matrix[factor]
        .values

    )

    for factor in factor_cols

})

print(
    "\nPortfolio Factor Exposure"
)

print(
    portfolio_factor_exposure
    .sort_values(
        ascending=False
    )
)

print(
    "\nMax Absolute Factor Exposure:",
    round(
        portfolio_factor_exposure.abs().max(),
        4
    )
)

hhi = np.sum(
    universe["Weight"] ** 2
)

effective_holdings = (
    1 / hhi
)

print(
    "\nEffective Holdings:",
    round(
        effective_holdings,
        2
    )
)

portfolio = (

    universe

    .sort_values(
        "Weight",
        ascending=False
    )

)

portfolio = portfolio[
    portfolio["Weight"] >= MIN_POSITION_WEIGHT
]

portfolio = portfolio.head(
    TARGET_HOLDINGS
)

portfolio["Weight"] = (

    portfolio["Weight"]

    /

    portfolio["Weight"].sum()

)

# =====================================================
# ANALYTICS
# =====================================================

portfolio_return = (

    portfolio["Expected_Return"]

    *

    portfolio["Weight"]

).sum()

# =====================================================
# FULL PORTFOLIO VOLATILITY
# =====================================================

full_symbols = (
    universe["Symbol"]
    .tolist()
)

full_weights = (
    universe["Weight"]
    .values
)

full_cov = (

    risk_cov

    .loc[
        full_symbols,
        full_symbols
    ]

    .values
)

portfolio_volatility = np.sqrt(

    full_weights.T

    @

    full_cov

    @

    full_weights

)

annual_portfolio_volatility = portfolio_volatility

portfolio_vector = (
    universe["Weight"]
    .values
)

tracking_error_value = np.sqrt(

    (
        portfolio_vector
        -
        benchmark
    ).T

    @

    Sigma

    @

    (
        portfolio_vector
        -
        benchmark
    )

)

active_share = 0.5 * np.abs(
    portfolio_vector
    -
    benchmark
).sum()

print(
    "Active Share:",
    round(
        active_share * 100,
        2
    ),
    "%"
)

annual_alpha = (

    portfolio["Expected_Return"]

    *

    portfolio["Weight"]

).sum()

annual_te = tracking_error_value

information_ratio = (

    annual_alpha

    /

    max(
        annual_te,
        1e-6
    )

)

print(
    "Information Ratio:",
    round(
        information_ratio,
        2
    )
)

print(
    "\nTracking Error:",
    round(
        tracking_error_value * 100,
        2
    ),
    "%"
)


print(
    "\nPortfolio Return:",
    round(
        portfolio_return * 100,
        2
    ),
    "%"
)

print(
    "Portfolio Volatility:",
    round(
        annual_portfolio_volatility * 100,
        2
    ),
    "%"
)

print(
    "Holdings:",
    len(portfolio)
)
final_hhi = np.sum(
    portfolio["Weight"] ** 2
)

final_effective_holdings = (
    1 / final_hhi
)

print(
    "Final Effective Holdings:",
    round(
        final_effective_holdings,
        2
    )
)

factor_risk = (

    portfolio_factor_exposure.abs()

    /

    portfolio_factor_exposure.abs().sum()

)

print(
    "\nFactor Risk Attribution"
)

print(
    factor_risk
    .sort_values(
        ascending=False
    )
)

if round(effective_holdings, 1) < 25:

    print(
        "\nWARNING:"
        " Portfolio Concentrated"
    )

sector_weights = (
    portfolio
    .groupby("Sector")
    ["Weight"]
    .sum()
    .sort_values(
        ascending=False
    )
)

print("\nTop Holdings:")

print(

    portfolio[
        [
            "Symbol",
            "Weight",
            "Sector"
        ]
    ]

    .head(10)

)

approval_score = 100

if annual_te > 0.10:
    approval_score -= 20

if annual_portfolio_volatility > 0.50:
    approval_score -= 20

elif annual_portfolio_volatility > 0.35:
    approval_score -= 10

if portfolio_factor_exposure.max() > 0.75:
    approval_score -= 20

if active_share < 0.75:
    approval_score -= 20

if portfolio_factor_exposure.abs().max() > 1.0:
    approval_score -= 20

    print(
        "\nWARNING: Excessive Factor Concentration"
    )


status = (
    "APPROVED"
    if approval_score >= 80
    else "REVIEW"
)

print(
    "\nApproval Score:",
    approval_score
)

print(
    "Approval Status:",
    status
)

print("\n========================")
print("PORTFOLIO DASHBOARD")
print("========================")

print(
    f"Alpha Forecast      : {portfolio_return:.2%}"
)

print(
    f"Annual Tracking Error      : {annual_te:.2%}"
)

print(
    f"Portfolio Vol       : {annual_portfolio_volatility:.2%}"
)

print(
    f"Active Share        : {active_share:.2%}"
)

print(
    f"Effective Holdings  : {final_effective_holdings:.2f}"
)

print(
    f"Information Ratio   : {information_ratio:.2f}"
)

print(
    f"Approval Status     : {status}"
)

# =====================================================
# SAVE
# =====================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

portfolio.to_parquet(
    OUTPUT_FILE,
    index=False
)

print(
    "\nSaved:",
    OUTPUT_FILE
)