from __future__ import annotations

import sys

import pandas as pd

import streamlit as st

import plotly.graph_objects as go

import plotly.express as px

from pathlib import Path

ROOT_DIR = (

    Path(__file__)

    .resolve()

    .parents[1]

)

sys.path.insert(

    0,

    str(

        ROOT_DIR

    )

)


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(

    page_title="Institutional Quant Platform",

    page_icon="📈",

    layout="wide"

)

# ==========================================================
# PATHS
# ==========================================================

PERFORMANCE_DIR = (

    ROOT_DIR

    / "data"

    / "performance"

)

EXECUTIVE_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "executive_dashboard.csv"

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

SURVEILLANCE_FILE = (

    PERFORMANCE_DIR

    / "surveillance_dashboard.csv"

)

# ==========================================================
# DATA LOADER
# ==========================================================

class DashboardRepository:

    @staticmethod
    def load_csv(

        file_path: Path

    ) -> pd.DataFrame:

        if not file_path.exists():

            return pd.DataFrame()

        return pd.read_csv(

            file_path

        )

    @classmethod
    def load_all(

        cls

    ):

        return {

            "dashboard":

                cls.load_csv(

                    EXECUTIVE_DASHBOARD_FILE

                ),

            "forecast":

                cls.load_csv(

                    FORECAST_FILE

                ),

            "governance":

                cls.load_csv(

                    GOVERNANCE_FILE

                ),

            "scenario":

                cls.load_csv(

                    SCENARIO_FILE

                ),

            "stress":

                cls.load_csv(

                    STRESS_FILE

                ),

            "committee":

                cls.load_csv(

                    COMMITTEE_PACK_FILE

                ),

            "surveillance":

                cls.load_csv(

                    SURVEILLANCE_FILE

                )

        }
    
data = (

    DashboardRepository

    .load_all()

)

# ==========================================================
# HEADER
# ==========================================================

st.title(

    "📈 Institutional Quant Platform"

)

st.markdown(

    """
    Portfolio Construction → Optimization →
    Performance → Risk → Forecast →
    Governance → Scenario Analysis →
    Stress Testing → Investment Committee
    """
)

# ==========================================================
# TABS
# ==========================================================

(

    executive_tab,

    forecast_tab,

    governance_tab,

    scenario_tab,

    stress_tab,

    committee_tab,

    surveillance_tab

) = st.tabs(

    [

        "Executive",

        "Forecast",

        "Governance",

        "Scenario Analysis",

        "Stress Testing",

        "Committee Pack",

        "Surveillance"

    ]

)


# ==========================================================
# EXECUTIVE TAB
# ==========================================================

