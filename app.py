"""
Energy Dignity Index (EDI) — Real-Time Intelligence Dashboard
India's premier energy access & dignity analytics platform
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

from realtime_data import (
    fetch_live_national_metrics,
    fetch_state_realtime_data,
    fetch_generation_mix,
    fetch_historical_trend,
    fetch_recent_policy_updates,
    STATE_ENERGY_DATA,
)
from enhanced_model import EnhancedEDIModel, compute_edi_dataframe

# ── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="EDI Intelligence | India Energy Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design System ───────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google Font ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

  /* ── Base reset ── */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* ── Full black background ── */
  .stApp {
    background: #000000 !important;
  }
  section[data-testid="stSidebar"] {
    background: #0a0a0a !important;
    border-right: 1px solid #1a1a1a;
  }
  .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
  }

  /* ── Typography ── */
  h1, h2, h3, h4, h5, h6,
  .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #ffffff !important;
    font-weight: 700;
    letter-spacing: -0.5px;
  }
  p, li, label, span,
  .stMarkdown p, .stMarkdown li {
    color: #a0a0a0 !important;
  }

  /* ── Hero header ── */
  .hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #888888 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    line-height: 1.1;
  }
  .hero-sub {
    font-size: 0.95rem;
    color: #555555 !important;
    font-weight: 400;
    margin-top: 0.4rem;
  }
  .live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #111111;
    border: 1px solid #222222;
    color: #888888 !important;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    padding: 4px 10px;
    border-radius: 4px;
    margin-top: 0.5rem;
  }
  .live-dot {
    width: 6px; height: 6px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse-dot 1.8s ease-in-out infinite;
    display: inline-block;
  }
  @keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.7); }
  }

  /* ── KPI cards ── */
  .kpi-card {
    background: #0d0d0d;
    border: 1px solid #1c1c1c;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s ease, transform 0.3s ease;
  }
  .kpi-card:hover {
    border-color: #333333;
    transform: translateY(-2px);
  }
  .kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #1a1a1a, #ffffff22, #1a1a1a);
    animation: shimmer 3s linear infinite;
  }
  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }
  .kpi-label {
    font-size: 0.72rem;
    color: #555555 !important;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
  }
  .kpi-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
  }
  .kpi-delta {
    font-size: 0.78rem;
    margin-top: 0.4rem;
    font-weight: 500;
  }
  .kpi-delta.up { color: #22c55e !important; }
  .kpi-delta.down { color: #ef4444 !important; }
  .kpi-delta.neutral { color: #888888 !important; }

  /* ── Section dividers ── */
  .section-title {
    font-size: 0.72rem;
    color: #444444 !important;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1a1a1a;
  }

  /* ── Tab styling ── */
  .stTabs [data-baseweb="tab-list"] {
    background: #0a0a0a !important;
    border-bottom: 1px solid #1a1a1a !important;
    gap: 0;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #555555 !important;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 0.7rem 1.4rem !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.25s ease;
  }
  .stTabs [aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 2px solid #ffffff !important;
    background: transparent !important;
  }
  .stTabs [data-baseweb="tab"]:hover {
    color: #cccccc !important;
    background: #111111 !important;
  }
  .stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding-top: 1.5rem !important;
  }

  /* ── Sidebar elements ── */
  .stSidebar .stMultiSelect label,
  .stSidebar .stSelectbox label,
  .stSidebar .stSlider label,
  .stSidebar p {
    color: #888888 !important;
    font-size: 0.82rem;
  }
  .sidebar-brand {
    font-size: 1.05rem;
    font-weight: 800;
    color: #ffffff !important;
    letter-spacing: -0.5px;
  }
  .sidebar-brand-sub {
    font-size: 0.72rem;
    color: #444444 !important;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  /* ── Dataframe ── */
  .stDataFrame {
    background: #0d0d0d !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 8px !important;
  }
  [data-testid="stDataFrameResizable"] {
    background: #0d0d0d !important;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: #1a1a1a !important;
    color: #ffffff !important;
    border: 1px solid #333333 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.5px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.25s ease !important;
  }
  .stButton > button:hover {
    background: #262626 !important;
    border-color: #555555 !important;
  }

  /* ── Select/Multi-select ── */
  .stMultiSelect [data-baseweb="select"] {
    background: #111111 !important;
    border-color: #222222 !important;
  }
  .stSelectbox [data-baseweb="select"] {
    background: #111111 !important;
    border-color: #222222 !important;
  }

  /* ── Slider ── */
  .stSlider [data-baseweb="slider"] { padding-top: 1.2rem; }

  /* ── Metrics (native) ── */
  [data-testid="stMetric"] {
    background: #0d0d0d !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 10px !important;
    padding: 1rem !important;
  }
  [data-testid="stMetricLabel"] { color: #666666 !important; }
  [data-testid="stMetricValue"] { color: #ffffff !important; }
  [data-testid="stMetricDelta"] svg { display: none; }

  /* ── Policy card ── */
  .policy-card {
    background: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.7rem;
    border-left: 3px solid #333333;
    transition: border-left-color 0.3s;
  }
  .policy-card.positive { border-left-color: #22c55e; }
  .policy-card.neutral  { border-left-color: #888888; }
  .policy-card.negative { border-left-color: #ef4444; }
  .policy-date { font-size: 0.72rem; color: #444444 !important; font-family: 'JetBrains Mono', monospace; }
  .policy-title { font-size: 0.92rem; font-weight: 700; color: #cccccc !important; margin: 0.2rem 0; }
  .policy-detail { font-size: 0.80rem; color: #555555 !important; }

  /* ── Risk badge ── */
  .risk-high { color: #ef4444 !important; font-weight: 700; }
  .risk-med  { color: #f59e0b !important; font-weight: 700; }
  .risk-low  { color: #22c55e !important; font-weight: 700; }

  /* ── Info box ── */
  .stAlert {
    background: #0d0d0d !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 8px !important;
    color: #888888 !important;
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: #0a0a0a; }
  ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }
  ::-webkit-scrollbar-thumb:hover { background: #3a3a3a; }

  /* ── Hide Streamlit branding ── */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Plotly dark template ────────────────────────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#888888", size=12),
    colorway=["#ffffff", "#555555", "#888888", "#333333", "#aaaaaa", "#222222"],
    xaxis=dict(gridcolor="#111111", zerolinecolor="#1a1a1a", linecolor="#1a1a1a"),
    yaxis=dict(gridcolor="#111111", zerolinecolor="#1a1a1a", linecolor="#1a1a1a"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1a1a1a"),
    title=dict(font=dict(color="#ffffff", size=14, family="Inter"), x=0.0, xanchor="left"),
    margin=dict(l=0, r=0, t=40, b=0),
)

GRAY_SCALE = ["#ffffff", "#d4d4d4", "#a3a3a3", "#737373", "#525252", "#404040", "#262626", "#171717"]


def apply_theme(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(**PLOT_THEME, height=height)
    fig.update_xaxes(gridcolor="#111111", zerolinecolor="#1a1a1a", linecolor="#0a0a0a")
    fig.update_yaxes(gridcolor="#111111", zerolinecolor="#1a1a1a", linecolor="#0a0a0a")
    return fig


# ── Caching ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_national_metrics():
    return fetch_live_national_metrics()

@st.cache_data(ttl=60)
def get_state_data():
    df = fetch_state_realtime_data()
    model = EnhancedEDIModel()
    return model.compute_for_dataframe(df)

@st.cache_data(ttl=300)
def get_historical():
    return fetch_historical_trend(years=7)

@st.cache_data(ttl=300)
def get_generation_mix():
    return fetch_generation_mix()

@st.cache_data(ttl=600)
def get_policy_updates():
    return fetch_recent_policy_updates()


# ── KPI card helper ──────────────────────────────────────────────────────────
def kpi_card(label: str, value: str, delta: str = "", delta_dir: str = "up"):
    dir_class = delta_dir if delta_dir in ("up", "down", "neutral") else "neutral"
    delta_html = f'<div class="kpi-delta {dir_class}">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {delta_html}
    </div>""", unsafe_allow_html=True)


