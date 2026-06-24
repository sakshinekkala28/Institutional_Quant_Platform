from __future__ import annotations

import logging

from pathlib import Path

import pandas as pd

from core.settings import settings

from monitoring.alert_history_engine import (

    AlertHistoryEngine

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
# PATHS
# ==========================================================

ROOT_DIR = (

    settings
    .environment
    .ROOT_DIR

)

PERFORMANCE_DIR = (

    ROOT_DIR

    / "data"

    / "performance"

)

MONITORING_DIR = (

    ROOT_DIR

    / "data"

    / "monitoring"

)

STRESS_DASHBOARD_FILE = (

    MONITORING_DIR

    / "stress_dashboard.csv"

)

MONITORING_DIR.mkdir(

    parents=True,

    exist_ok=True

)

FORECAST_FILE = (

    PERFORMANCE_DIR

    / "performance_forecast.csv"

)

COMMITTEE_FILE = (

    PERFORMANCE_DIR

    / "investment_committee_pack.csv"

)

STRESS_FILE = (

    PERFORMANCE_DIR

    / "stress_test_results.csv"

)

SURVEILLANCE_FILE = (

    PERFORMANCE_DIR

    / "surveillance_dashboard.csv"

)

MONITOR_STATUS_FILE = (

    MONITORING_DIR

    / "monitor_status.csv"

)

MONITOR_ALERTS_FILE = (

    MONITORING_DIR

    / "monitor_alerts.csv"

)

MONITOR_DASHBOARD_FILE = (

    MONITORING_DIR

    / "monitor_dashboard.csv"

)

# ==========================================================
# REPOSITORY
# ==========================================================

class MonitorRepository:

    @staticmethod
    def load_forecast():

        logger.info(

            "Loading Forecast"

        )

        return pd.read_csv(

            FORECAST_FILE

        )

    @staticmethod
    def load_committee():

        logger.info(

            "Loading Committee Pack"

        )

        return pd.read_csv(

            COMMITTEE_FILE

        )

    @staticmethod
    def load_stress():

        logger.info(

            "Loading Stress Results"

        )

        return pd.read_csv(

            STRESS_FILE

        )

    @staticmethod
    def load_surveillance():

        logger.info(

            "Loading Surveillance"

        )

        return pd.read_csv(

            SURVEILLANCE_FILE

        )
    
# ==========================================================
# VALIDATOR
# ==========================================================

class MonitorValidator:

    @staticmethod
    def validate(

        forecast,

        committee,

        stress,

        surveillance

    ):

        if forecast.empty:

            raise ValueError(

                "Forecast Empty"

            )

        if committee.empty:

            raise ValueError(

                "Committee Pack Empty"

            )

        if stress.empty:

            raise ValueError(

                "Stress Results Empty"

            )

        if surveillance.empty:

            raise ValueError(

                "Surveillance Empty"

            )

        logger.info(

            "Monitor Validation Passed"

        )

# ==========================================================
# ALERT MODEL
# ==========================================================

class AlertBuilder:

    @staticmethod
    def build(

        severity,

        category,

        message

    ):

        return {

            "Severity":

                severity,

            "Category":

                category,

            "Message":

                message

        }
    
# ==========================================================
# STATUS MODEL
# ==========================================================

class StatusBuilder:

    @staticmethod
    def build(

        category,

        status

    ):

        return {

            "Category":

                category,

            "Status":

                status

        }
    
# ==========================================================
# FORECAST MONITOR ENGINE
# ==========================================================

class ForecastMonitorEngine:

    @staticmethod
    def evaluate(

        forecast

    ):

        logger.info(

            "Evaluating Forecast Monitor"

        )

        alerts = []

        statuses = []

        row = (

            forecast

            .iloc[0]

        )

        confidence = (

            row[
                "Forecast_Confidence"
            ]

        )

        regime = (

            row[
                "Forecast_Regime"
            ]

        )

        recommendation = (

            row[
                "Forecast_Recommendation"
            ]

        )

        if confidence < 50:

            alerts.append(

                AlertBuilder.build(

                    "CRITICAL",

                    "FORECAST",

                    "Forecast Confidence below 50"

                )

            )

            status = "CRITICAL"

        elif confidence < 60:

            alerts.append(

                AlertBuilder.build(

                    "HIGH",

                    "FORECAST",

                    "Forecast Confidence below 60"

                )

            )

            status = "WARNING"

        elif confidence < 70:

            alerts.append(

                AlertBuilder.build(

                    "MEDIUM",

                    "FORECAST",

                    "Forecast Confidence below 70"

                )

            )

            status = "WATCH"

        else:

            status = "NORMAL"

        if regime == "BEAR":

            alerts.append(

                AlertBuilder.build(

                    "HIGH",

                    "FORECAST",

                    "Forecast Regime is BEAR"

                )

            )

        if recommendation == "UNDERWEIGHT":

            alerts.append(

                AlertBuilder.build(

                    "MEDIUM",

                    "FORECAST",

                    "Recommendation is UNDERWEIGHT"

                )

            )

        statuses.append(

            StatusBuilder.build(

                "Forecast",

                status

            )

        )

        return alerts, statuses

# ==========================================================
# COMMITTEE MONITOR ENGINE
# ==========================================================

class CommitteeMonitorEngine:

    @staticmethod
    def evaluate(

        committee

    ):

        logger.info(

            "Evaluating Committee Monitor"

        )

        alerts = []

        statuses = []

        metrics = {}

        for _, row in committee.iterrows():

            metrics[
                str(
                    row["Metric"]
                )
            ] = row["Value"]

        committee_score = float(

            metrics.get(

                "Committee_Score",

                0

            )

        )

        decision = str(

            metrics.get(

                "Decision",

                "APPROVE"

            )

        )

        committee_view = str(

            metrics.get(

                "Committee_View",

                ""

            )

        )

        if committee_score < 40:

            alerts.append(

                AlertBuilder.build(

                    "CRITICAL",

                    "COMMITTEE",

                    "Committee Score below 40"

                )

            )

            status = "CRITICAL"

        elif committee_score < 50:

            alerts.append(

                AlertBuilder.build(

                    "HIGH",

                    "COMMITTEE",

                    "Committee Score below 50"

                )

            )

            status = "WARNING"

        elif committee_score < 60:

            alerts.append(

                AlertBuilder.build(

                    "MEDIUM",

                    "COMMITTEE",

                    "Committee Score below 60"

                )

            )

            status = "WATCH"

        else:

            status = "NORMAL"

        if decision != "APPROVE":

            alerts.append(

                AlertBuilder.build(

                    "CRITICAL",

                    "COMMITTEE",

                    f"Decision = {decision}"

                )

            )

        if committee_view in [

            "SELL",

            "STRONG_SELL"

        ]:

            alerts.append(

                AlertBuilder.build(

                    "HIGH",

                    "COMMITTEE",

                    f"Committee View = {committee_view}"

                )

            )

        statuses.append(

            StatusBuilder.build(

                "Committee",

                status

            )

        )

        return alerts, statuses
    
# ==========================================================
# MONITOR AGGREGATOR
# ==========================================================

class MonitorAggregator:

    @staticmethod
    def combine(

        *results

    ):

        alerts = []

        statuses = []

        for result in results:

            alerts.extend(

                result[0]

            )

            statuses.extend(

                result[1]

            )

        return alerts, statuses


class StressAnalytics:

    @staticmethod
    def calculate(

        stress

    ):

        worst_score = (

            stress[
                "Stress_Score"
            ]

            .min()

        )

        rejected = len(

            stress[

                stress[
                    "Stress_Score"
                ]

                < 25

            ]

        )

        stress_average = (

            stress[
                "Stress_Score"
            ]

            .mean()

        )

        stress_severity_score = (

            100

            -

            stress_average

        )

        if stress_average >= 70:

            stress_view = "RESILIENT"

        elif stress_average >= 50:

            stress_view = "STABLE"

        elif stress_average >= 30:

            stress_view = "VULNERABLE"

        else:

            stress_view = "TAIL_RISK"

        return {

            "Worst_Stress_Score":

                worst_score,

            "Rejected_Scenarios":

                rejected,

            "Stress_Average":

                stress_average,

            "Stress_Severity_Score":
                    stress_severity_score,

            "Stress_View":

                stress_view

        }
    
# ==========================================================
# STRESS MONITOR ENGINE
# ==========================================================

class StressMonitorEngine:

    @staticmethod
    def evaluate(

        stress

    ):

        logger.info(

            "Evaluating Stress Monitor"

        )

        alerts = []

        statuses = []

        stress_metrics = (

            StressAnalytics

            .calculate(

                stress

            )

        )

        worst_score = (

            stress_metrics[

                "Worst_Stress_Score"

            ]

        )

        rejected = (

            stress_metrics[

                "Rejected_Scenarios"

            ]

        )

        stress_average = (

            stress_metrics[

                "Stress_Average"

            ]

        )

        stress_view = (

            stress_metrics[

                "Stress_View"

            ]

        )

        if worst_score < 10:

            alerts.append(

                AlertBuilder.build(

                    "CRITICAL",

                    "STRESS",

                    (

                        f"Worst Stress Score "

                        f"{worst_score:.2f}"

                    )

                )

            )

            status = "CRITICAL"

        elif worst_score < 25:

            alerts.append(

                AlertBuilder.build(

                    "HIGH",

                    "STRESS",

                    (

                        f"Worst Stress Score "

                        f"{worst_score:.2f}"

                    )

                )

            )

            status = "WARNING"

        elif worst_score < 40:

            alerts.append(

                AlertBuilder.build(

                    "MEDIUM",

                    "STRESS",

                    (

                        f"Worst Stress Score "

                        f"{worst_score:.2f}"

                    )

                )

            )

            status = "WATCH"

        else:

            status = "NORMAL"

        if rejected >= 3:

            alerts.append(

                AlertBuilder.build(

                    "HIGH",

                    "STRESS",

                    (

                        f"{rejected} Stress "

                        f"Scenarios Rejected"

                    )

                )

            )

        alerts.append(

            AlertBuilder.build(

                "INFO",

                "STRESS",

                f"Stress View: {stress_view}"

            )

        )

        statuses.append(

            StatusBuilder.build(

                "Stress",

                status

            )

        )

        return alerts, statuses


class StressDashboardBuilder:

    @staticmethod
    def build(

        stress

    ):

        stress_metrics = (

            StressAnalytics

            .calculate(

                stress

            )

        )

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Stress_View",

                    "Value":

                        stress_metrics[

                            "Stress_View"

                        ]

                },

                {

                    "Metric":

                        "Stress_Average",

                    "Value":

                        stress_metrics[

                            "Stress_Average"

                        ]

                },

                {

                    "Metric":

                        "Stress_Severity_Score",

                    "Value":

                        stress_metrics[

                            "Stress_Severity_Score"

                        ]                

                },
                
                {

                    "Metric":

                        "Worst_Stress_Score",

                    "Value":

                        stress_metrics[

                            "Worst_Stress_Score"

                        ]

                },

                {

                    "Metric":

                        "Rejected_Scenarios",

                    "Value":

                        stress_metrics[

                            "Rejected_Scenarios"

                        ]

                }

            ]

        )
    
