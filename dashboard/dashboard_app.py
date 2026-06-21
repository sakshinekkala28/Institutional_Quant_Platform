# ==========================================================
# DASHBOARD APP
# Institutional Quant Platform
# ==========================================================

import streamlit as st
import pandas as pd
import requests

st.set_page_config(

    page_title="Institutional Quant Platform",

    layout="wide"

)

API_URL = "http://localhost:8000"


# ==========================================================
# API CLIENT
# ==========================================================

class APIClient:

    @staticmethod
    def get(endpoint):

        response = requests.get(

            f"{API_URL}/{endpoint}"

        )

        if response.status_code == 200:

            return response.json()

        return None


# ==========================================================
# HEADER
# ==========================================================

st.title(

    "Institutional Quant Platform"

)

st.caption(

    "Portfolio Management System"

)

# ==========================================================
# PORTFOLIO DASHBOARD
# ==========================================================

st.header("Portfolio")

portfolio = APIClient.get(

    "portfolio/live"

)

if portfolio:

    portfolio_df = pd.DataFrame(

        portfolio

    )

    st.dataframe(

        portfolio_df,

        use_container_width=True

    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(

            "Holdings",

            len(portfolio_df)

        )

    with col2:

        st.metric(

            "Weight Sum",

            round(

                portfolio_df[
                    "Target_Weight"
                ].sum(),

                4

            )

        )

    with col3:

        st.metric(

            "Max Position",

            round(

                portfolio_df[
                    "Target_Weight"
                ].max(),

                4

            )

        )

    import plotly.express as px

# ==========================================================
# RISK DASHBOARD
# ==========================================================

st.header("Risk Dashboard")

risk = APIClient.get(

    "risk/latest"

)

if risk:

    risk_df = pd.DataFrame(

        risk

    )

    st.dataframe(

        risk_df,

        use_container_width=True

    )

# ==========================================================
# SECTOR EXPOSURE
# ==========================================================

if portfolio:

    sector_weights = (

        portfolio_df

        .groupby("Sector")

        ["Target_Weight"]

        .sum()

        .reset_index()

    )

    fig = px.pie(

        sector_weights,

        names="Sector",

        values="Target_Weight",

        title="Sector Allocation"

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

# ==========================================================
# PERFORMANCE
# ==========================================================

st.header("Performance Dashboard")

performance = APIClient.get(

    "performance"

)

if performance:

    st.json(performance)

# ==========================================================
# GOVERNANCE
# ==========================================================

st.header("Governance")

governance = APIClient.get(

    "governance"

)

if governance:

    st.json(governance)

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(

    "Institutional Quant Platform v1.0"

)