# ── 3D Globe / Surface chart ─────────────────────────────────────────────────
def make_3d_edi_surface(state_df: pd.DataFrame) -> go.Figure:
    """3D surface of state-level EDI by area type."""
    pivot = state_df.pivot_table(index="state", columns="area", values="EDI")
    pivot = pivot.dropna().sort_values("urban", ascending=False).head(25)

    x_labels = pivot.index.tolist()
    x_idx = list(range(len(x_labels)))
    z_urban = pivot["urban"].values
    z_rural = pivot["rural"].values if "rural" in pivot.columns else z_urban * 0.88

    fig = go.Figure()

    # Urban surface
    fig.add_trace(go.Scatter3d(
        x=x_idx, y=[1] * len(x_idx), z=z_urban,
        mode="lines+markers",
        name="Urban",
        line=dict(color="white", width=4),
        marker=dict(size=5, color=z_urban, colorscale=[[0, "#333333"], [1, "#ffffff"]]),
    ))

    # Rural surface
    fig.add_trace(go.Scatter3d(
        x=x_idx, y=[0] * len(x_idx), z=z_rural,
        mode="lines+markers",
        name="Rural",
        line=dict(color="#555555", width=4),
        marker=dict(size=5, color=z_rural, colorscale=[[0, "#1a1a1a"], [1, "#888888"]]),
    ))

    # Vertical connectors
    for i, (u, r) in enumerate(zip(z_urban, z_rural)):
        fig.add_trace(go.Scatter3d(
            x=[i, i], y=[1, 0], z=[u, r],
            mode="lines",
            line=dict(color="#222222", width=1),
            showlegend=False,
        ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                ticktext=x_labels, tickvals=x_idx,
                tickfont=dict(size=8, color="#555555"),
                gridcolor="#111111", backgroundcolor="rgba(0,0,0,0)",
                showbackground=False,
            ),
            yaxis=dict(
                ticktext=["Rural", "Urban"], tickvals=[0, 1],
                tickfont=dict(size=10, color="#888888"),
                gridcolor="#111111", backgroundcolor="rgba(0,0,0,0)",
                showbackground=False,
            ),
            zaxis=dict(
                range=[0, 1], title="EDI",
                tickfont=dict(size=9, color="#666666"),
                gridcolor="#1a1a1a", backgroundcolor="rgba(0,0,0,0)",
                showbackground=False,
            ),
            camera=dict(eye=dict(x=1.8, y=-1.8, z=1.2)),
            aspectratio=dict(x=2.5, y=0.6, z=1),
        ),
        legend=dict(font=dict(color="#888888"), bgcolor="rgba(0,0,0,0)"),
        font=dict(family="Inter", color="#888888"),
        height=500,
        margin=dict(l=0, r=0, t=40, b=0),
        title=dict(
            text="Urban-Rural EDI Depth — Top 25 States",
            font=dict(color="#ffffff", size=14, family="Inter"),
            x=0, xanchor="left",
        ),
    )
    return fig


