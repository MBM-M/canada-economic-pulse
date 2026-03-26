import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Canada's Economic Pulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}

/* Main background */
.stApp {
    background-color: #0e1117;
    color: #e8e8e8;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161b27;
    border-right: 1px solid #2a2f3e;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
    border: 1px solid #2a3555;
    border-radius: 12px;
    padding: 16px 20px;
}

[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #7a8aaa !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.8rem !important;
    color: #e8e8e8 !important;
}

[data-testid="stMetricDelta"] svg {
    display: none;
}

/* Header banner */
.header-banner {
    background: linear-gradient(135deg, #0d1b3e 0%, #1a2d5a 50%, #0d2240 100%);
    border: 1px solid #2a4080;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.header-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%);
    pointer-events: none;
}

.header-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.header-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    color: #7a9acc;
    font-weight: 300;
    margin: 0;
}

.header-badge {
    display: inline-block;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    color: #60a5fa;
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 1rem;
}

/* Section headers */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #e8e8e8;
    border-left: 3px solid #3b82f6;
    padding-left: 0.75rem;
    margin: 1.5rem 0 1rem 0;
}

/* Finding cards */
.finding-card {
    background: linear-gradient(135deg, #1a2035 0%, #1c2438 100%);
    border: 1px solid #2a3555;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

.finding-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #3b82f6;
    margin-bottom: 0.3rem;
}

.finding-text {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: #c8d4e8;
    line-height: 1.5;
}

/* Divider */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #2a3555, transparent);
    margin: 1.5rem 0;
}

