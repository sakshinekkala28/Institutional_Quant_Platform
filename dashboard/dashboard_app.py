# ==========================================================
# DASHBOARD APP
# Institutional Quant Platform
# ==========================================================

import pandas as pd
import plotly.express as px
import requests

import streamlit as st

st.set_page_config(page_title="Institutional Quant Platform", layout="wide")

API_URL = "http://localhost:8000"


# ==========================================================
# API CLIENT
# ==========================================================


class APIClient:
    @staticmethod
    def get(endpoint):

        response = requests.get(f"{API_URL}/{endpoint}")

        if response.status_code == 200:
            return response.json()

        return None


# ==========================================================
# HEADER
# ==========================================================

st.title("Institutional Quant Platform")

st.caption("Portfolio Management System")

# ==========================================================
# PORTFOLIO DASHBOARD
# ==========================================================

st.header("Portfolio")

portfolio = APIClient.get("portfolio/live")

if portfolio:
    portfolio_df = pd.DataFrame(portfolio)

    weight_col = next(
        (
            c
            for c in [
                "Target_Weight",
                "Current_Weight",
                "Current_Weight_Old",
                "Weight",
            ]
            if c in portfolio_df.columns
        ),
        None,
    )

    st.dataframe(portfolio_df, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Holdings", len(portfolio_df))

    with col2:
        if weight_col:
            st.metric(
                "Weight Sum",
                round(portfolio_df[weight_col].fillna(0).sum(), 4),
            )
        else:
            st.metric("Weight Sum", "N/A")

    with col3:
        if weight_col:
            st.metric(
                "Max Position",
                round(portfolio_df[weight_col].fillna(0).max(), 4),
            )
        else:
            st.metric("Max Position", "N/A")


# ==========================================================
# RISK DASHBOARD
# ==========================================================

st.header("Risk Dashboard")

risk = APIClient.get("risk/latest")

if risk:
    risk_df = pd.DataFrame(risk)

    st.dataframe(risk_df, use_container_width=True)

# ==========================================================
# SECTOR EXPOSURE
# ==========================================================

if portfolio:
    if weight_col:
        sector_weights = (
            portfolio_df.groupby("Sector", as_index=False)[weight_col]
            .sum()
            .sort_values(weight_col, ascending=False)
        )

        fig = px.pie(
            sector_weights,
            names="Sector",
            values=weight_col,
            title="Sector Allocation",
        )

        st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# PERFORMANCE
# ==========================================================

st.header("Performance Dashboard")

performance = APIClient.get("performance")

if performance:
    st.json(performance)

# ==========================================================
# GOVERNANCE
# ==========================================================

st.header("Governance")

governance = APIClient.get("governance")

if governance:
    st.json(governance)

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption("Institutional Quant Platform v1.0")
