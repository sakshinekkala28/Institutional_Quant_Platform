from __future__ import annotations

import logging

from pathlib import Path

import pandas as pd

from reportlab.platypus import (

    SimpleDocTemplate,

    Paragraph,

    Spacer,

    PageBreak

)

from reportlab.lib.styles import (

    getSampleStyleSheet

)

from core.settings import settings

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

REPORT_DIR = (

    ROOT_DIR

    / "data"

    / "reports"

)

REPORT_DIR.mkdir(

    parents=True,

    exist_ok=True

)

PERFORMANCE_SUMMARY_FILE = (

    PERFORMANCE_DIR

    / "performance_summary.csv"

)

FORECAST_FILE = (

    PERFORMANCE_DIR

    / "performance_forecast.csv"

)

GOVERNANCE_FILE = (

    PERFORMANCE_DIR

    / "governance_decision.csv"

)

SCENARIO_FILE = (

    PERFORMANCE_DIR

    / "scenario_analysis.csv"

)

STRESS_FILE = (

    PERFORMANCE_DIR

    / "stress_test_results.csv"

)

COMMITTEE_PACK_FILE = (

    PERFORMANCE_DIR

    / "investment_committee_pack.csv"

)

EXECUTIVE_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "executive_dashboard.csv"

)

PDF_REPORT_FILE = (

    REPORT_DIR

    / "investment_committee_report.pdf"

)

# ==========================================================
# REPOSITORY
# ==========================================================

class PDFRepository:

    @staticmethod
    def load_summary():

        return pd.read_csv(

            PERFORMANCE_SUMMARY_FILE

        )

    @staticmethod
    def load_forecast():

        return pd.read_csv(

            FORECAST_FILE

        )

    @staticmethod
    def load_governance():

        return pd.read_csv(

            GOVERNANCE_FILE

        )

    @staticmethod
    def load_scenarios():

        return pd.read_csv(

            SCENARIO_FILE

        )

    @staticmethod
    def load_stress():

        return pd.read_csv(

            STRESS_FILE

        )

    @staticmethod
    def load_committee_pack():

        return pd.read_csv(

            COMMITTEE_PACK_FILE

        )

    @staticmethod
    def load_dashboard():

        return pd.read_csv(

            EXECUTIVE_DASHBOARD_FILE

        )
    
# ==========================================================
# VALIDATOR
# ==========================================================

class PDFValidator:

    @staticmethod
    def validate(

        summary,

        forecast,

        governance

    ):

        if summary.empty:

            raise ValueError(

                "Summary Empty"

            )

        if forecast.empty:

            raise ValueError(

                "Forecast Empty"

            )

        if governance.empty:

            raise ValueError(

                "Governance Empty"

            )
        
# ==========================================================
# EXECUTIVE SUMMARY SECTION
# ==========================================================

class ExecutiveSummarySection:

    @staticmethod
    def build(

        story,

        dashboard: pd.DataFrame,

        styles

    ):

        logger.info(

            "Building Executive Summary"

        )

        story.append(

            Paragraph(

                "Executive Summary",

                styles["Heading1"]

            )

        )

        for _, row in dashboard.iterrows():

            story.append(

                Paragraph(

                    f"<b>{row['Metric']}</b>: {row['Value']}",

                    styles["BodyText"]

                )

            )

        story.append(

            Spacer(

                1,

                12

            )

        )

# ==========================================================
# FORECAST SECTION
# ==========================================================

class ForecastSection:

    @staticmethod
    def build(

        story,

        forecast: pd.DataFrame,

        styles

    ):

        logger.info(

            "Building Forecast Section"

        )

        row = (

            forecast

            .iloc[0]

        )

        story.append(

            Paragraph(

                "Performance Forecast",

                styles["Heading1"]

            )

        )

        story.append(

            Paragraph(

                (

                    f"Forecast Regime: "

                    f"{row['Forecast_Regime']}"

                ),

                styles["BodyText"]

            )

        )

        story.append(

            Paragraph(

                (

                    f"Expected 12M Return: "

                    f"{row['Expected_Return_12M']:.2%}"

                ),

                styles["BodyText"]

            )

        )

        story.append(

            Paragraph(

                (

                    f"Expected Sharpe: "

                    f"{row['Expected_Sharpe']:.2f}"

                ),

                styles["BodyText"]

            )

        )

        story.append(

            Paragraph(

                (

                    f"Forecast Confidence: "

                    f"{row['Forecast_Confidence']:.2f}"

                ),

                styles["BodyText"]

            )

        )

        story.append(

            Spacer(

                1,

                12

            )

        )

# ==========================================================
# GOVERNANCE SECTION
# ==========================================================

class GovernanceSection:

    @staticmethod
    def build(

        story,

        governance: pd.DataFrame,

        styles

    ):

        logger.info(

            "Building Governance Section"

        )

        row = (

            governance

            .iloc[0]

        )

        story.append(

            Paragraph(

                "Governance Decision",

                styles["Heading1"]

            )

        )

        story.append(

            Paragraph(

                (

                    f"Decision: "

                    f"{row['Decision']}"

                ),

                styles["BodyText"]

            )

        )

        story.append(

            Paragraph(

                (

                    f"Committee Score: "

                    f"{row['Committee_Score']:.2f}"

                ),

                styles["BodyText"]

            )

        )

        story.append(

            Paragraph(

                (

                    f"Governance Score: "

                    f"{row['Governance_Score']:.2f}"

                ),

                styles["BodyText"]

            )

        )

        story.append(

            Paragraph(

                (

                    f"Risk Score: "

                    f"{row['Risk_Score']:.2f}"

                ),

                styles["BodyText"]

            )

        )

        story.append(

            Spacer(

                1,

                12

            )

        )