# ==========================================================
# SURVEILLANCE MONITOR ENGINE
# ==========================================================

class SurveillanceMonitorEngine:

    @staticmethod
    def evaluate(

        surveillance

    ):

        logger.info(

            "Evaluating Surveillance Monitor"

        )

        alerts = []

        statuses = []

        metrics = {}

        for _, row in surveillance.iterrows():

            metrics[
                str(
                    row["Metric"]
                )
            ] = row["Value"]

        critical = int(

            metrics.get(

                "Critical_Alerts",

                0

            )

        )

        warning = int(

            metrics.get(

                "Warning_Alerts",

                0

            )

        )

        if critical > 0:

            alerts.append(

                AlertBuilder.build(

                    "CRITICAL",

                    "SURVEILLANCE",

                    (

                        f"{critical} "

                        f"Critical Alerts"

                    )

                )

            )

            status = "CRITICAL"

        elif warning >= 5:

            alerts.append(

                AlertBuilder.build(

                    "HIGH",

                    "SURVEILLANCE",

                    (

                        f"{warning} "

                        f"Warning Alerts"

                    )

                )

            )

            status = "WARNING"

        elif warning > 0:

            alerts.append(

                AlertBuilder.build(

                    "MEDIUM",

                    "SURVEILLANCE",

                    (

                        f"{warning} "

                        f"Warning Alerts"

                    )

                )

            )

            status = "WATCH"

        else:

            status = "NORMAL"

        statuses.append(

            StatusBuilder.build(

                "Surveillance",

                status

            )

        )

        return alerts, statuses
    
