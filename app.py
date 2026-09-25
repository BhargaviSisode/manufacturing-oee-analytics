import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Page Config ----------
st.set_page_config(page_title="Manufacturing OEE Dashboard", layout="wide")

# ---------- Load Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/plant_oee_analytical_mart.csv")
    return df

df = load_data()

# ---------- Title ----------
st.title("🏭 Manufacturing Plant OEE & Downtime Intelligence")

# ---------- Sidebar Filter ----------
lines = ["All"] + sorted(df["production_line"].unique().tolist())
selected_line = st.sidebar.selectbox("Filter by Production Line", lines)

if selected_line != "All":
    filtered_df = df[df["production_line"] == selected_line]
else:
    filtered_df = df

# ---------- KPI Calculations ----------
avg_oee = filtered_df["oee_pct"].mean()
avg_availability = filtered_df["availability_pct"].mean()
total_downtime_hours = filtered_df["downtime_min"].sum() / 60
scrap_defect_rate = (filtered_df["defective_units"].sum() / filtered_df["total_units"].sum()) * 100

# ---------- KPI Cards ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Plant OEE", f"{avg_oee:.2f}%")
col2.metric("Avg Availability", f"{avg_availability:.2f}%")
col3.metric("Total Downtime Hours", f"{total_downtime_hours:.2f}")
col4.metric("Scrap Defect Rate", f"{scrap_defect_rate:.2f}%")

st.markdown("---")

# ---------- Charts Row ----------
chart_col1, chart_col2 = st.columns(2)

# Chart 1: Downtime by Reason (Horizontal Bar)
with chart_col1:
    st.subheader("Sum of Downtime (min) by Reason")
    downtime_by_reason = (
        filtered_df[filtered_df["downtime_reason"] != "None"]
        .groupby("downtime_reason")["downtime_min"]
        .sum()
        .sort_values()
    )
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.barh(downtime_by_reason.index, downtime_by_reason.values, color="#4A90D9")
    ax1.set_xlabel("Downtime (minutes)")
    st.pyplot(fig1)

# Chart 2: OEE by Production Line (Vertical Bar)
with chart_col2:
    st.subheader("Sum of OEE % by Production Line")
    oee_by_line = filtered_df.groupby("production_line")["oee_pct"].sum().sort_values(ascending=False)
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.bar(oee_by_line.index, oee_by_line.values, color="#4A90D9")
    ax2.set_ylabel("Sum of OEE %")
    st.pyplot(fig2)

st.markdown("---")

# ---------- Detailed Table ----------
st.subheader("Detailed Shift-Level Data")
table_cols = [
    "machine_id", "production_line", "shift_type",
    "downtime_reason", "downtime_min", "oee_pct", "oee_health_status"
]
st.dataframe(filtered_df[table_cols], use_container_width=True)

# ---------- Totals Footer ----------
st.markdown(f"""
**Total Downtime (min):** {filtered_df['downtime_min'].sum():,.0f}  
**Total OEE Sum:** {filtered_df['oee_pct'].sum():,.2f}
""")