# ==========================================================
# COMMITTEE PACK SECTION
# ==========================================================

class CommitteePackSection:

    @staticmethod
    def build(

        story,

        committee_pack: pd.DataFrame,

        styles

    ):

        logger.info(

            "Building Committee Pack Section"

        )

        story.append(

            Paragraph(

                "Investment Committee Pack",

                styles["Heading1"]

            )

        )

        current_section = None

        for _, row in committee_pack.iterrows():

            section = row.get(

                "Section",

                ""

            )

            if section != current_section:

                current_section = section

                story.append(

                    Paragraph(

                        str(section),

                        styles["Heading2"]

                    )

                )

            story.append(

                Paragraph(

                    (

                        f"<b>{row['Metric']}</b>: "

                        f"{row['Value']}"

                    ),

                    styles["BodyText"]

                )

            )

        story.append(

            Spacer(

                1,

                12

            )

        )

# ==========================================================
# SCENARIO SECTION
# ==========================================================

class ScenarioSection:

    @staticmethod
    def build(

        story,

        scenarios: pd.DataFrame,

        styles

    ):

        logger.info(

            "Building Scenario Section"

        )

        story.append(

            Paragraph(

                "Scenario Analysis",

                styles["Heading1"]

            )

        )

        ranked = (

            scenarios

            .sort_values(

                "Scenario_Rank"

            )

        )

        for _, row in ranked.iterrows():

            story.append(

                Paragraph(

                    (

                        f"<b>{row['Scenario']}</b> | "

                        f"Return: {row['Expected_Return']:.2%} | "

                        f"Score: {row['Scenario_Score']:.2f}"

                    ),

                    styles["BodyText"]

                )

            )

        story.append(

            Spacer(

                1,

                12

            )

        )

# ==========================================================
# STRESS TESTING SECTION
# ==========================================================

class StressTestingSection:

    @staticmethod
    def build(

        story,

        stress_df: pd.DataFrame,

        styles

    ):

        logger.info(

            "Building Stress Testing Section"

        )

        story.append(

            Paragraph(

                "Stress Testing",

                styles["Heading1"]

            )

        )

        ranked = (

            stress_df

            .sort_values(

                "Stress_Rank"

            )

        )

        for _, row in ranked.iterrows():

            story.append(

                Paragraph(

                    (

                        f"<b>{row['Scenario']}</b> | "

                        f"Impact: {row['Return_Impact']:.2%} | "

                        f"Score: {row['Stress_Score']:.2f}"

                    ),

                    styles["BodyText"]

                )

            )

        story.append(

            Spacer(

                1,

                12

            )

        )

# ==========================================================
# PDF REPORT BUILDER
# ==========================================================

class PDFReportBuilder:

    def build(

        self

    ):

        logger.info(

            "Building PDF Report"

        )

        summary = (

            PDFRepository

            .load_summary()

        )

        forecast = (

            PDFRepository

            .load_forecast()

        )

        governance = (

            PDFRepository

            .load_governance()

        )

        scenarios = (

            PDFRepository

            .load_scenarios()

        )

        stress_df = (

            PDFRepository

            .load_stress()

        )

        committee_pack = (

            PDFRepository

            .load_committee_pack()

        )

        dashboard = (

            PDFRepository

            .load_dashboard()

        )

        PDFValidator.validate(

            summary,

            forecast,

            governance

        )

        styles = (

            getSampleStyleSheet()

        )

        story = []

        story.append(

            Paragraph(

                "Institutional Investment Committee Report",

                styles["Title"]

            )

        )

        story.append(

            Spacer(

                1,

                20

            )

        )

        ExecutiveSummarySection.build(

            story,

            dashboard,

            styles

        )

        ForecastSection.build(

            story,

            forecast,

            styles

        )

        GovernanceSection.build(

            story,

            governance,

            styles

        )

        ScenarioSection.build(

            story,

            scenarios,

            styles

        )

        StressTestingSection.build(

            story,

            stress_df,

            styles

        )

        story.append(

            PageBreak()

        )

        CommitteePackSection.build(

            story,

            committee_pack,

            styles

        )

        return story

# ==========================================================
# PDF EXPORT ENGINE
# ==========================================================

class PDFExportEngine:

    @staticmethod
    def export():

        logger.info(

            "Exporting PDF Report"

        )

        story = (

            PDFReportBuilder()

            .build()

        )

        document = (

            SimpleDocTemplate(

                str(

                    PDF_REPORT_FILE

                )

            )

        )

        document.build(

            story

        )

        logger.info(

            "PDF Report Exported"

        )

        return PDF_REPORT_FILE
    
# ==========================================================
# REPORT SUMMARY ENGINE
# ==========================================================

class ReportSummaryEngine:

    @staticmethod
    def build():

        dashboard = (

            PDFRepository

            .load_dashboard()

        )

        summary = {}

        for _, row in dashboard.iterrows():

            summary[

                str(

                    row["Metric"]

                )

            ] = (

                row["Value"]

            )

        return summary
    
# ==========================================================
# RUNNER
# ==========================================================

def run_example():

    pdf_path = (

        PDFExportEngine

        .export()

    )

    summary = (

        ReportSummaryEngine

        .build()

    )

    print()

    print(

        "=" * 80

    )

    print(

        "INSTITUTIONAL PDF REPORT"

    )

    print(

        "=" * 80

    )

    print(

        f"Report: {pdf_path}"

    )

    print()

    for metric, value in summary.items():

        print(

            f"{metric}: {value}"

        )

    print(

        "=" * 80

    )

# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    run_example()