/* Footer */
.footer {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: #4a5568;
    text-align: center;
    padding: 2rem 0 1rem 0;
    border-top: 1px solid #1e2535;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc = os.path.join(base, "processed")
    return {
        "wages_vs_cpi":        pd.read_csv(os.path.join(proc, "wages_vs_cpi.csv")),
        "wages_annual":        pd.read_csv(os.path.join(proc, "wages_annual.csv")),
        "cpi_annual":          pd.read_csv(os.path.join(proc, "cpi_annual.csv")),
        "employment_annual":   pd.read_csv(os.path.join(proc, "employment_annual.csv")),
        "employment_monthly":  pd.read_csv(os.path.join(proc, "employment_monthly.csv")),
    }

data = load_data()
wages_vs_cpi      = data["wages_vs_cpi"]
wages_annual      = data["wages_annual"]
cpi_annual        = data["cpi_annual"]
employment_annual = data["employment_annual"]

PROVINCES = [
    "British Columbia", "Alberta", "Saskatchewan", "Manitoba",
    "Ontario", "Quebec", "New Brunswick", "Nova Scotia",
    "Prince Edward Island", "Newfoundland and Labrador",
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#c8d4e8"),
    xaxis=dict(gridcolor="#1e2535", linecolor="#2a3555", tickcolor="#2a3555"),
    yaxis=dict(gridcolor="#1e2535", linecolor="#2a3555", tickcolor="#2a3555"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2a3555", borderwidth=1),
    margin=dict(l=20, r=20, t=50, b=20),
)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p style="font-family:Syne;font-size:1.1rem;font-weight:700;color:#e8e8e8;">Filters</p>', unsafe_allow_html=True)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    year_min, year_max = int(wages_vs_cpi["year"].min()), int(wages_vs_cpi["year"].max())
    year_range = st.slider("Year range", year_min, year_max, (year_min, year_max))

    st.markdown("**Provinces**")
    selected_provinces = st.multiselect(
        "Select provinces",
        options=PROVINCES,
        default=["British Columbia", "Ontario", "Alberta", "Quebec"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.75rem;color:#4a5568;font-family:Inter;">
    Data: Statistics Canada<br>
    Tables 14-10-0023-01, 18-10-0005-01, 14-10-0064-01<br><br>
    All indices set to 2014 = 100
    </p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <div class="header-badge">Statistics Canada · 2014–2024</div>
    <div class="header-title">Canada's Economic Pulse</div>
    <div class="header-subtitle">Are Canadians keeping up? Wages, housing costs & employment across the provinces.</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI metrics
# ─────────────────────────────────────────────
national = wages_vs_cpi[wages_vs_cpi["geo"] == "Canada"].copy()
national_filtered = national[
    (national["year"] >= year_range[0]) & (national["year"] <= year_range[1])
]

latest = national_filtered[national_filtered["year"] == national_filtered["year"].max()].iloc[0]
earliest = national_filtered[national_filtered["year"] == national_filtered["year"].min()].iloc[0]

wage_growth    = latest["avg_hourly_wage"] - earliest["avg_hourly_wage"]
shelter_gap    = latest["shelter_index"] - latest["wage_index"]
nat_avg_wage   = latest["avg_hourly_wage"]

# Worst affordability gap province
prov_latest = wages_vs_cpi[
    (wages_vs_cpi["year"] == year_range[1]) &
    (wages_vs_cpi["geo"].isin(PROVINCES))
].copy()
prov_latest["gap"] = prov_latest["shelter_index"] - prov_latest["wage_index"]
worst_prov = prov_latest.loc[prov_latest["gap"].idxmax(), "geo"]
worst_gap  = prov_latest["gap"].max()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Avg Hourly Wage (Canada)", f"${nat_avg_wage:.2f}",
              delta=f"+${wage_growth:.2f} since {year_range[0]}")
with col2:
    st.metric("Wage Index", f"{latest['wage_index']:.1f}",
              delta=f"vs 100 in {year_range[0]}")
with col3:
    st.metric("Shelter CPI Index", f"{latest['shelter_index']:.1f}",
              delta=f"Gap: {shelter_gap:+.1f} pts vs wages")
with col4:
    st.metric("Hardest Hit Province", worst_prov,
              delta=f"Shelter leads wages by {worst_gap:.1f} pts")

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Chart 1 — Wages vs CPI national
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Wages vs. Housing Costs — National (2014 = 100)</div>', unsafe_allow_html=True)

nat_chart = national[
    (national["year"] >= year_range[0]) & (national["year"] <= year_range[1])
]

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=nat_chart["year"], y=nat_chart["wage_index"],
    name="Avg Hourly Wage Index",
    line=dict(color="#3b82f6", width=3),
    mode="lines+markers", marker=dict(size=6)
))
fig1.add_trace(go.Scatter(
    x=nat_chart["year"], y=nat_chart["shelter_index"],
    name="Shelter CPI Index",
    line=dict(color="#f43f5e", width=3, dash="dash"),
    mode="lines+markers", marker=dict(size=6)
))
fig1.add_trace(go.Scatter(
    x=nat_chart["year"], y=nat_chart["cpi_index"],
    name="All-Items CPI Index",
    line=dict(color="#f59e0b", width=2, dash="dot"),
    mode="lines"
))
fig1.add_hline(y=100, line_color="#2a3555", line_dash="solid", opacity=0.6)
fig1.update_layout(
    **PLOTLY_LAYOUT,
    height=380,
    yaxis_title="Index (base year = 100)",
    xaxis_title="Year",
    hovermode="x unified"
)
st.plotly_chart(fig1, use_container_width=True)

# ─────────────────────────────────────────────
# Chart 2 — Provincial comparison
# ─────────────────────────────────────────────
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-header">Provincial Wage vs. Shelter CPI Trends</div>', unsafe_allow_html=True)

if selected_provinces:
    prov_chart = wages_vs_cpi[
        (wages_vs_cpi["geo"].isin(selected_provinces)) &
        (wages_vs_cpi["year"] >= year_range[0]) &
        (wages_vs_cpi["year"] <= year_range[1])
    ]

    col_a, col_b = st.columns(2)

    with col_a:
        fig2a = px.line(
            prov_chart, x="year", y="wage_index", color="geo",
            title="Wage Index by Province",
            labels={"wage_index": "Wage Index", "year": "Year", "geo": "Province"},
            template="plotly_dark"
        )
        fig2a.update_layout(**PLOTLY_LAYOUT, height=340)
        fig2a.add_hline(y=100, line_color="#2a3555", opacity=0.5)
        st.plotly_chart(fig2a, use_container_width=True)

    with col_b:
        fig2b = px.line(
            prov_chart, x="year", y="shelter_index", color="geo",
            title="Shelter CPI Index by Province",
            labels={"shelter_index": "Shelter Index", "year": "Year", "geo": "Province"},
            template="plotly_dark"
        )
        fig2b.update_layout(**PLOTLY_LAYOUT, height=340)
        fig2b.add_hline(y=100, line_color="#2a3555", opacity=0.5)
        st.plotly_chart(fig2b, use_container_width=True)

    # Affordability gap bar chart
    st.markdown('<div class="section-header">Affordability Gap by Province (Shelter Index − Wage Index)</div>', unsafe_allow_html=True)
    gap_data = wages_vs_cpi[
        (wages_vs_cpi["year"] == year_range[1]) &
        (wages_vs_cpi["geo"].isin(PROVINCES))
    ].copy()
    gap_data["gap"] = gap_data["shelter_index"] - gap_data["wage_index"]
    gap_data = gap_data.sort_values("gap", ascending=True)
    gap_data["color"] = gap_data["gap"].apply(lambda x: "#f43f5e" if x > 0 else "#22c55e")

    fig3 = go.Figure(go.Bar(
        x=gap_data["gap"],
        y=gap_data["geo"],
        orientation="h",
        marker_color=gap_data["color"],
        text=gap_data["gap"].round(1),
        textposition="outside",
        textfont=dict(color="#c8d4e8", size=11)
    ))
    fig3.add_vline(x=0, line_color="#4a5568", line_width=1.5)
    fig3.update_layout(
        **PLOTLY_LAYOUT,
        height=380,
        xaxis_title="Index points (positive = shelter outpaced wages)",
        annotations=[dict(
            text=f"As of {year_range[1]} · Red = shelter outpaced wages · Green = wages outpaced shelter",
            xref="paper", yref="paper", x=0, y=-0.15,
            showarrow=False, font=dict(size=11, color="#4a5568")
        )]
    )
    st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────
# Chart 3 — Employment
# ─────────────────────────────────────────────
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-header">Employment by Industry (2014–2024)</div>', unsafe_allow_html=True)

top_industries = (
    employment_annual[employment_annual["year"] == 2019]
    .nlargest(8, "avg_employed_thousands")["industry"]
    .tolist()
)
emp_chart = employment_annual[
    (employment_annual["industry"].isin(top_industries)) &
    (employment_annual["year"] >= year_range[0]) &
    (employment_annual["year"] <= year_range[1])
]

fig4 = px.line(
    emp_chart, x="year", y="avg_employed_thousands", color="industry",
    title="Top 8 Industries by Employment",
    labels={"avg_employed_thousands": "Avg Employed (thousands)", "year": "Year", "industry": "Industry"},
    template="plotly_dark"
)
if year_range[0] <= 2020 <= year_range[1]:
    fig4.add_vline(x=2020, line_dash="dash", line_color="#f43f5e",
                   opacity=0.6, annotation_text="COVID-19",
                   annotation_font_color="#f43f5e")
fig4.update_layout(
    **PLOTLY_LAYOUT,
    height=420,
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,
        xanchor="left",
        x=0,
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=11)
    ),
    margin=dict(l=20, r=20, t=50, b=140),
)
st.plotly_chart(fig4, use_container_width=True)

