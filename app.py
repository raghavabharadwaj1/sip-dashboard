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
df = df[df["period_years"] == 3]

st.title("📊 SIP Timing Analysis Dashboard")

# ---------------- NAVIGATION ----------------
selected_top = option_menu(
    menu_title=None,
    options=["Home", "Analysis Dashboard"],
    icons=["house", "graph-up"],
    default_index=0,
    orientation="horizontal",
)

# ---------------- HOME ----------------
if selected_top == "Home":

    st.subheader("Welcome")

    st.write("""
    This dashboard analyzes **SIP investment timing performance** for mutual funds.

    It compares how SIP investments perform depending on which day of the month
    the investment is made.

    Features included:

    • Scheme-level analysis  
    • Multi-scheme comparison  
    • Overall SIP day performance  
    • Heatmap visualization  
    """)

# ---------------- MAIN DASHBOARD ----------------
elif selected_top == "Analysis Dashboard":

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Scheme Analysis", "📊 Compare Schemes", "🌍 Overall Analysis", "🔥 Heatmap"]
    )

    # ---------------- TAB 1 : SCHEME ANALYSIS ----------------
    with tab1:

        schemes = df["scheme_name"].unique()

        selected_scheme = st.selectbox("Select Scheme", schemes)

        scheme_df = df[df["scheme_name"] == selected_scheme]

        best_row = scheme_df.loc[scheme_df["cagr_%"].idxmax()]
        worst_row = scheme_df.loc[scheme_df["cagr_%"].idxmin()]
        gap = best_row["cagr_%"] - worst_row["cagr_%"]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Best SIP Day",
            f"Day {int(best_row['sip_day'])}",
            f"{round(best_row['cagr_%'],2)}%"
        )

        col2.metric(
            "Worst SIP Day",
            f"Day {int(worst_row['sip_day'])}",
            f"{round(worst_row['cagr_%'],2)}%"
        )

        col3.metric(
            "Performance Gap",
            f"{round(gap,2)}%"
        )

        fig = px.line(
            scheme_df,
            x="sip_day",
            y="cagr_%",
            markers=True,
            color_discrete_sequence=["#0f9d58"]
        )

        fig.update_layout(
            title="CAGR by SIP Day",
            xaxis_title="SIP Day",
            yaxis_title="CAGR %",
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

    # ---------------- TAB 2 : COMPARE SCHEMES ----------------
    with tab2:

        schemes = df["scheme_name"].unique()

        selected_schemes = st.multiselect(
            "Select Schemes to Compare",
            schemes,
            default=schemes[:1]
        )

        scheme_df = df[df["scheme_name"].isin(selected_schemes)]

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
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)

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

    # ---------------- TAB 3 : OVERALL ANALYSIS ----------------
    with tab3:

        overall_df = df.groupby("sip_day")["cagr_%"].mean().reset_index()

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
            template="plotly_white"
        )

        st.plotly_chart(fig2, use_container_width=True)

    # ---------------- TAB 4 : HEATMAP ----------------
    with tab4:

        st.subheader("CAGR Heatmap")

        pivot = df.pivot(index="scheme_name", columns="sip_day", values="cagr_%")

        plt.figure(figsize=(12,6))
        sns.heatmap(pivot, cmap="Greens", annot=False)

        st.pyplot(plt)
