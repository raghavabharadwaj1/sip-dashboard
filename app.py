import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os
from streamlit_option_menu import option_menu

st.set_page_config(page_title="SIP Timing Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    file_path = os.path.join(os.getcwd(), "SIP_Calendar_CAGR_Results.xlsx")
    return pd.read_excel(file_path)

df = load_data()

# Filter only 3-year data
df = df[df["period_years"] == 3]
st.sidebar.header("Filters")

schemes = df["scheme_name"].unique()

selected_schemes = st.sidebar.multiselect(
    "Select Schemes",
    schemes,
    default=schemes[:1]
)

filtered_df = df[df["scheme_name"].isin(selected_schemes)]

# ---------------- TITLE ----------------
st.title("📊 SIP Timing Analysis Dashboard")

# ---------------- NAVIGATION BAR ----------------
selected_top = option_menu(
    menu_title=None,
    options=["Home", "Compare Schemes", "Overall Analysis","Data"],
    icons=["house","bar-chart", "globe", "grid","book"],
    default_index=0,
    orientation="horizontal",
)

# ---------------- HOME PAGE ----------------
if selected_top == "Home":

    st.subheader("Welcome")

    st.write(
        """
        This dashboard analyzes **SIP investment timing** for mutual funds.

        It compares investment performance across **different SIP days (1–28)** 
        over a **3-year investment period**.

        Features available in this dashboard:

        • Scheme level analysis  
        • Multi-scheme comparison  
        • Overall best SIP day analysis  
        • Heatmap visualization of SIP timing sensitivity  
        """
    )
# ---------------- COMPARE SCHEMES ----------------
elif selected_top == "Compare Schemes":

    schemes = df["scheme_name"].unique()

    selected_schemes = st.sidebar.multiselect(
        "Select Schemes to Compare",
        schemes,
        default=schemes[:1]
    )

    scheme_df = filtered_df[df["scheme_name"].isin(selected_schemes)]

    fig = px.line(
        scheme_df,
        x="sip_day",
        y="cagr_%",
        color="scheme_name",
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_layout(
        title="SIP Day CAGR Comparison",
        xaxis_title="SIP Day",
        yaxis_title="CAGR %",
        legend_title="Scheme",
        template="plotly_white",
        yaxis=dict(range=[-20,30])
    )

    st.plotly_chart(fig, use_container_width=True)

    # Best SIP Day Summary
    st.subheader("Best SIP Day per Selected Scheme")

    summary_data = []

    for scheme in selected_schemes:
        temp = df[df["scheme_name"] == scheme]
        best_row = temp.loc[temp["cagr_%"].idxmax()]

        summary_data.append({
            "Scheme": scheme,
            "Best SIP Day": int(best_row["sip_day"]),
            "Best CAGR %": round(best_row["cagr_%"], 2)
        })

    summary_df = pd.DataFrame(summary_data)

    st.dataframe(summary_df, use_container_width=True)

# ---------------- OVERALL ANALYSIS ----------------
elif selected_top == "Overall Analysis":

    overall_df = filtered_df.groupby("sip_day")["cagr_%"].mean().reset_index()

    best_overall = overall_df.loc[overall_df["cagr_%"].idxmax()]
    worst_overall = overall_df.loc[overall_df["cagr_%"].idxmin()]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Overall Best Day",
        f"Day {int(best_overall['sip_day'])}",
        f"{round(best_overall['cagr_%'],2)}%"
    )

    col2.metric(
        "Overall Worst Day",
        f"Day {int(worst_overall['sip_day'])}",
        f"{round(worst_overall['cagr_%'],2)}%"
    )

    col3.metric(
        "Overall Gap",
        f"{round(best_overall['cagr_%'] - worst_overall['cagr_%'],2)}%"
    )

    fig2 = px.line(
        overall_df,
        x="sip_day",
        y="cagr_%",
        markers=True,
        color_discrete_sequence=["#0f9d58"]
    )

    fig2.update_layout(
        title="Average CAGR by SIP Day",
        xaxis_title="SIP Day",
        yaxis_title="Average CAGR %",
        template="plotly_white",
        yaxis=dict(range=[-20,30])
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------- data ----------------
elif selected_top == "Data":
    st.subheader("Selected Scheme Data")
    schemes = df["scheme_name"].unique()
    selected_schemes = st.sidebar.multiselect(
        "Select Schemes to View Data",
        schemes,
        default=schemes[:1]
    )
    
    filtered_df = df[df["scheme_name"].isin(selected_schemes)]
    
    st.dataframe(filtered_df,
use_container_width=True)


   
