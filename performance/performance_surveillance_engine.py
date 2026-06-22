from __future__ import annotations

import logging

from core.settings import settings

from pathlib import Path

import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

ROOT_DIR = (

    Path(__file__)

    .resolve()

    .parents[1]

)

PERFORMANCE_DIR = (

    ROOT_DIR

    / "data"

    / "performance"

)

PERFORMANCE_SUMMARY_FILE = (

    PERFORMANCE_DIR

    / "performance_summary.csv"

)

RISK_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "risk_dashboard.csv"

)

REGIME_SCORECARD_FILE = (

    PERFORMANCE_DIR

    / "regime_scorecard.csv"

)

ROLLING_PERFORMANCE_FILE = (

    PERFORMANCE_DIR

    / "rolling_performance.csv"

)

PERFORMANCE_SURVEILLANCE_FILE = (

    PERFORMANCE_DIR

    / "performance_surveillance.csv"

)

PERFORMANCE_ALERTS_FILE = (

    PERFORMANCE_DIR

    / "performance_alerts.csv"

)

RISK_BREACHES_FILE = (

    PERFORMANCE_DIR

    / "risk_breaches.csv"

)

REGIME_ALERTS_FILE = (

    PERFORMANCE_DIR

    / "regime_alerts.csv"

)

ROLLING_ALERTS_FILE = (

    PERFORMANCE_DIR

    / "rolling_alerts.csv"

)

SURVEILLANCE_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "surveillance_dashboard.csv"

)


# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(

    level=logging.INFO,

    format=(

        "%(asctime)s | "

        "%(levelname)s | "

        "%(message)s"

    )

)

logger = logging.getLogger(
    __name__
)

# ==========================================================
# PERFORMANCE REPOSITORY
# ==========================================================

class PerformanceRepository:

    @staticmethod
    def load_summary() -> pd.DataFrame:

        logger.info(

            "Loading Performance Summary"

        )

        if not PERFORMANCE_SUMMARY_FILE.exists():

            raise FileNotFoundError(

                PERFORMANCE_SUMMARY_FILE

            )

        return pd.read_csv(

            PERFORMANCE_SUMMARY_FILE

        )

    @staticmethod
    def load_risk_dashboard() -> pd.DataFrame:

        logger.info(

            "Loading Risk Dashboard"

        )

        if not RISK_DASHBOARD_FILE.exists():

            raise FileNotFoundError(

                RISK_DASHBOARD_FILE

            )
        
        return pd.read_csv(

            RISK_DASHBOARD_FILE

        )

    @staticmethod
    def load_regime_scorecard() -> pd.DataFrame:

        logger.info(

            "Loading Regime Scorecard"

        )

        if not REGIME_SCORECARD_FILE.exists():

            raise FileNotFoundError(

                REGIME_SCORECARD_FILE

            )
        
        return pd.read_csv(

            REGIME_SCORECARD_FILE

        )

    @staticmethod
    def load_rolling_performance() -> pd.DataFrame:

        logger.info(

            "Loading Rolling Performance"

        )

        if not ROLLING_PERFORMANCE_FILE.exists():

            raise FileNotFoundError(

                ROLLING_PERFORMANCE_FILE

            )
        
        return pd.read_csv(

            ROLLING_PERFORMANCE_FILE

        )
    
# ==========================================================
# DATA VALIDATOR
# ==========================================================

class SurveillanceValidator:

    @staticmethod
    def validate_summary(

        summary: pd.DataFrame

    ):

        if summary.empty:

            raise ValueError(

                "Performance Summary Empty"

            )

    @staticmethod
    def validate_rolling(

        rolling_df: pd.DataFrame

    ):

        if rolling_df.empty:

            raise ValueError(

                "Rolling Performance Empty"

            )

        required = [

            "Rolling_Sharpe",

            "Rolling_Information_Ratio",

            "Rolling_Alpha",

            "Rolling_Max_Drawdown",

            "Rolling_Risk_Grade",

            "Rolling_Performance_Score"

        ]

        missing = [

            col

            for col in required

            if col not in rolling_df.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Columns: {missing}"

            )
    @staticmethod
    def validate_inputs(

        summary: pd.DataFrame,

        risk_dashboard: pd.DataFrame,

        regime_scorecard: pd.DataFrame,

        rolling_df: pd.DataFrame

    ):

        SurveillanceValidator.validate_summary(

            summary

        )

        SurveillanceValidator.validate_rolling(

            rolling_df

        )

        if risk_dashboard.empty:

            raise ValueError(

                "Risk Dashboard Empty"

            )

        if regime_scorecard.empty:

            raise ValueError(

                "Regime Scorecard Empty"

            )

        logger.info(

            "Surveillance Validation Passed"

        )