# ==========================================================
# ALERT SEVERITY ENGINE
# ==========================================================

class AlertSeverityEngine:

    @staticmethod
    def summarize(

        statuses

    ):

        score_map = {

            "NORMAL": 100,

            "WATCH": 70,

            "WARNING": 40,

            "CRITICAL": 10

        }

        scores = [

            score_map.get(

                item["Status"],

                0

            )

            for item in statuses

        ]

        overall_score = (

            sum(scores)

            / len(scores)

        )

        if overall_score >= 80:

            return "NORMAL"

        if overall_score >= 60:

            return "WATCH"

        if overall_score >= 40:

            return "WARNING"

        return "CRITICAL"
    
# ==========================================================
# MONITOR DASHBOARD BUILDER
# ==========================================================

class MonitorDashboardBuilder:

    @staticmethod
    def build(

        statuses,

        overall_severity

    ):

        dashboard = []

        for item in statuses:

            dashboard.append(

                {

                    "Category":

                        item["Category"],

                    "Status":

                        item["Status"]

                }

            )

        dashboard.append(

            {

                "Category":

                    "Overall",

                "Status":

                    overall_severity

            }

        )

        return pd.DataFrame(

            dashboard

        )

# ==========================================================
# LIVE PORTFOLIO MONITOR
# ==========================================================