def make_3d_scatter(state_df: pd.DataFrame) -> go.Figure:
    """3D scatter: electrification × clean cooking × EDI."""
    df = state_df[state_df["area"] == "urban"].drop_duplicates("state")

    fig = go.Figure(data=[go.Scatter3d(
        x=df["electrification_pct"],
        y=df["clean_cooking_pct"],
        z=df["EDI"],
        mode="markers+text",
        text=df["state"].apply(lambda s: s[:10]),
        textposition="top center",
        textfont=dict(size=7, color="#555555"),
        marker=dict(
            size=6,
            color=df["EDI"],
            colorscale=[[0, "#1a1a1a"], [0.5, "#555555"], [1, "#ffffff"]],
            colorbar=dict(
                title=dict(text="EDI", font=dict(color="#666666", size=11)),
                tickfont=dict(color="#666666"),
                bordercolor="#1a1a1a",
                bgcolor="rgba(0,0,0,0)",
            ),
            showscale=True,
            line=dict(width=0.5, color="#333333"),
        ),
    )])

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Electrification %", gridcolor="#111111",
                       backgroundcolor="rgba(0,0,0,0)", showbackground=False,
                       tickfont=dict(color="#555555", size=9)),
            yaxis=dict(title="Clean Cooking %", gridcolor="#111111",
                       backgroundcolor="rgba(0,0,0,0)", showbackground=False,
                       tickfont=dict(color="#555555", size=9)),
            zaxis=dict(title="EDI", range=[0, 1], gridcolor="#1a1a1a",
                       backgroundcolor="rgba(0,0,0,0)", showbackground=False,
                       tickfont=dict(color="#555555", size=9)),
            camera=dict(eye=dict(x=1.5, y=-1.5, z=1.3)),
        ),
        font=dict(family="Inter", color="#888888"),
        height=480,
        margin=dict(l=0, r=0, t=50, b=0),
        title=dict(
            text="3D Nexus: Electrification × Clean Cooking × EDI",
            font=dict(color="#ffffff", size=14, family="Inter"),
            x=0, xanchor="left",
        ),
    )
    return fig


def make_radar(scores: dict, title: str = "Dimension Profile") -> go.Figure:
    cats = ["Access", "Affordability", "Reliability", "Health", "Productive", "Agency"]
    dims = ["A", "E", "R", "H", "P", "G"]
    vals = [scores.get(d, scores.get(f"S_{d}", 0)) for d in dims]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=cats + [cats[0]],
        fill="toself",
        fillcolor="rgba(255,255,255,0.05)",
        line=dict(color="#ffffff", width=2),
        name=title,
    ))
    # Reference circle at 0.5
    fig.add_trace(go.Scatterpolar(
        r=[0.5] * (len(cats) + 1),
        theta=cats + [cats[0]],
        mode="lines",
        line=dict(color="#333333", width=1, dash="dot"),
        showlegend=False,
    ))
    _radar_theme = {k: v for k, v in PLOT_THEME.items() if k not in ["xaxis", "yaxis", "colorway", "title", "margin"]}
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 1], visible=True, tickfont=dict(color="#444444", size=9),
                            gridcolor="#1a1a1a", linecolor="#1a1a1a"),
            angularaxis=dict(tickfont=dict(color="#888888", size=10), gridcolor="#1a1a1a"),
        ),
        showlegend=False,
        title=dict(text=title, font=dict(color="#ffffff", size=13), x=0, xanchor="left"),
        height=320,
        margin=dict(l=10, r=10, t=50, b=10),
        **_radar_theme,
    )
    return fig


