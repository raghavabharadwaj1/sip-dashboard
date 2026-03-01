import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="SIP Timing Dashboard", layout="wide")

# ---------------- GREEN THEME ----------------
st.markdown("""
    <style>
    body {background-color: #e6f4ea;}
    .stMetric {background-color: white; padding: 15px; border-radius: 10px;}
    </style>
""", unsafe_allow_html=True)

# ---------------- DATABASE CONNECTION ----------------
def get_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="sip_analysis"
    )
    df = pd.read_sql("SELECT * FROM sip_calendar_cagr WHERE period_years = 3", conn)
    conn.close()
    return df

df = get_data()

st.title("📊 SIP Timing Analysis Dashboard")

# ---------------- SCHEME SELECT ----------------
schemes = df["scheme_name"].unique()
selected_scheme = st.selectbox("Select Scheme", schemes)

scheme_df = df[df["scheme_name"] == selected_scheme]

# ---------------- BEST / WORST ----------------
best_row = scheme_df.loc[scheme_df["cagr_percent"].idxmax()]
worst_row = scheme_df.loc[scheme_df["cagr_percent"].idxmin()]
gap = best_row["cagr_percent"] - worst_row["cagr_percent"]

col1, col2, col3 = st.columns(3)

col1.metric("Best SIP Day", f"Day {int(best_row['sip_day'])}", f"{round(best_row['cagr_percent'],2)}% CAGR")
col2.metric("Worst SIP Day", f"Day {int(worst_row['sip_day'])}", f"{round(worst_row['cagr_percent'],2)}% CAGR")
col3.metric("Performance Gap", f"{round(gap,2)}%")

# ---------------- GRAPH ----------------
fig = px.line(
    scheme_df,
    x="sip_day",
    y="cagr_percent",
    markers=True,
    color_discrete_sequence=["#0f9d58"]
)

fig.add_scatter(
    x=[best_row["sip_day"]],
    y=[best_row["cagr_percent"]],
    mode="markers",
    marker=dict(size=15, color="red"),
    name="Best Day"
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- OVERALL ANALYSIS ----------------
st.subheader("Overall Analysis")

overall_df = df.groupby("sip_day")["cagr_percent"].mean().reset_index()

best_overall = overall_df.loc[overall_df["cagr_percent"].idxmax()]
worst_overall = overall_df.loc[overall_df["cagr_percent"].idxmin()]

col1, col2, col3 = st.columns(3)

col1.metric("Overall Best Day", f"Day {int(best_overall['sip_day'])}", f"{round(best_overall['cagr_percent'],2)}%")
col2.metric("Overall Worst Day", f"Day {int(worst_overall['sip_day'])}", f"{round(worst_overall['cagr_percent'],2)}%")
col3.metric("Overall Gap", f"{round(best_overall['cagr_percent'] - worst_overall['cagr_percent'],2)}%")

fig2 = px.line(
    overall_df,
    x="sip_day",
    y="cagr_percent",
    markers=True,
    color_discrete_sequence=["#0f9d58"]
)

st.plotly_chart(fig2, use_container_width=True)

# ---------------- HEATMAP ----------------
st.subheader("CAGR Heatmap")

pivot = df.pivot(index="scheme_name", columns="sip_day", values="cagr_percent")

plt.figure(figsize=(12,6))
sns.heatmap(pivot, cmap="Greens", annot=False)
st.pyplot(plt)