# ==========================================================
# ALERT FACTORY
# ==========================================================

class AlertFactory:

    @staticmethod
    def create(

        category: str,

        severity: str,

        metric: str,

        value,

        threshold,

        message: str

    ) -> dict:

        return {

            "Category":
                category,

            "Severity":
                severity,

            "Metric":
                metric,

            "Value":
                value,

            "Threshold":
                threshold,

            "Message":
                message

        }

# ==========================================================
# PERFORMANCE ALERT ENGINE
# ==========================================================

class PerformanceAlertEngine:

    @staticmethod
    def build(

        summary: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Performance Alerts"

        )

        alerts = []

        metrics = (

            summary

            .iloc[0]

        )

        if (

            metrics[
                "Sharpe_Ratio"
            ]

            <

            settings
            .surveillance
            .MIN_SHARPE

        ):

            alerts.append(

                AlertFactory.create(

                    category="Performance",

                    severity="WARNING",

                    metric="Sharpe_Ratio",

                    value=metrics[
                        "Sharpe_Ratio"
                    ],

                    threshold=

                        settings
                        .surveillance
                        .MIN_SHARPE,

                    message=(

                        "Sharpe Ratio "

                        "below threshold"

                    )

                )

            )

        if (

            metrics[
                "Information_Ratio"
            ]

            <

            settings
            .surveillance
            .MIN_INFORMATION_RATIO

        ):

            alerts.append(

                AlertFactory.create(

                    category="Performance",

                    severity="WARNING",

                    metric="Information_Ratio",

                    value=metrics[
                        "Information_Ratio"
                    ],

                    threshold=

                        settings
                        .surveillance
                        .MIN_INFORMATION_RATIO,

                    message=(

                        "Information Ratio "

                        "below threshold"

                    )

                )

            )

        if (

            metrics[
                "Alpha"
            ]

            <

            settings
            .surveillance
            .MIN_ALPHA

        ):

            alerts.append(

                AlertFactory.create(

                    category="Performance",

                    severity="CRITICAL",

                    metric="Alpha",

                    value=metrics[
                        "Alpha"
                    ],

                    threshold=

                        settings
                        .surveillance
                        .MIN_ALPHA,

                    message=(

                        "Negative Alpha "

                        "detected"

                    )

                )

            )

        if (

            metrics[
                "Hit_Ratio"
            ]

            <

            settings
            .surveillance
            .MIN_HIT_RATIO

        ):

            alerts.append(

                AlertFactory.create(

                    category="Performance",

                    severity="WARNING",

                    metric="Hit_Ratio",

                    value=metrics[
                        "Hit_Ratio"
                    ],

                    threshold=

                        settings
                        .surveillance
                        .MIN_HIT_RATIO,

                    message=(

                        "Hit Ratio "

                        "below threshold"

                    )

                )

            )

        return pd.DataFrame(

            alerts

        )

# ==========================================================
# RISK BREACH ENGINE
# ==========================================================

