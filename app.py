import streamlit as st
import pandas as pd
import plotly.express as px
import os
from streamlit_option_menu import option_menu

# ---------------- CONFIG ----------------
st.set_page_config(page_title="SIP Timing Dashboard", layout="wide")
# This puts it at the top left of the sidebar
if os.path.exists("logo.png"): # Change "logo.png" to your actual filename
    st.sidebar.image("logo.png", use_container_width=True)
    st.sidebar.markdown("---")
else:
    st.sidebar.warning("Logo file not found.")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    file_path = os.path.join(os.getcwd(), "SIP_Calendar_CAGR_Results.xlsx")
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    else:
        # Returning a dummy dataframe structure to prevent immediate crashes if file is missing
        return pd.DataFrame(columns=["scheme_name", "sip_day", "cagr_%", "period_years"])

df = load_data()

if df.empty:
    st.error("Data file 'SIP_Calendar_CAGR_Results.xlsx' not found. Please ensure it is in the same directory.")
    st.stop()

# ---------------- TITLE ----------------
st.title("📊 MUTUAL FUNDS-Akhir Kaunsa din sahi hai")

# ---------------- NAVIGATION BAR ----------------
selected_top = option_menu(
    menu_title=None,
    options=["Home", "Compare Schemes", "Overall Analysis", "Data"],
    icons=["house", "bar-chart", "globe", "grid"],
    default_index=0,
    orientation="horizontal",
)

# ---------------- HOME PAGE ----------------
if selected_top == "Home":
    st.subheader("Welcome")
    st.write(
        """
        This dashboard analyzes **SIP investment timing** for mutual funds.
        It compares investment performance across **different SIP days (1–28)** over various investment periods.

        **Features available:**
        * Scheme level analysis  
        * Multi-scheme comparison  
        * Overall best SIP day analysis  
        * Data exploration
        """
    )

# ---------------- COMPARE SCHEMES ----------------
elif selected_top == "Compare Schemes":
    st.sidebar.header("Filters")
    schemes = df["scheme_name"].unique()
    selected_schemes = st.sidebar.multiselect(
        "Select Schemes",
        schemes,
        default=schemes[:1] if len(schemes) > 0 else None
    )

    if not selected_schemes:
        st.warning("Please select at least one scheme from the sidebar.")
    else:
        scheme_df = df[df["scheme_name"].isin(selected_schemes)]
        
        # Best SIP Day Metrics by Period
        st.subheader("Best SIP Day Metrics")
        periods = sorted(df["period_years"].unique())
        cols = st.columns(len(periods))

        for i, p in enumerate(periods):
            temp = scheme_df[scheme_df["period_years"] == p]
            if not temp.empty:
                best_row = temp.loc[temp["cagr_%"].idxmax()]
                cols[i].metric(
                    f"Best Day (Year {p})",
                    f"Day {int(best_row['sip_day'])}",
                    f"{round(best_row['cagr_%'], 2)}% CAGR"
                )

        # Visualizations
        if len(selected_schemes) == 1:
            st.subheader(f"Analysis for {selected_schemes[0]}")
            
            # Single Scheme Best/Worst
            best_row = scheme_df.loc[scheme_df["cagr_%"].idxmax()]
            worst_row = scheme_df.loc[scheme_df["cagr_%"].idxmin()]

            m1, m2 = st.columns(2)
            m1.metric("Overall Best Day", f"Day {int(best_row['sip_day'])}", f"{round(best_row['cagr_%'], 2)}%")
            m2.metric("Overall Worst Day", f"Day {int(worst_row['sip_day'])}", f"{round(worst_row['cagr_%'], 2)}%")

            fig = px.line(
                scheme_df, x="sip_day", y="cagr_%", color="period_years",
                markers=True, title="SIP Day Performance by Period"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.subheader("SIP Day CAGR Comparison")
            fig = px.line(
                scheme_df, x="sip_day", y="cagr_%", color="scheme_name",
                facet_col="period_years", markers=True
            )
            st.plotly_chart(fig, use_container_width=True)

# ---------------- OVERALL ANALYSIS ----------------
elif selected_top == "Overall Analysis":
    st.subheader("Market-Wide SIP Performance")
    
    periods = sorted(df["period_years"].unique())
    
    for p in periods:
        temp = df[df["period_years"] == p]
        overall_df = temp.groupby("sip_day")["cagr_%"].mean().reset_index()
        
        best_row = overall_df.loc[overall_df["cagr_%"].idxmax()]
        
        st.write(f"### Performance for {p} Year Period")
        st.metric(
            f"Average Best Day (Year {p})",
            f"Day {int(best_row['sip_day'])}",
            f"{round(best_row['cagr_%'], 2)}% Avg CAGR"
        )
      
        fig2 = px.bar(
            overall_df, x="sip_day", y="cagr_%",
            title=f"Average CAGR by SIP Day ({p} Year Period)",
            color="cagr_%"
        )
        st.plotly_chart(fig2, use_container_width=True)

# ---------------- DATA ----------------
elif selected_top == "Data":
    st.subheader("Raw Data Explorer")
    schemes = df["scheme_name"].unique()
    selected_schemes = st.sidebar.multiselect(
        "Select Schemes to View Data",
        schemes,
        default=schemes[:1] if len(schemes) > 0 else None
    )
    
    if selected_schemes:
        filtered_df = df[df["scheme_name"].isin(selected_schemes)]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)