# Industry stats table below the chart
latest_emp = employment_annual[employment_annual["year"] == year_range[1]]
base_emp   = employment_annual[employment_annual["year"] == 2019]
merged_emp = latest_emp.merge(base_emp[["industry", "avg_employed_thousands"]], on="industry", suffixes=("_latest", "_2019"))
merged_emp = merged_emp[merged_emp["industry"].isin(top_industries)].copy()
merged_emp["change_pct"] = ((merged_emp["avg_employed_thousands_latest"] - merged_emp["avg_employed_thousands_2019"]) / merged_emp["avg_employed_thousands_2019"] * 100).round(1)
merged_emp = merged_emp.sort_values("avg_employed_thousands_latest", ascending=False)

cols = st.columns(len(merged_emp))
for i, (_, row) in enumerate(merged_emp.iterrows()):
    label = row["industry"].split("[")[0].strip()
    label = label[:22] + "…" if len(label) > 22 else label
    change = row["change_pct"]
    color  = "#22c55e" if change >= 0 else "#f43f5e"
    arrow  = "▲" if change >= 0 else "▼"
    with cols[i]:
        st.markdown(f"""
        <div style="background:#1a2035;border:1px solid #2a3555;border-radius:8px;
                    padding:8px 6px;text-align:center;">
            <div style="font-size:0.6rem;color:#7a8aaa;font-family:Inter;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                        margin-bottom:4px;">{label}</div>
            <div style="font-size:1rem;font-family:Syne;color:#e8e8e8;font-weight:700;">
                {row["avg_employed_thousands_latest"]:,.0f}k
            </div>
            <div style="font-size:0.75rem;color:{color};font-family:Inter;">
                {arrow} {abs(change)}% vs 2019
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Key Findings
# ─────────────────────────────────────────────
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-header">Key Findings</div>', unsafe_allow_html=True)

findings = [
    ("Wages vs. Housing (National)",
     "Nationally, wage growth slightly outpaced shelter CPI by 2024 (wage index ~138 vs. shelter ~135), but the gap narrowed sharply after 2020 — Canadians are barely keeping ahead."),
    ("Provincial Divergence",
     "Prairie provinces were hit hardest — Manitoba (+10.6 pts), Alberta (+9.7 pts), and Saskatchewan (+5.0 pts) saw shelter costs outpace wages. Atlantic Canada and Quebec fared better, with wages pulling ahead."),
    ("Post-COVID Labour Shift",
     "Strongest employment growth 2019→2024: Professional & technical services (+27%), Public administration (+24.8%), Finance & insurance (+19.3%). The knowledge economy and public sector led recovery."),
    ("Sectors Still Lagging",
     "Agriculture (-21.1%), Fishing & trapping (-11.5%), Forestry & logging (-10.1%), and Retail trade (-1.7%) all remain below pre-COVID employment levels as of 2024."),
]

col1, col2 = st.columns(2)
for i, (label, text) in enumerate(findings):
    with (col1 if i % 2 == 0 else col2):
        st.markdown(f"""
        <div class="finding-card">
            <div class="finding-label">{label}</div>
            <div class="finding-text">{text}</div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Data: Statistics Canada open data · Tables 14-10-0023-01, 18-10-0005-01, 14-10-0064-01<br>
    Built with Python, Pandas, Plotly & Streamlit
</div>
""", unsafe_allow_html=True)