class RiskBreachEngine:

    @staticmethod
    def build(

        summary: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Risk Breaches"

        )

        breaches = []

        metrics = (

            summary

            .iloc[0]

        )

        if (

            metrics[
                "Historical_VaR_95"
            ]

            >

            settings
            .surveillance
            .MAX_VAR95

        ):

            breaches.append(

                AlertFactory.create(

                    category="Risk",

                    severity="CRITICAL",

                    metric="Historical_VaR_95",

                    value=metrics[
                        "Historical_VaR_95"
                    ],

                    threshold=

                        settings
                        .surveillance
                        .MAX_VAR95,

                    message=(

                        "VaR limit "

                        "breached"

                    )

                )

            )

        if (

            metrics[
                "Historical_CVaR_95"
            ]

            >

            settings
            .surveillance
            .MAX_CVAR95

        ):

            breaches.append(

                AlertFactory.create(

                    category="Risk",

                    severity="CRITICAL",

                    metric="Historical_CVaR_95",

                    value=metrics[
                        "Historical_CVaR_95"
                    ],

                    threshold=

                        settings
                        .surveillance
                        .MAX_CVAR95,

                    message=(

                        "CVaR limit "

                        "breached"

                    )

                )

            )

        drawdown = abs(

            metrics[
                "Max_Drawdown"
            ]

        )

        if (

            drawdown

            >

            settings
            .surveillance
            .CRITICAL_DRAWDOWN

        ):

            severity = "CRITICAL"

            threshold = (

                settings
                .surveillance
                .CRITICAL_DRAWDOWN

            )

        elif (

            drawdown

            >

            settings
            .surveillance
            .WARNING_DRAWDOWN

        ):

            severity = "WARNING"

            threshold = (

                settings
                .surveillance
                .WARNING_DRAWDOWN

            )

        else:

            severity = None

        if severity:

            breaches.append(

                AlertFactory.create(

                    category="Risk",

                    severity=severity,

                    metric="Max_Drawdown",

                    value=metrics[
                        "Max_Drawdown"
                    ],

                    threshold=threshold,

                    message=(

                        "Drawdown threshold "

                        "breached"

                    )

                )

            )

        if (

            metrics[
                "Tracking_Error"
            ]

            >

            settings
            .surveillance
            .MAX_TRACKING_ERROR

        ):

            breaches.append(

                AlertFactory.create(

                    category="Risk",

                    severity="WARNING",

                    metric="Tracking_Error",

                    value=metrics[
                        "Tracking_Error"
                    ],

                    threshold=

                        settings
                        .surveillance
                        .MAX_TRACKING_ERROR,

                    message=(

                        "Tracking Error "

                        "above threshold"

                    )

                )

            )

        return pd.DataFrame(

            breaches

        )
    
# ==========================================================
# ROLLING SURVEILLANCE ENGINE
# ==========================================================

class RollingSurveillanceEngine:

    @staticmethod
    def build(

        rolling_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Rolling Surveillance"

        )

        alerts = []

        latest = (

            rolling_df

            .sort_values(

                "Date"

            )

            .iloc[-1]

        )

        if (

            latest[
                "Rolling_Sharpe"
            ]

            <

            settings
            .surveillance
            .MIN_SHARPE

        ):

            alerts.append(

                AlertFactory.create(

                    category="Rolling",

                    severity="WARNING",

                    metric="Rolling_Sharpe",

                    value=latest[
                        "Rolling_Sharpe"
                    ],

                    threshold=

                        settings
                        .surveillance
                        .MIN_SHARPE,

                    message=(

                        "Rolling Sharpe "

                        "below threshold"

                    )

                )

            )

        if (

            latest[
                "Rolling_Information_Ratio"
            ]

            <

            settings
            .surveillance
            .MIN_INFORMATION_RATIO

        ):

            alerts.append(

                AlertFactory.create(

                    category="Rolling",

                    severity="WARNING",

                    metric="Rolling_Information_Ratio",

                    value=latest[
                        "Rolling_Information_Ratio"
                    ],

                    threshold=

                        settings
                        .surveillance
                        .MIN_INFORMATION_RATIO,

                    message=(

                        "Rolling Information Ratio "

                        "below threshold"

                    )

                )

            )

        if (

            latest[
                "Rolling_Alpha"
            ]

            <

            settings
            .surveillance
            .MIN_ALPHA

        ):

            alerts.append(

                AlertFactory.create(

                    category="Rolling",

                    severity="CRITICAL",

                    metric="Rolling_Alpha",

                    value=latest[
                        "Rolling_Alpha"
                    ],

                    threshold=

                        settings
                        .surveillance
                        .MIN_ALPHA,

                    message=(

                        "Rolling Alpha "

                        "negative"

                    )

                )

            )

        rolling_drawdown = abs(

            latest[
                "Rolling_Max_Drawdown"
            ]

        )

        if (

            rolling_drawdown

            >

            settings
            .surveillance
            .CRITICAL_DRAWDOWN

        ):

            severity = "CRITICAL"

            threshold = (

                settings
                .surveillance
                .CRITICAL_DRAWDOWN

            )

        elif (

            rolling_drawdown

            >

            settings
            .surveillance
            .WARNING_DRAWDOWN

        ):

            severity = "WARNING"

            threshold = (

                settings
                .surveillance
                .WARNING_DRAWDOWN

            )

        else:

            severity = None

        if severity:

            alerts.append(

                AlertFactory.create(

                    category="Rolling",

                    severity=severity,

                    metric="Rolling_Max_Drawdown",

                    value=latest[
                        "Rolling_Max_Drawdown"
                    ],

                    threshold=threshold,

                    message=(

                        "Rolling Drawdown "

                        "breached"

                    )

                )

            )

        if (

            latest[
                "Rolling_Performance_Score"
            ]

            <

            settings
            .surveillance
            .MIN_ROLLING_SCORE

        ):

            alerts.append(

                AlertFactory.create(

                    category="Rolling",

                    severity="WARNING",

                    metric="Rolling_Performance_Score",

                    value=latest[
                        "Rolling_Performance_Score"
                    ],

                    threshold=

                        settings
                        .surveillance
                        .MIN_ROLLING_SCORE,

                    message=(

                        "Rolling Performance Score "

                        "below threshold"

                    )

                )

            )

        if (

            str(

                latest[
                    "Rolling_Risk_Grade"
                ]

            ).upper()

            ==

            "HIGH"

        ):

            alerts.append(

                AlertFactory.create(

                    category="Rolling",

                    severity="CRITICAL",

                    metric="Rolling_Risk_Grade",

                    value=latest[
                        "Rolling_Risk_Grade"
                    ],

                    threshold="MODERATE",

                    message=(

                        "High Risk Grade "

                        "detected"

                    )

                )

            )

        return pd.DataFrame(

            alerts

        )
    