class LivePortfolioMonitor:

    def run(

        self

    ):

        logger.info(

            "Starting Live Portfolio Monitor"

        )

        forecast = (

            MonitorRepository

            .load_forecast()

        )

        committee = (

            MonitorRepository

            .load_committee()

        )

        stress = (

            MonitorRepository

            .load_stress()

        )

        surveillance = (

            MonitorRepository

            .load_surveillance()

        )

        MonitorValidator.validate(

            forecast,

            committee,

            stress,

            surveillance

        )

        forecast_result = (

            ForecastMonitorEngine

            .evaluate(

                forecast

            )

        )

        committee_result = (

            CommitteeMonitorEngine

            .evaluate(

                committee

            )

        )

        stress_result = (

            StressMonitorEngine

            .evaluate(

                stress

            )

        )

        surveillance_result = (

            SurveillanceMonitorEngine

            .evaluate(

                surveillance

            )

        )

        alerts, statuses = (

            MonitorAggregator

            .combine(

                forecast_result,

                committee_result,

                stress_result,

                surveillance_result

            )

        )

        stress_dashboard = (

            StressDashboardBuilder

            .build(

                stress

            )

        )

        stress_dashboard.to_csv(

            STRESS_DASHBOARD_FILE,

            index=False
        
        )

        severity = (

            AlertSeverityEngine

            .summarize(

                statuses

            )

        )

        dashboard = (

            MonitorDashboardBuilder

            .build(

                statuses,

                severity

            )

        )

        return {

            "alerts":

                alerts,

            "statuses":

                statuses,

            "severity":

                severity,

            "dashboard":

                dashboard

        }

