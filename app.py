import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OEE Pulse | Plant Intelligence", page_icon="🔥", layout="wide")

# ---------------- NEON DATA PULSE STYLE ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sora', sans-serif;
    }

    .stApp {
        background: #0A0A0F;
        background-image:
            radial-gradient(circle at 10% 10%, rgba(255, 0, 200, 0.12) 0%, transparent 35%),
            radial-gradient(circle at 90% 20%, rgba(0, 240, 255, 0.12) 0%, transparent 35%),
            radial-gradient(circle at 30% 90%, rgba(255, 220, 0, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 80% 85%, rgba(120, 0, 255, 0.1) 0%, transparent 40%);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1350px;
    }

    /* HEADER */
    .pulse-header {
        text-align: center;
        padding: 1.8rem 1rem 2.2rem 1rem;
        margin-bottom: 1.5rem;
    }
    .pulse-title {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #FF00C8, #00F0FF 40%, #FFDC00 70%, #7800FF);
        background-size: 300% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 6s linear infinite;
    }
    @keyframes shine {
        to { background-position: 300% center; }
    }
    .pulse-subtitle {
        font-family: 'JetBrains Mono', monospace;
        color: #8A8FA3;
        font-size: 0.9rem;
        margin-top: 0.5rem;
        letter-spacing: 0.05em;
    }

    /* METRIC CARDS - Neon glass, each different color */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 18px;
        padding: 1.3rem 1.4rem !important;
        transition: all 0.3s ease;
    }
    div[data-testid="column"]:nth-child(1) [data-testid="stMetric"] {
        border: 1.5px solid rgba(255, 0, 200, 0.5);
        box-shadow: 0 0 25px rgba(255, 0, 200, 0.15);
    }
    div[data-testid="column"]:nth-child(2) [data-testid="stMetric"] {
        border: 1.5px solid rgba(0, 240, 255, 0.5);
        box-shadow: 0 0 25px rgba(0, 240, 255, 0.15);
    }
    div[data-testid="column"]:nth-child(3) [data-testid="stMetric"] {
        border: 1.5px solid rgba(255, 220, 0, 0.5);
        box-shadow: 0 0 25px rgba(255, 220, 0, 0.15);
    }
    div[data-testid="column"]:nth-child(4) [data-testid="stMetric"] {
        border: 1.5px solid rgba(120, 0, 255, 0.5);
        box-shadow: 0 0 25px rgba(120, 0, 255, 0.15);
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-6px) scale(1.02);
    }
    [data-testid="stMetricLabel"] {
        font-family: 'JetBrains Mono', monospace !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8A8FA3 !important;
        font-size: 0.7rem !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Sora', sans-serif !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 15, 22, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] label {
        font-family: 'JetBrains Mono', monospace !important;
        color: #00F0FF !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.75rem !important;
    }

    /* Section headers */
    h3 {
        font-family: 'Sora', sans-serif !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        letter-spacing: -0.01em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    hr {
        border-color: rgba(255,255,255,0.08) !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.08);
    }

    [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
    }

    .stMarkdown p {
        font-family: 'JetBrains Mono', monospace;
        color: #8A8FA3;
    }
</style>

<div class="pulse-header">
    <div class="pulse-title">⚡ OEE PULSE</div>
    <div class="pulse-subtitle">// REAL-TIME PLANT PERFORMANCE INTELLIGENCE ENGINE //</div>
</div>
""", unsafe_allow_html=True)

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/plant_oee_analytical_mart.csv")
    return df

df = load_data()

# ---------------- Sidebar Filter ----------------
st.sidebar.markdown("### 🎛️ CONTROL PANEL")
lines = ["All"] + sorted(df["production_line"].unique().tolist())
selected_line = st.sidebar.selectbox("PRODUCTION LINE", lines)

if selected_line != "All":
    filtered_df = df[df["production_line"] == selected_line]
else:
    filtered_df = df

# ---------------- KPI Calculations ----------------
avg_oee = filtered_df["oee_pct"].mean()
avg_availability = filtered_df["availability_pct"].mean()
total_downtime_hours = filtered_df["downtime_min"].sum() / 60
scrap_defect_rate = (filtered_df["defective_units"].sum() / filtered_df["total_units"].sum()) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("AVG PLANT OEE", f"{avg_oee:.2f}%")
col2.metric("AVG AVAILABILITY", f"{avg_availability:.2f}%")
col3.metric("DOWNTIME (HRS)", f"{total_downtime_hours:.2f}")
col4.metric("SCRAP RATE", f"{scrap_defect_rate:.2f}%")

st.markdown("---")

# ---------------- Neon Plotly Charts (Single Gradient per Chart) ----------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("### 🔻 Downtime by Root Cause")
    downtime_by_reason = (
        filtered_df[filtered_df["downtime_reason"] != "None"]
        .groupby("downtime_reason")["downtime_min"]
        .sum()
        .sort_values()
        .reset_index()
    )
    fig1 = px.bar(
        downtime_by_reason, x="downtime_min", y="downtime_reason",
        orientation="h",
        color="downtime_min",
        color_continuous_scale=["#3D1A5C", "#FF00C8"],
        text="downtime_min"
    )
    fig1.update_traces(texttemplate='%{text}', textposition='outside', marker_line_width=0)
    fig1.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8ECEF", family="JetBrains Mono"),
        showlegend=False, height=380,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)", title="DOWNTIME (MIN)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", title=""),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    st.markdown("### ⚡ OEE % by Production Line")
    oee_by_line = filtered_df.groupby("production_line")["oee_pct"].sum().sort_values(ascending=False).reset_index()
    fig2 = px.bar(
        oee_by_line, x="production_line", y="oee_pct",
        color="oee_pct",
        color_continuous_scale=["#0A3D4A", "#00F0FF"],
        text="oee_pct"
    )
    fig2.update_traces(texttemplate='%{text:.0f}', textposition='outside', marker_line_width=0)
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8ECEF", family="JetBrains Mono"),
        showlegend=False, height=380,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="rgba(255,255,255,0.08)", title=""),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)", title="SUM OF OEE %"),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ---------------- Detailed Table ----------------
st.markdown("### 📋 Shift-Level Data Feed")
table_cols = [
    "machine_id", "production_line", "shift_type",
    "downtime_reason", "downtime_min", "oee_pct", "oee_health_status"
]
st.dataframe(filtered_df[table_cols], use_container_width=True)

st.markdown(f"""
**Total Downtime:** {filtered_df['downtime_min'].sum():,.0f} min &nbsp;&nbsp;⚡&nbsp;&nbsp; **Total OEE Sum:** {filtered_df['oee_pct'].sum():,.2f}
""")