# ==========================================================
# REGIME ALERT ENGINE
# ==========================================================

class RegimeAlertEngine:

    @staticmethod
    def build(

        regime_scorecard: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Regime Alerts"

        )

        alerts = []

        for _, row in (

            regime_scorecard

            .iterrows()

        ):

            if (

                row[
                    "Regime_Score"
                ]

                <

                settings
                .surveillance
                .MIN_REGIME_SCORE

            ):

                alerts.append(

                    AlertFactory.create(

                        category="Regime",

                        severity="WARNING",

                        metric=row[
                            "Regime"
                        ],

                        value=row[
                            "Regime_Score"
                        ],

                        threshold=

                            settings
                            .surveillance
                            .MIN_REGIME_SCORE,

                        message=(

                            f"{row['Regime']} "

                            "Regime Score "

                            "below threshold"

                        )

                    )

                )

            if (

                row[
                    "Sharpe"
                ]

                < 0

            ):

                alerts.append(

                    AlertFactory.create(

                        category="Regime",

                        severity="CRITICAL",

                        metric=(

                            f"{row['Regime']}_Sharpe"

                        ),

                        value=row[
                            "Sharpe"
                        ],

                        threshold=0,

                        message=(

                            f"{row['Regime']} "

                            "Regime Sharpe "

                            "negative"

                        )

                    )

                )

            if (

                row[
                    "Alpha"
                ]

                < 0

            ):

                alerts.append(

                    AlertFactory.create(

                        category="Regime",

                        severity="CRITICAL",

                        metric=(

                            f"{row['Regime']}_Alpha"

                        ),

                        value=row[
                            "Alpha"
                        ],

                        threshold=0,

                        message=(

                            f"{row['Regime']} "

                            "Regime Alpha "

                            "negative"

                        )

                    )

                )

        return pd.DataFrame(

            alerts

        )
    
# ==========================================================
# SURVEILLANCE DASHBOARD ENGINE
# ==========================================================

class SurveillanceDashboardEngine:

    @staticmethod
    def build(

        performance_alerts: pd.DataFrame,

        risk_breaches: pd.DataFrame,

        rolling_alerts: pd.DataFrame,

        regime_alerts: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Surveillance Dashboard"

        )

        total_alerts = (

            len(performance_alerts)

            +

            len(risk_breaches)

            +

            len(rolling_alerts)

            +

            len(regime_alerts)

        )

        critical_alerts = (

            sum(

                len(

                    df.loc[

                        df[
                            "Severity"
                        ]

                        ==

                        "CRITICAL"

                    ]

                )

                for df in [

                    performance_alerts,

                    risk_breaches,

                    rolling_alerts,

                    regime_alerts

                ]

                if not df.empty

            )

        )

        warning_alerts = (

            sum(

                len(

                    df.loc[

                        df[
                            "Severity"
                        ]

                        ==

                        "WARNING"

                    ]

                )

                for df in [

                    performance_alerts,

                    risk_breaches,

                    rolling_alerts,

                    regime_alerts

                ]

                if not df.empty

            )

        )

        health = (

            "HEALTHY"

            if critical_alerts == 0

            else

            "ACTION_REQUIRED"

        )

        return pd.DataFrame(

            [

                {

                    "Metric":
                        "Total_Alerts",

                    "Value":
                        total_alerts

                },

                {

                    "Metric":
                        "Critical_Alerts",

                    "Value":
                        critical_alerts

                },

                {

                    "Metric":
                        "Warning_Alerts",

                    "Value":
                        warning_alerts

                },

                {

                    "Metric":
                        "Surveillance_Health",

                    "Value":
                        health

                }

            ]

        )
    