def make_animated_bar(state_df: pd.DataFrame, metric: str = "EDI") -> go.Figure:
    """Animated horizontal bar sorted by EDI."""
    urban = state_df[state_df["area"] == "urban"].drop_duplicates("state")
    urban = urban.sort_values(metric, ascending=True)

    color_vals = urban[metric].values
    norm = (color_vals - color_vals.min()) / (np.ptp(color_vals) or 1)

    colors = [f"rgba({int(255*v)},{int(255*v)},{int(255*v)},1)" for v in norm]

    fig = go.Figure(go.Bar(
        x=urban[metric],
        y=urban["state"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.3f}" for v in urban[metric]],
        textposition="outside",
        textfont=dict(size=9, color="#555555"),
        hovertemplate="<b>%{y}</b><br>EDI: %{x:.4f}<extra></extra>",
    ))
    apply_theme(fig, height=max(420, len(urban) * 22))
    fig.update_layout(
        title=dict(text=f"{metric} by State (Urban)", font=dict(color="#ffffff", size=13)),
        xaxis=dict(range=[0, 1], tickfont=dict(color="#555555")),
        yaxis=dict(tickfont=dict(color="#888888", size=10)),
    )
    return fig


def make_generation_donut(mix: dict) -> go.Figure:
    labels = list(mix.keys())
    values = list(mix.values())
    colors = [
        "#ffffff", "#888888", "#555555", "#333333",
        "#aaaaaa", "#666666", "#222222", "#444444",
    ]
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.6,
        marker=dict(colors=colors[:len(labels)], line=dict(color="#000000", width=2)),
        textinfo="label+percent",
        textfont=dict(size=10, color="#888888"),
        hovertemplate="<b>%{label}</b><br>%{value:,} MW (%{percent})<extra></extra>",
    ))
    total_mw = sum(values)
    fig.add_annotation(
        text=f"<b>{total_mw/1000:.0f} GW</b><br><span style='font-size:10px;color:#555'>Total</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="#ffffff", family="Inter"),
        xref="paper", yref="paper",
    )
    apply_theme(fig, height=350)
    fig.update_layout(
        title=dict(text="National Generation Mix — Live", font=dict(color="#ffffff", size=13)),
        legend=dict(font=dict(color="#888888", size=10)),
        showlegend=True,
    )
    return fig


def make_trend_chart(hist_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    # Confidence band
    fig.add_trace(go.Scatter(
        x=list(hist_df["year"]) + list(hist_df["year"])[::-1],
        y=list(hist_df["urban_EDI"]) + list(hist_df["rural_EDI"])[::-1],
        fill="toself",
        fillcolor="rgba(255,255,255,0.04)",
        line=dict(width=0),
        name="Urban-Rural Range",
        showlegend=True,
    ))
    # National
    fig.add_trace(go.Scatter(
        x=hist_df["year"], y=hist_df["EDI"],
        mode="lines+markers",
        name="National EDI",
        line=dict(color="#ffffff", width=3),
        marker=dict(size=7, color="#ffffff", line=dict(width=2, color="#000000")),
        hovertemplate="<b>%{x}</b><br>EDI: %{y:.4f}<extra></extra>",
    ))
    # Urban
    fig.add_trace(go.Scatter(
        x=hist_df["year"], y=hist_df["urban_EDI"],
        mode="lines", name="Urban",
        line=dict(color="#888888", width=2, dash="dot"),
    ))
    # Rural
    fig.add_trace(go.Scatter(
        x=hist_df["year"], y=hist_df["rural_EDI"],
        mode="lines", name="Rural",
        line=dict(color="#444444", width=2, dash="dash"),
    ))

    apply_theme(fig, height=350)
    fig.update_layout(
        title=dict(text="National EDI Trajectory (2018-2024)", font=dict(color="#ffffff", size=13)),
        yaxis=dict(range=[0.3, 0.95], tickformat=".2f"),
        xaxis=dict(tickformat="d"),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    )
    return fig


def make_corr_heatmap(state_df: pd.DataFrame) -> go.Figure:
    dim_cols = [c for c in ["S_A", "S_E", "S_R", "S_H", "S_P", "S_G", "EDI"] if c in state_df.columns]
    labels = ["Access", "Affordability", "Reliability", "Health", "Productive", "Agency", "EDI"][:len(dim_cols)]
    corr = state_df[dim_cols].corr()

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=labels, y=labels,
        colorscale=[[0, "#000000"], [0.5, "#333333"], [1, "#ffffff"]],
        zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color="#888888"),
        hovertemplate="<b>%{x} × %{y}</b><br>r = %{z:.3f}<extra></extra>",
        colorbar=dict(tickfont=dict(color="#666666"), bordercolor="#1a1a1a",
                      bgcolor="rgba(0,0,0,0)", thickness=12),
    ))
    apply_theme(fig, height=380)
    fig.update_layout(
        title=dict(text="Dimension Correlation Matrix", font=dict(color="#ffffff", size=13)),
        xaxis=dict(tickfont=dict(color="#888888", size=10)),
        yaxis=dict(tickfont=dict(color="#888888", size=10)),
    )
    return fig