with executive_tab:

    st.subheader(

        "Executive Dashboard"

    )

    dashboard = data["dashboard"]

    if dashboard.empty:

        st.warning(

            "Executive Dashboard Missing"

        )

    else:

        metrics = {}

        for _, row in dashboard.iterrows():

            metrics[

                row["Metric"]

            ] = row["Value"]

        col1, col2, col3 = st.columns(3)

        col1.metric(

            "Pack Score",

            metrics.get(

                "Pack_Score",

                "N/A"

            )

        )

        col2.metric(

            "Recommendation",

            metrics.get(

                "Recommendation",

                "N/A"

            )

        )

        col3.metric(

            "Committee View",

            metrics.get(

                "Committee_View",

                "N/A"

            )

        )

        st.dataframe(

            dashboard,

            use_container_width=True

        )

        dashboard_csv = (

            dashboard

            .to_csv(

                index=False

            )

        )

        st.download_button(

            "📥 Download Executive Dashboard",
        
            dashboard_csv,

            "executive_dashboard.csv",

            "text/csv"

        )

        st.subheader("Portfolio Health")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Pack Score",
            metrics.get("Pack_Score", "N/A")
        )

        col2.metric(
            "Committee View",
            metrics.get("Committee_View", "N/A")
        )

        col3.metric(
            "Recommendation",
            metrics.get("Recommendation", "N/A")
        )

        col4.metric(
            "Forecast Regime",
            metrics.get("Forecast_Regime", "N/A")
        )

        pack_score = float(
            metrics.get(
                "Pack_Score",
                0
            )
        )

        if pack_score >= 85:

            grade = "A"

        elif pack_score >= 70:

            grade = "B"

        elif pack_score >= 55:

            grade = "C"

        elif pack_score >= 40:

            grade = "D"

        else:

            grade = "F"

        st.metric(

            "Pack Grade",

            grade

        )


        fig = go.Figure(

            go.Indicator(

                mode="gauge+number",

                value=pack_score,

                title={"text": "Pack Score"},

                gauge={

                    "axis": {"range": [0, 100]},

                    "bar": {"color": "darkblue"}

                }
    
            )

        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ==========================================================
# FORECAST TAB
# ==========================================================

with forecast_tab:

    st.subheader(

        "Performance Forecast"

    )

    forecast = data["forecast"]

    if forecast.empty:

        st.warning(

            "Forecast Missing"

        )

    else:

        row = (

            forecast

            .iloc[0]

        )

        col1, col2, col3 = st.columns(3)

        col1.metric(

            "Expected Return (12M)",

            f"{row['Expected_Return_12M']:.2%}"

        )

        col2.metric(

            "Forecast Confidence",

            f"{row['Forecast_Confidence']:.2f}"

        )

        col3.metric(

            "Forecast Regime",

            row["Forecast_Regime"]

        )

        st.dataframe(

            forecast,

            use_container_width=True

        )

        forecast_csv = forecast.to_csv(
            index=False
        )

        st.download_button(

            "Download Forecast",

            forecast_csv,

            "performance_forecast.csv",

            "text/csv"

        )        

# ==========================================================
# SCENARIO ANALYSIS TAB
# ==========================================================

with scenario_tab:

    st.subheader(

        "Scenario Analysis"

    )

    scenario = data["scenario"]

    if scenario.empty:

        st.warning(

            "Scenario Analysis Missing"

        )

    else:

        st.dataframe(

            scenario,

            use_container_width=True

        )

        scenario_csv = (

           scenario

            .to_csv(

                index=False

            )

        )

        st.download_button(

            "📥 Download Scenario Analysis",

            scenario_csv,

            "scenario_analysis.csv",

            "text/csv"

        )

        fig = px.bar(

            scenario,

            x="Scenario",

            y="Scenario_Score",

            color="Scenario_Score",

            text="Scenario_Score"

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

        fig2 = px.bar(

            scenario,

            x="Scenario",

            y="Expected_Return",

            title="Scenario Expected Returns",

            text="Expected_Return"

        )

        st.plotly_chart(

            fig2,

            use_container_width=True

        )

        top = (

            scenario

            .sort_values(

                "Scenario_Score",

                ascending=False

            )

        )

        st.subheader(

            "Scenario Leaderboard"

        )

        st.dataframe(

            top[

                [

                    "Scenario",

                    "Scenario_Score",

                    "Scenario_Rank"

                ]

            ],

            use_container_width=True

        )    

# ==========================================================
# STRESS TESTING TAB
# ==========================================================

with stress_tab:

    st.subheader(

        "Stress Testing"

    )

    stress = data["stress"]

    if stress.empty:

        st.warning(

            "Stress Results Missing"

        )

    else:

        st.dataframe(

            stress.sort_values(

                "Stress_Rank"

            ),

            use_container_width=True

        )

        stress_csv = (

            stress

            .to_csv(

                index=False

            )

        )

        st.download_button(

            "📥 Download Stress Results",

            stress_csv,

            "stress_test_results.csv",

            "text/csv"

        )

        fig = px.bar(

            stress,

            x="Scenario",

            y="Stress_Score",

            color="Stress_Score",

            text="Stress_Score"

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

        fig2 = px.bar(

            stress,

            x="Scenario",

            y="Return_Impact",

            title="Stress Return Impact",

            text="Return_Impact"

        )

        st.plotly_chart(

            fig2,

            use_container_width=True

        )

        heat = stress.pivot_table(

            values="Stress_Score",

            index="Scenario"

        )

        fig = px.imshow(

            heat,
        
            text_auto=True,

            title="Stress Score Heatmap"

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )

# ==========================================================
# GOVERNANCE TAB
# ==========================================================

with governance_tab:

    st.subheader(

        "Governance Decision"

    )

    governance = data["governance"]

    if governance.empty:

        st.warning(

            "Governance File Missing"

        )

    else:

        row = (

            governance

            .iloc[0]

        )

        col1, col2, col3 = st.columns(3)

        col1.metric(

            "Committee Score",

            f"{row['Committee_Score']:.2f}"

        )

        col2.metric(

            "Governance Score",

            f"{row['Governance_Score']:.2f}"

        )

        col3.metric(

            "Risk Score",

            f"{row['Risk_Score']:.2f}"

        )

        st.success(

            f"Decision: {row['Decision']}"

        )

        if row["Decision"] == "APPROVE":

            st.success(
                "Investment Committee Approved"
            )

        else:

            st.error(
                "Investment Committee Rejected"
            )

        st.dataframe(

            governance,

            use_container_width=True

        )

        governance_csv = (

            governance

            .to_csv(
        
                index=False

            )
        
        )

        st.download_button(

            "📥 Download Governance Decision",

            governance_csv,

            "governance_decision.csv",

            "text/csv"

        )

# ==========================================================
# COMMITTEE PACK TAB
# ==========================================================

with committee_tab:

    st.subheader(

        "Investment Committee Pack"

    )

    committee = data["committee"]

    if committee.empty:

        st.warning(

            "Committee Pack Missing"

        )

    else:

        committee_csv = (

            committee

            .to_csv(

                index=False

            )

        )

        st.download_button(

            "📥 Download Committee Pack",

            committee_csv,

            "investment_committee_pack.csv",

            "text/csv"

        )

        sections = (

            committee[
                "Section"
            ]

            .dropna()

            .unique()

        )

        for section in sections:

            st.markdown(

                f"### {section}"

            )

            subset = (

                committee[
                    committee[
                        "Section"
                    ]
                    ==
                    section
                ]

            )

            st.dataframe(

                subset,

                use_container_width=True,

                hide_index=True

            )

# ==========================================================
# SURVEILLANCE TAB
# ==========================================================

with surveillance_tab:

    st.subheader(

        "Surveillance Dashboard"

    )

    surveillance = data["surveillance"]

    if surveillance.empty:

        st.warning(

            "Surveillance Missing"

        )

    else:

        surveillance_metrics = {}

        for _, row in surveillance.iterrows():

            surveillance_metrics[

                row["Metric"]

            ] = row["Value"]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(

            "Total Alerts",

            surveillance_metrics.get(

                "Total_Alerts",

                "N/A"

            )

        )

        col2.metric(

            "Critical Alerts",

            surveillance_metrics.get(

                "Critical_Alerts",

                "N/A"

            )

        )

        col3.metric(

            "Warning Alerts",

            surveillance_metrics.get(

                "Warning_Alerts",

                "N/A"

            )

        )

        col4.metric(

            "Health",

            surveillance_metrics.get(

                "Surveillance_Health",

                "N/A"

            )

        )

        st.dataframe(

            surveillance,

            use_container_width=True

        )

        surveillance_csv = (

            surveillance

            .to_csv(

                index=False

            )

        )

        st.download_button(

            "📥 Download Surveillance Dashboard",

            surveillance_csv,

            "surveillance_dashboard.csv",

            "text/csv"

        )

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(

    "Institutional Quant Platform | Portfolio Construction → Optimization → Performance → Risk → Forecast → Governance → Scenario Analysis → Stress Testing → Investment Committee"

)