# ==========================================================
# EXPORT ENGINE
# ==========================================================

class ExportEngine:

    @staticmethod
    def save(

        performance_alerts: pd.DataFrame,

        risk_breaches: pd.DataFrame,

        rolling_alerts: pd.DataFrame,

        regime_alerts: pd.DataFrame,

        surveillance_dashboard: pd.DataFrame

    ):

        logger.info(

            "Exporting Surveillance Reports"

        )

        all_alerts = pd.concat(

            [

                performance_alerts,

                risk_breaches,

                rolling_alerts,

                regime_alerts

            ],

            ignore_index=True

        )

        all_alerts.to_csv(

            PERFORMANCE_SURVEILLANCE_FILE,

            index=False

        )

        for df, path in [

            (

                performance_alerts,

                PERFORMANCE_ALERTS_FILE

            ),

            (

                risk_breaches,

                RISK_BREACHES_FILE

            ),

            (

                regime_alerts,

                REGIME_ALERTS_FILE

            ),

            (

                rolling_alerts,

                ROLLING_ALERTS_FILE

            )

        ]:

            if df.empty:

                pd.DataFrame(

                    columns=[

                        "Category",

                        "Severity",

                        "Metric",

                        "Value",

                        "Threshold",

                        "Message"

                    ]

                ).to_csv(

                    path,

                    index=False

                )

            else:

                df.to_csv(

                    path,

                    index=False

                )

        surveillance_dashboard.to_csv(

            SURVEILLANCE_DASHBOARD_FILE,

            index=False

        )

        logger.info(

            "Surveillance Reports Exported"

        )

# ==========================================================
# PERFORMANCE SURVEILLANCE ENGINE
# ==========================================================

class PerformanceSurveillanceEngine:

    def run(

        self

    ):

        logger.info(

            "Starting Performance Surveillance"

        )

        summary = (

            PerformanceRepository

            .load_summary()

        )

        risk_dashboard = (

            PerformanceRepository

            .load_risk_dashboard()

        )

        regime_scorecard = (

            PerformanceRepository

            .load_regime_scorecard()

        )

        rolling_df = (

            PerformanceRepository

            .load_rolling_performance()

        )

        SurveillanceValidator.validate_inputs(

            summary,

            risk_dashboard,

            regime_scorecard,

            rolling_df

        )

        performance_alerts = (

            PerformanceAlertEngine

            .build(

                summary

            )

        )

        risk_breaches = (

            RiskBreachEngine

            .build(

                summary

            )

        )

        rolling_alerts = (

            RollingSurveillanceEngine

            .build(

                rolling_df

            )

        )

        regime_alerts = (

            RegimeAlertEngine

            .build(

                regime_scorecard

            )

        )

        surveillance_dashboard = (

            SurveillanceDashboardEngine

            .build(

                performance_alerts,

                risk_breaches,

                rolling_alerts,

                regime_alerts

            )

        )

        ExportEngine.save(

            performance_alerts,

            risk_breaches,

            rolling_alerts,

            regime_alerts,

            surveillance_dashboard

        )

        logger.info(

            "Performance Surveillance Complete"

        )

        return {

            "performance_alerts":

                len(

                    performance_alerts

                ),

            "risk_breaches":

                len(

                    risk_breaches

                ),

            "rolling_alerts":

                len(

                    rolling_alerts

                ),

            "regime_alerts":

                len(

                    regime_alerts

                )

        }

# ==========================================================
# RUNNER
# ==========================================================

def run_example():

    results = (

        PerformanceSurveillanceEngine()

        .run()

    )

    print()

    print(

        "=" * 80

    )

    print(

        "INSTITUTIONAL PERFORMANCE SURVEILLANCE"

    )

    print(

        "=" * 80

    )

    for key, value in (

        results.items()

    ):

        print(

            f"{key}: {value:,}"

        )

    print(

        "=" * 80

    )


if __name__ == "__main__":

    run_example()