class MonitorHistoryEngine:

    @staticmethod
    def archive(


        dashboard

    ):

        logger.info(

            "Archiving Monitor History"

        )

        history_dir = (

            MONITORING_DIR

            / "history"

        )

        history_dir.mkdir(

            parents=True,

            exist_ok=True

        )

        history_file = (

            history_dir

            /

            f"monitor_"

            f"{pd.Timestamp.now().strftime('%Y%m%d')}"

            f".csv"

        )

        history_record = pd.DataFrame(

            [

                {

                    "Date":

                        pd.Timestamp.now()

                        .strftime(

                            "%Y-%m-%d"

                        ),

                    "Forecast_Status":

                        dashboard.loc[

                            dashboard["Category"]

                            ==

                            "Forecast",

                            "Status"

                        ]

                        .iloc[0],

                    "Committee_Status":

                        dashboard.loc[

                            dashboard["Category"]

                            ==

                            "Committee",

                            "Status"

                        ]

                        .iloc[0],

                    "Stress_Status":

                        dashboard.loc[

                            dashboard["Category"]

                            ==

                            "Stress",

                            "Status"

                        ]

                        .iloc[0],

                    "Surveillance_Status":

                        dashboard.loc[

                            dashboard["Category"]

                            ==

                            "Surveillance",

                            "Status"

                        ]

                        .iloc[0],

                    "Overall_Status":

                        dashboard.loc[

                            dashboard["Category"]

                            ==

                            "Overall",

                            "Status"

                        ]

                        .iloc[0]

                }

            ]

        )
        
        history_record.to_csv(

            history_file,

            index=False

        )

        return history_file
       
# ==========================================================
# STATUS EXPORTER
# ==========================================================

class MonitorStatusExporter:

    @staticmethod
    def export(

        statuses

    ):

        logger.info(

            "Exporting Monitor Status"

        )

        df = pd.DataFrame(

            statuses

        )

        df.to_csv(

            MONITOR_STATUS_FILE,

            index=False

        )

        return df
    
# ==========================================================
# ALERT EXPORTER
# ==========================================================

class MonitorAlertExporter:

    @staticmethod
    def export(

        alerts

    ):

        logger.info(

            "Exporting Monitor Alerts"

        )

        df = pd.DataFrame(

            alerts

        )

        df.to_csv(

            MONITOR_ALERTS_FILE,

            index=False

        )

        return df
    
# ==========================================================
# DASHBOARD EXPORTER
# ==========================================================

class MonitorDashboardExporter:

    @staticmethod
    def export(

        dashboard

    ):

        logger.info(

            "Exporting Monitor Dashboard"

        )

        dashboard.to_csv(

            MONITOR_DASHBOARD_FILE,

            index=False

        )

        return dashboard
    
# ==========================================================
# RUNNER
# ==========================================================

def run_example():

    result = (

        LivePortfolioMonitor()

        .run()

    )

    MonitorStatusExporter.export(

        result["statuses"]

    )

    MonitorAlertExporter.export(

        result["alerts"]

    )

    AlertHistoryEngine.append(

        result["alerts"]

    )

    MonitorDashboardExporter.export(

        result["dashboard"]

    )

    history_file = (

        MonitorHistoryEngine

        .archive(

            result["dashboard"]

        )

    )

    print(

        f"History: {history_file}"

    )

    print()

    print(

        "=" * 80

    )

    print(

        "LIVE PORTFOLIO MONITOR"

    )

    print(

        "=" * 80

    )

    print(

        f"Overall Severity: "

        f"{result['severity']}"

    )

    print()

    print(

        "Status Summary"

    )

    print(

        result["dashboard"]

    )

    print()

    if result["alerts"]:

        print(

            "Alerts"

        )

        print(

            pd.DataFrame(

                result["alerts"]

            )

        )

    else:

        print(

            "No Alerts Generated"

        )

    print(

        "=" * 80

    )

# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    run_example()