def make_projection_chart(projections: list, scenario: str) -> go.Figure:
    df = pd.DataFrame(projections)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["EDI"],
        mode="lines+markers",
        name="Projected EDI",
        line=dict(color="#ffffff", width=3),
        marker=dict(size=8, color="#ffffff", line=dict(color="#000000", width=2)),
        fill="tozeroy",
        fillcolor="rgba(255,255,255,0.04)",
        hovertemplate="Year +%{x}<br>EDI: %{y:.4f}<extra></extra>",
    ))
    fig.add_hline(y=1.0, line_dash="dot", line_color="#333333",
                  annotation_text="Full Dignity", annotation_font=dict(color="#555555"))
    fig.add_hline(y=0.7, line_dash="dot", line_color="#222222",
                  annotation_text="Target 2030", annotation_font=dict(color="#444444"))

    apply_theme(fig, height=320)
    fig.update_layout(
        title=dict(text=f"EDI Projection — {scenario} Scenario", font=dict(color="#ffffff", size=13)),
        yaxis=dict(range=[0, 1.05], tickformat=".2f"),
        xaxis=dict(title="Years from Now"),
    )
    return fig


# ── Main app ────────────────────────────────────────────────────────────────
def main():
    # ── Load data ──
    metrics = get_national_metrics()
    state_df = get_state_data()
    hist_df = get_historical()
    gen_mix = get_generation_mix()
    policy_updates = get_policy_updates()
    model = EnhancedEDIModel()

    dim_names = {
        "A": "Basic Access", "E": "Affordability",
        "R": "Reliability", "H": "Health & Environment",
        "P": "Productive Use", "G": "Agency",
    }

    # ── Sidebar ─────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">EDI Intelligence</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-brand-sub">Energy Dignity Index — India</div>', unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("**Filters**")
        all_states = sorted(state_df["state"].unique())
        selected_states = st.multiselect(
            "States",
            options=all_states,
            default=all_states[:12],
            key="state_filter",
        )
        selected_area = st.multiselect(
            "Area Type",
            options=["urban", "rural"],
            default=["urban", "rural"],
            key="area_filter",
        )
        st.markdown("---")

        st.markdown("**Model Configuration**")
        ensemble_alpha = st.slider(
            "Geometric weight (alpha)",
            min_value=0.0, max_value=1.0, value=0.70, step=0.05,
            help="Alpha=1 → pure geometric mean. Alpha=0 → arithmetic mean.",
        )
        model.ENSEMBLE_ALPHA = ensemble_alpha

        st.markdown("---")
        st.markdown(
            f'<div style="font-size:0.70rem;color:#333;">Last refresh: {metrics["timestamp"]}</div>',
            unsafe_allow_html=True,
        )
        if st.button("Refresh Data", key="refresh_btn"):
            st.cache_data.clear()
            st.rerun()

        st.markdown(
            f'<div style="font-size:0.70rem;color:#333;margin-top:0.5rem;">'
            f'Source: {metrics["data_source"]}</div>',
            unsafe_allow_html=True,
        )

    # ── Filter ──
    filtered = state_df[
        (state_df["state"].isin(selected_states)) &
        (state_df["area"].isin(selected_area))
    ]

    # ── Header ──────────────────────────────────────────────────────────────
    col_title, col_badge = st.columns([4, 1])
    with col_title:
        st.markdown('<div class="hero-title">Energy Dignity Index</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Real-time intelligence platform for India\'s energy access & dignity</div>', unsafe_allow_html=True)
    with col_badge:
        st.markdown(
            f'<div class="live-badge"><span class="live-dot"></span>LIVE — {metrics["timestamp"][-8:]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title">National Pulse</div>', unsafe_allow_html=True)

    # ── KPI row ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    national_edi = state_df["EDI"].mean()

    with k1:
        kpi_card("National EDI", f"{national_edi:.3f}", "+0.015 YoY", "up")
    with k2:
        kpi_card("Electrification", f"{metrics['electrification_rate']:.1f}%", "+0.3% YoY", "up")
    with k3:
        kpi_card("Clean Cooking", f"{metrics['clean_cooking_access']:.1f}%", "+4.8% YoY", "up")
    with k4:
        kpi_card("Renewables", f"{metrics['renewable_share']:.1f}%", "+6.2% YoY", "up")
    with k5:
        kpi_card("Live Demand", f"{metrics['current_demand_gw']:.1f} GW", f"Solar {metrics['current_solar_gw']:.1f} GW", "neutral")
    with k6:
        kpi_card("AT&C Losses", f"{metrics['at_c_losses']:.1f}%", "-1.2% YoY", "down")

    st.markdown('<div style="margin-top:2rem;"></div>', unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab_overview, tab_geo3d, tab_trends, tab_model, tab_policy = st.tabs([
        "Overview",
        "3D Geography",
        "Trends & Time Series",
        "Model & Simulation",
        "Policy Intelligence",
    ])

    # ── TAB 1: OVERVIEW ─────────────────────────────────────────────────────
    with tab_overview:
        col_l, col_r = st.columns([1, 1], gap="large")

        with col_l:
            # Trend chart
            st.plotly_chart(make_trend_chart(hist_df), use_container_width=True)

        with col_r:
            # Generation mix donut
            st.plotly_chart(make_generation_donut(gen_mix), use_container_width=True)

        # State bar + radar
        col_bar, col_radar = st.columns([3, 2], gap="large")

        with col_bar:
            urban_only = state_df[state_df["area"] == "urban"].drop_duplicates("state")
            if selected_states:
                urban_only = urban_only[urban_only["state"].isin(selected_states)]
            st.plotly_chart(make_animated_bar(urban_only if not urban_only.empty else state_df), use_container_width=True)

        with col_radar:
            # National average radar
            avg_scores = {
                d: float(filtered[f"S_{d}"].mean()) if f"S_{d}" in filtered.columns else 0.5
                for d in "AERHPG"
            }
            st.plotly_chart(make_radar(avg_scores, "National Average — Dimension Profile"), use_container_width=True)

            # Alkire-Foster stats
            af = model.alkire_foster(filtered)
            st.markdown(f"""
            <div style="background:#0d0d0d;border:1px solid #1a1a1a;border-radius:10px;padding:1rem 1.2rem;margin-top:0.5rem;">
              <div class="kpi-label">Alkire-Foster Poverty Measure (k=1/3)</div>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-top:0.6rem;">
                <div><div style="color:#555;font-size:0.70rem;text-transform:uppercase;letter-spacing:1px;">Headcount H</div>
                     <div style="color:#fff;font-size:1.4rem;font-weight:700;font-family:'JetBrains Mono';">{af['H']:.3f}</div></div>
                <div><div style="color:#555;font-size:0.70rem;text-transform:uppercase;letter-spacing:1px;">Intensity A</div>
                     <div style="color:#fff;font-size:1.4rem;font-weight:700;font-family:'JetBrains Mono';">{af['A']:.3f}</div></div>
                <div><div style="color:#555;font-size:0.70rem;text-transform:uppercase;letter-spacing:1px;">M0</div>
                     <div style="color:#fff;font-size:1.4rem;font-weight:700;font-family:'JetBrains Mono';">{af['M0']:.3f}</div></div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 2: 3D GEOGRAPHY ─────────────────────────────────────────────────
    with tab_geo3d:
        st.plotly_chart(make_3d_edi_surface(state_df), use_container_width=True)
        st.plotly_chart(make_3d_scatter(state_df), use_container_width=True)

        # Correlation heatmap
        st.plotly_chart(make_corr_heatmap(filtered if len(filtered) > 5 else state_df), use_container_width=True)

        # State table
        st.markdown('<div class="section-title">State-Level Data</div>', unsafe_allow_html=True)
        tbl_cols = ["state", "area", "EDI", "electrification_pct", "clean_cooking_pct",
                    "S_A", "S_E", "S_R", "S_H", "S_P", "S_G", "deprivation_score", "last_updated"]
        tbl_cols = [c for c in tbl_cols if c in filtered.columns]
        st.dataframe(
            filtered[tbl_cols].sort_values("EDI", ascending=False).round(4),
            use_container_width=True,
            height=350,
        )

    # ── TAB 3: TRENDS ───────────────────────────────────────────────────────
    with tab_trends:
        # Dimension trend animation
        dim_cols_avail = [f"S_{d}" for d in "AERHPG" if f"S_{d}" in hist_df.columns]
        dim_fig = go.Figure()
        for i, col in enumerate(dim_cols_avail):
            d = col[2]
            dim_fig.add_trace(go.Scatter(
                x=hist_df["year"], y=hist_df[col],
                mode="lines+markers",
                name=dim_names.get(d, d),
                line=dict(width=2, color=GRAY_SCALE[i % len(GRAY_SCALE)]),
                marker=dict(size=6),
            ))
        apply_theme(dim_fig, height=360)
        dim_fig.update_layout(
            title=dict(text="Dimension Score Trajectories 2018–2024", font=dict(color="#ffffff", size=13)),
            yaxis=dict(range=[0, 1], tickformat=".2f"),
            xaxis=dict(tickformat="d"),
            legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center", font=dict(color="#888888")),
        )
        st.plotly_chart(dim_fig, use_container_width=True)

        # Urban-rural gap over time
        gap_y = hist_df["urban_EDI"] - hist_df["rural_EDI"]
        gap_fig = go.Figure()
        gap_fig.add_trace(go.Bar(
            x=hist_df["year"], y=gap_y,
            name="Urban-Rural Gap",
            marker=dict(color=[f"rgba({int(220*v/0.15)},{int(220*v/0.15)},{int(220*v/0.15)},0.9)" for v in gap_y]),
            hovertemplate="<b>%{x}</b><br>Gap: %{y:.4f}<extra></extra>",
        ))
        apply_theme(gap_fig, height=280)
        gap_fig.update_layout(
            title=dict(text="Urban–Rural EDI Disparity Over Time", font=dict(color="#ffffff", size=13)),
            yaxis=dict(range=[0, 0.25], tickformat=".3f"),
            xaxis=dict(tickformat="d"),
        )
        st.plotly_chart(gap_fig, use_container_width=True)

    # ── TAB 4: MODEL & SIMULATION ────────────────────────────────────────────
    with tab_model:
        col_sim, col_results = st.columns([1, 1], gap="large")

        with col_sim:
            st.markdown("**Policy Scenario Projection**")
            scenario = st.selectbox(
                "Growth scenario",
                ["Optimistic", "Moderate", "Conservative"],
                key="scenario_sel",
            )
            scenarios = {
                "Optimistic":    {"A": 0.06, "E": 0.09, "R": 0.11, "H": 0.09, "P": 0.11, "G": 0.16},
                "Moderate":      {"A": 0.03, "E": 0.05, "R": 0.06, "H": 0.05, "P": 0.06, "G": 0.09},
                "Conservative":  {"A": 0.01, "E": 0.02, "R": 0.02, "H": 0.02, "P": 0.02, "G": 0.03},
            }
            avg_scores_dim = {
                d: float(filtered[f"S_{d}"].mean()) if f"S_{d}" in filtered.columns else 0.5
                for d in "AERHPG"
            }
            projections = model.project_edi(avg_scores_dim, scenarios[scenario], years=7)
            st.plotly_chart(make_projection_chart(projections, scenario), use_container_width=True)

        with col_results:
            st.markdown("**Sensitivity Analysis**")
            sensitivity = model.sensitivity_analysis(avg_scores_dim)
            # Visualise
            sens_fig = go.Figure(go.Bar(
                x=sensitivity["EDI Gain (+5%)"],
                y=sensitivity["Dimension"],
                orientation="h",
                marker=dict(
                    color=sensitivity["EDI Gain (+5%)"],
                    colorscale=[[0, "#1a1a1a"], [1, "#ffffff"]],
                ),
                text=[f"{v:.5f}" for v in sensitivity["EDI Gain (+5%)"]],
                textposition="outside",
                textfont=dict(size=9, color="#555555"),
                hovertemplate="<b>%{y}</b><br>EDI Gain: %{x:.5f}<extra></extra>",
            ))
            apply_theme(sens_fig, height=280)
            sens_fig.update_layout(
                title=dict(text="Sensitivity: EDI Gain per +5% Dimension Score", font=dict(color="#ffffff", size=13)),
                xaxis=dict(tickformat=".4f"),
            )
            st.plotly_chart(sens_fig, use_container_width=True)

        # Intervention simulator
        st.markdown('<div class="section-title">Policy Intervention Simulator</div>', unsafe_allow_html=True)
        sim_c1, sim_c2, sim_c3 = st.columns(3)
        with sim_c1:
            target_dim = st.selectbox(
                "Target Dimension",
                options=list(dim_names.keys()),
                format_func=lambda x: dim_names[x],
                key="target_dim",
            )
        with sim_c2:
            magnitude = st.slider(
                "Intervention Magnitude",
                min_value=0.0, max_value=0.5, value=0.10, step=0.01,
                key="magnitude_slider",
            )
        with sim_c3:
            if st.button("Simulate", key="sim_btn"):
                impact = model.calculate_policy_impact(avg_scores_dim, target_dim, magnitude)
                st.markdown(f"""
                <div class="kpi-card" style="margin-top:0.5rem;">
                  <div class="kpi-label">EDI Improvement</div>
                  <div class="kpi-value">+{impact['edi_improvement']:.4f}</div>
                  <div class="kpi-delta up">+{impact['percent_improvement']:.2f}% relative gain</div>
                </div>""", unsafe_allow_html=True)

        # Dimension breakdown table
        st.markdown('<div class="section-title">Dimension Score Breakdown</div>', unsafe_allow_html=True)
        result = model.compute(avg_scores_dim)
        breakdown_rows = []
        for d, dr in result.dimensions.items():
            breakdown_rows.append({
                "Dimension": dim_names.get(d, d),
                "Score": f"{dr.score:.4f}",
                "90% CI": f"[{dr.confidence_low:.3f}, {dr.confidence_high:.3f}]",
                "Weight": f"{dr.weight:.2%}",
                "Contribution": f"{dr.contribution:.4f}",
            })
        st.dataframe(pd.DataFrame(breakdown_rows), use_container_width=True, height=250)

        # Risk flags
        if result.risk_flags:
            st.markdown('<div class="section-title">Risk Flags</div>', unsafe_allow_html=True)
            for flag in result.risk_flags:
                color_cls = "risk-high" if "Critical" in flag else "risk-med"
                st.markdown(f'<div class="{color_cls}" style="padding:0.3rem 0;">{flag}</div>', unsafe_allow_html=True)

    # ── TAB 5: POLICY INTELLIGENCE ───────────────────────────────────────────
    with tab_policy:
        col_cards, col_priority = st.columns([2, 3], gap="large")

        with col_cards:
            st.markdown('<div class="section-title">Recent Policy Updates</div>', unsafe_allow_html=True)
            for p in policy_updates:
                card_cls = "policy-card " + p.get("impact", "neutral")
                st.markdown(f"""
                <div class="{card_cls}">
                  <div class="policy-date">{p['date']}</div>
                  <div class="policy-title">{p['title']}</div>
                  <div class="policy-detail">{p['detail']}</div>
                </div>""", unsafe_allow_html=True)

        with col_priority:
            st.markdown('<div class="section-title">Priority Ranking — States by Need</div>', unsafe_allow_html=True)
            # Identify bottom states by EDI
            urban_states = state_df[state_df["area"] == "urban"].drop_duplicates("state").copy()
            urban_states["priority_score"] = (1 - urban_states["EDI"]) * 0.6 + urban_states["deprivation_score"] * 0.4
            priority_df = urban_states.sort_values("priority_score", ascending=False)[
                ["state", "EDI", "deprivation_score", "clean_cooking_pct", "electrification_pct", "priority_score"]
            ].head(20).round(4)

            # Colour EDI column
            priority_fig = go.Figure(go.Bar(
                x=priority_df["priority_score"],
                y=priority_df["state"],
                orientation="h",
                marker=dict(
                    color=priority_df["EDI"],
                    colorscale=[[0, "#ffffff"], [1, "#1a1a1a"]],
                    reversescale=True,
                    colorbar=dict(title="EDI", tickfont=dict(color="#666666"), thickness=10),
                ),
                text=[f"EDI {v:.3f}" for v in priority_df["EDI"]],
                textposition="outside",
                textfont=dict(size=8, color="#555555"),
                hovertemplate="<b>%{y}</b><br>Priority: %{x:.3f}<br>EDI: %{marker.color:.4f}<extra></extra>",
            ))
            apply_theme(priority_fig, height=480)
            priority_fig.update_layout(
                title=dict(text="States Ranked by Intervention Priority", font=dict(color="#ffffff", size=13)),
                xaxis=dict(range=[0, 0.9], tickformat=".2f"),
                yaxis=dict(tickfont=dict(color="#888888", size=9)),
            )
            st.plotly_chart(priority_fig, use_container_width=True)

        # Marginal impact table
        st.markdown('<div class="section-title">Marginal Impact Analysis</div>', unsafe_allow_html=True)
        avg_scores_dim = {
            d: float(state_df[f"S_{d}"].mean()) if f"S_{d}" in state_df.columns else 0.5
            for d in "AERHPG"
        }
        sensitivity_df = model.sensitivity_analysis(avg_scores_dim)
        sensitivity_df["Dimension"] = sensitivity_df["Dimension"].map(lambda x: dim_names.get(x, x))
        st.dataframe(sensitivity_df, use_container_width=True, height=260)


if __name__ == "__main__":
    main()
