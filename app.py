import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tilgungschart",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# Design tokens
# ─────────────────────────────────────────────────────────────────────────────
DARK_BG  =  "#0f1117"
PANEL    =  "#151821"
BORDER   =  "#1e2235"
BORDER2  =  "#2e3347"
GREEN    =  "#00c896"
RED      =  "#ff4d6d"
AMBER    =  "#f59e0b"
BLUE     =  "#3b82f6"
PURPLE   =  "#a78bfa"
DIM      =  "#4a5568"
MID      =  "#8892a4"
BRT      =  "#e2e8f0"
MONO     =  "DM Mono, monospace"
SYNE     =  "Syne, sans-serif"

# Per-bank trace colors for comparison charts
BANK_COLORS = [
    {"interest": "#ff4d6d", "principal": "#00c896", "balance": "#f59e0b",
     "cum_prin": "#3b82f6", "cum_int": "#ff4d6d", "marker": "#00c896"},   # Bank 1
    {"interest": "#a78bfa", "principal": "#22d3ee", "balance": "#f472b6",
     "cum_prin": "#60a5fa", "cum_int": "#a78bfa", "marker": "#a78bfa"},   # Bank 2
    {"interest": "#fb923c", "principal": "#34d399", "balance": "#fbbf24",
     "cum_prin": "#818cf8", "cum_int": "#fb923c", "marker": "#fbbf24"},   # Bank 3
]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Syne', sans-serif;
    background: #0f1117 !important;
    color: #e2e8f0 !important;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #1a1d27; }
::-webkit-scrollbar-thumb { background: #2e3347; border-radius: 3px; }

.main .block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1600px; }

/* ── Header ── */
.ep-header {
    display: flex; align-items: center; gap: 18px;
    padding: 0 0 24px 0; border-bottom: 2px solid #1e2235; margin-bottom: 28px;
}
.ep-logo-block {
    width: 48px; height: 48px; background: #00c896; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; font-weight: 800; color: #0f1117; letter-spacing: -2px;
}
.ep-title { font-size: 1.8rem; font-weight: 800; color: #f1f5f9; letter-spacing: -1px; line-height: 1; }
.ep-subtitle { font-size: 0.72rem; color: #4a5568; font-family: 'DM Mono', monospace; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }
.ep-badge {
    margin-left: auto; background: #151821; border: 1px solid #2e3347;
    padding: 5px 12px; font-size: 0.68rem; color: #00c896;
    font-family: 'DM Mono', monospace; letter-spacing: 1.5px; text-transform: uppercase;
}

/* ── Section label ── */
.ep-section { 
    font-size: 0.65rem; font-family: 'DM Mono', monospace; letter-spacing: 3px;
    text-transform: uppercase; color: #00c896; margin-bottom: 14px;
    padding-left: 10px; border-left: 3px solid #00c896;
}

/* ── Grid helpers ── */
.grid-header { 
    font-family: 'DM Mono', monospace; font-size: 0.6rem; color: #00c896; 
    letter-spacing: 1px; text-transform: uppercase; 
    border-bottom: 1px solid #2e3347; padding-bottom: 4px; margin-bottom: 6px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.grid-row-label { 
    color: #8892a4; font-size: 0.72rem; font-family: 'DM Mono', monospace; 
    letter-spacing: 1px; text-transform: uppercase; padding-top: 8px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.grid-placeholder { 
    height: 34px; background: #0f1117; border: 1px solid #1e2235; margin-top: 1px; 
}

/* ── Result cards ── */
.metric-card {
    background: #151821; border: 1px solid #1e2235; padding: 14px 16px;
    position: relative; overflow: hidden;
}
.metric-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; }
.metric-card.c-green::before  { background: #00c896; }
.metric-card.c-red::before    { background: #ff4d6d; }
.metric-card.c-amber::before  { background: #f59e0b; }
.metric-card.c-blue::before   { background: #3b82f6; }
.mc-label { font-size: 0.6rem; font-family: 'DM Mono', monospace; letter-spacing: 2px; text-transform: uppercase; color: #4a5568; margin-bottom: 7px; }
.mc-value { font-size: 1.1rem; font-weight: 700; color: #f1f5f9; font-family: 'DM Mono', monospace; letter-spacing: -0.5px; line-height: 1; }
.mc-sub { font-size: 0.65rem; color: #4a5568; margin-top: 5px; font-family: 'DM Mono', monospace; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0f1117 !important; border-bottom: 1px solid #1e2235 !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #4a5568 !important;
    border: none !important; border-bottom: 2px solid transparent !important;
    font-family: 'DM Mono', monospace !important; font-size: 0.72rem !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    padding: 10px 20px !important; margin: 0 !important; transition: all 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #8892a4 !important; }
.stTabs [aria-selected="true"] {
    color: #00c896 !important; border-bottom: 2px solid #00c896 !important; background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 20px 0 0 !important; background: transparent !important; }

/* ── Streamlit widget overrides ── */
div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input {
    background: #0f1117 !important; border: 1px solid #2e3347 !important;
    color: #e2e8f0 !important; border-radius: 0 !important;
    font-family: 'DM Mono', monospace !important; font-size: 0.85rem !important;
}
div[data-testid="stNumberInput"] input:focus { border-color: #00c896 !important; box-shadow: none !important; }
div[data-testid="stSelectbox"] > div > div {
    background: #0f1117 !important; border: 1px solid #2e3347 !important;
    border-radius: 0 !important; color: #e2e8f0 !important; font-family: 'DM Mono', monospace !important;
}
label, div[data-testid="stNumberInput"] label, div[data-testid="stSelectbox"] label {
    color: #8892a4 !important; font-size: 0.72rem !important;
    font-family: 'DM Mono', monospace !important; letter-spacing: 1px !important;
    text-transform: uppercase !important; font-weight: 500 !important;
}

/* ── Custom HTML Tables ── */
.ep-table-container { border: 1px solid #1e2235; overflow-x: auto; }
.ep-table { width: 100%; border-collapse: collapse; font-family: 'DM Mono', monospace; font-size: 0.78rem; }
.ep-table thead th { background: #151821; color: #00c896; text-transform: uppercase; letter-spacing: 1.5px; 
                     font-size: 0.65rem; padding: 10px 12px; border-bottom: 2px solid #2e3347; 
                     text-align: left; font-weight: 500; white-space: nowrap; }
.ep-table tbody td { background: #0f1117; color: #e2e8f0; padding: 8px 12px; border-bottom: 1px solid #1e2235; }
.ep-table tbody tr:hover td { background: #151821; }
.ep-table tbody tr:last-child td { border-bottom: none; }

/* ── Print button ── */
.ep-print-btn {
    background: #151821; border: 1px solid #2e3347; color: #e2e8f0;
    padding: 8px 16px; font-family: 'DM Mono', monospace; font-size: 0.72rem;
    cursor: pointer; text-transform: uppercase; letter-spacing: 1px;
}
.ep-print-btn:hover { border-color: #00c896; color: #00c896; }

/* ── Disclaimer ── */
.ep-disclaimer {
    font-size: 0.7rem; font-family: 'DM Mono', monospace; color: #2e3347;
    background: #0f1117; border: 1px solid #1a1d27; padding: 12px 16px;
    margin-top: 20px; letter-spacing: 0.3px; line-height: 1.6;
}

/* ── Print Styles ── */
@media print {
    .no-print, .ep-section, .stTabs [data-baseweb="tab-list"], 
    div[data-testid="stNumberInput"], div[data-testid="stTextInput"], div[data-testid="stSelectbox"] {
        display: none !important;
    }
    body, .stApp { background: #ffffff !important; color: #000000 !important; }
    .metric-card { 
        background: #f8f9fa !important; border: 1px solid #ddd !important; color: #000 !important; 
        page-break-inside: avoid; margin-bottom: 10px !important;
    }
    .mc-value, .mc-label, .mc-sub, .ep-title, .ep-subtitle { color: #000 !important; }
    .stTabs [data-baseweb="tab-panel"] { 
        display: block !important; margin-bottom: 40px !important; page-break-before: auto; 
    }
    .plotly-graph-div { page-break-inside: avoid; margin-bottom: 20px !important; height: 450px !important; }
    .print-only { display: block !important; font-family: 'Syne', sans-serif; font-size: 1rem; margin-bottom: 10px; color: #000; }
    .ep-table thead th { background: #f8f9fa !important; color: #000 !important; border-bottom: 1px solid #ddd !important; }
    .ep-table tbody td { background: #fff !important; color: #000 !important; border-bottom: 1px solid #eee !important; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ep-header">
 <div class="ep-logo-block">TC</div>
 <div>
  <div class="ep-title">Tilgungschart</div>
  <div class="ep-subtitle">Mortgage Amortization Calculator · Bankvergleich</div>
 </div>
 <div class="ep-badge">Fixed Rate Period Only</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def fmt_eur(v):
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {s}"

def fmt_eur_int(v):
    s = f"{abs(v):,.0f}".replace(",", ".")
    return f"€ {s}"

def amortization_fixed_period(principal, annual_rate, repayment_rate,
                              fixed_years, lump_sum=0, lump_sum_year=0, lump_sum_month=12,
                              annual_extra=0, annual_extra_month=12):
    schedule = []
    balance = principal
    monthly_rate = annual_rate / 100 / 12
    monthly_payment = balance * (monthly_rate + repayment_rate / 100 / 12)
    max_months = fixed_years * 12

    for month in range(1, max_months + 1):
        year = math.ceil(month / 12)
        interest = balance * monthly_rate
        principal_paid = min(monthly_payment - interest, balance)
        if principal_paid < 0: principal_paid = 0
        balance -= principal_paid

        lump_applied = 0.0
        if annual_extra > 0 and (month - 1) % 12 + 1 == annual_extra_month and balance > 0.01:
            lump_applied = min(annual_extra, balance)
            balance -= lump_applied

        lump_once = 0.0
        if lump_sum > 0 and month == (lump_sum_year - 1) * 12 + lump_sum_month and balance > 0.01:
            lump_once = min(lump_sum, balance)
            balance -= lump_once

        balance = max(balance, 0)
        schedule.append({
            "Month": month, "Year": year, "Payment": monthly_payment,
            "Interest": interest,
            "Principal": principal_paid + lump_applied + lump_once,
            "Extra": lump_applied + lump_once, "Balance": balance
        })
        if balance <= 0.01: break
    return pd.DataFrame(schedule)

def make_chart_layout(title_text, height=550):
    return dict(
        paper_bgcolor=DARK_BG, plot_bgcolor=PANEL,
        font=dict(family=MONO, color=MID, size=11),
        margin=dict(l=70, r=30, t=60, b=60),
        title=dict(text=title_text, font=dict(family=MONO, size=12, color=MID),
                   x=0.01, xanchor="left", pad=dict(b=10)),
        legend=dict(
            bgcolor="rgba(21,24,33,0.95)", bordercolor=BORDER2, borderwidth=1,
            font=dict(family=MONO, size=10, color=MID),
            orientation="h", yanchor="top", y=0.98, xanchor="right", x=0.98,
        ),
        hoverlabel=dict(bgcolor="#1a1d27", bordercolor=BORDER2,
                        font=dict(family=MONO, size=11, color=BRT)),
        hovermode="x unified",
        height=height,
    )

def apply_axes(fig, x_title="", y_title="", dtick=None, tickprefix="€"):
    xkw = dict(gridcolor=BORDER, zeroline=False, showline=False,
               tickfont=dict(family=MONO, size=11, color=DIM),
               title=dict(text=x_title, font=dict(family=MONO, size=11, color=MID), standoff=12))
    if dtick: xkw["dtick"] = dtick
    fig.update_xaxes(**xkw)
    fig.update_yaxes(
        gridcolor=BORDER, zeroline=False,
        tickfont=dict(family=MONO, size=11, color=DIM),
        tickprefix=tickprefix, tickformat=",.0f",
        title=dict(text=y_title, font=dict(family=MONO, size=11, color=MID), standoff=12),
    )

def render_styled_table(df, height=480):
    html = df.to_html(index=False, classes='ep-table', border=0, escape=False)
    st.markdown(f'<div class="ep-table-container" style="max-height:{height}px; overflow-y:auto;">{html}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Section 1: Horizontal Input Grid (rows = banks, cols = parameters)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ep-section">01 — Parameter & Bankvergleich</div>', unsafe_allow_html=True)

loan_amount = st.number_input("Darlehensbetrag (€)", min_value=10_000, max_value=5_000_000,
                              value=300_000, step=5_000, key="global_loan")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# --- Header row ---
c = st.columns([0.8, 0.8, 1.2, 1.0, 1.0, 1.0, 1.0, 0.7, 0.7, 1.0, 0.7])
headers = ["Bank", "Aktiv.", "Name", "Zinsbind.", "Sollzins", "Tilgung", "Einmalz.", "Jahr", "Monat", "Sondertilg.", "Monat"]
for i, h in enumerate(headers):
    c[i].markdown(f'<div class="grid-header">{h}</div>', unsafe_allow_html=True)

# --- Data rows ---
enabled = [False, False, False]
names = ["Bank 1", "Bank 2", "Bank 3"]
fixed_years_list = [10, 10, 10]
rates = [3.5, 3.5, 3.5]
reps = [2.0, 2.0, 2.0]
lumps = [0, 0, 0]
lump_years = [5, 5, 5]
lump_months = [12, 12, 12]
extras = [0, 0, 0]
extra_months = [12, 12, 12]

for i in range(3):
    c = st.columns([0.8, 0.8, 1.2, 1.0, 1.0, 1.0, 1.0, 0.7, 0.7, 1.0, 0.7])
    c[0].markdown(f'<div class="grid-row-label">🏦 Bank {i+1}</div>', unsafe_allow_html=True)
    with c[1]:
        enabled[i] = st.checkbox("Aktivieren", value=(i==0), key=f"comp_{i}", label_visibility="collapsed")
    if enabled[i]:
        with c[2]: names[i] = st.text_input("Name", value=f"Bank {i+1}", key=f"bname_{i}", label_visibility="collapsed")
        with c[3]: fixed_years_list[i] = st.selectbox("Zinsbindung", options=[5,10,15,20,25,30], index=1, key=f"bfix_{i}", label_visibility="collapsed")
        with c[4]: rates[i] = st.number_input("Sollzins", min_value=0.1, max_value=15.0, value=3.5, step=0.05, format="%.2f", key=f"brate_{i}", label_visibility="collapsed")
        with c[5]: reps[i] = st.number_input("Tilgung", min_value=0.5, max_value=20.0, value=2.0, step=0.1, format="%.2f", key=f"brep_{i}", label_visibility="collapsed")
        with c[6]: lumps[i] = st.number_input("Einmalz", min_value=0, max_value=int(loan_amount), value=0, step=1000, key=f"blump_{i}", label_visibility="collapsed")
        with c[7]: lump_years[i] = st.number_input("Jahr", min_value=1, max_value=int(fixed_years_list[i]), value=min(5, int(fixed_years_list[i])), step=1, key=f"blump_yr_{i}", label_visibility="collapsed")
        with c[8]: lump_months[i] = st.number_input("Monat", min_value=1, max_value=12, value=12, step=1, key=f"blump_mo_{i}", label_visibility="collapsed")
        with c[9]: extras[i] = st.number_input("Sondertilg", min_value=0, max_value=int(loan_amount), value=0, step=500, key=f"bextra_{i}", label_visibility="collapsed")
        with c[10]: extra_months[i] = st.number_input("Monat ST", min_value=1, max_value=12, value=12, step=1, key=f"bextra_mo_{i}", label_visibility="collapsed")
    else:
        for j in range(2, 11):
            c[j].markdown('<div class="grid-placeholder"></div>', unsafe_allow_html=True)

# Build bank_configs
bank_configs = []
for i in range(3):
    if enabled[i]:
        bank_configs.append({
            "enabled": True, "name": names[i], "fixed_years": fixed_years_list[i],
            "annual_rate": rates[i], "repayment_rate": reps[i],
            "lump_sum": lumps[i], "lump_year": lump_years[i], "lump_month": lump_months[i],
            "annual_extra": extras[i], "annual_extra_month": extra_months[i]
        })
    else:
        bank_configs.append({"enabled": False})

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Calculate per bank
# ─────────────────────────────────────────────────────────────────────────────
results_by_idx = {}
for i, cfg in enumerate(bank_configs):
    if cfg["enabled"]:
        df = amortization_fixed_period(
            loan_amount, cfg["annual_rate"], cfg["repayment_rate"],
            cfg["fixed_years"], cfg["lump_sum"], cfg["lump_year"], cfg["lump_month"],
            cfg["annual_extra"], cfg["annual_extra_month"]
        )
        monthly_payment = loan_amount * (cfg["annual_rate"]/100/12 + cfg["repayment_rate"]/100/12)
        total_interest_fp = df["Interest"].sum()
        total_principal_fp = df["Principal"].sum()
        balance_end = df["Balance"].iloc[-1]
        actual_months = df["Month"].max()
        annual = (df.groupby("Year")
                  .agg(Interest=("Interest", "sum"), Principal=("Principal", "sum"),
                       Balance=("Balance", "last"), Total=("Payment", "sum"))
                  .reset_index())
        results_by_idx[i] = {
            "name": cfg["name"], "df": df, "monthly_payment": monthly_payment,
            "total_interest": total_interest_fp, "total_principal": total_principal_fp,
            "balance_end": balance_end, "actual_months": actual_months, "annual": annual,
            "fixed_years": cfg["fixed_years"]
        }

# ─────────────────────────────────────────────────────────────────────────────
# Section 2: Horizontal Results Grid (rows = banks, cols = metrics)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="ep-section">02 — Ergebnisse</div>', unsafe_allow_html=True)

# Header
c = st.columns([1, 1.5, 1.5, 1.5, 1.5])
res_headers = ["Bank", "Monatliche Rate", "Zinskosten", "Restschuld", "Getilgter Betrag"]
for i, h in enumerate(res_headers):
    c[i].markdown(f'<div class="grid-header">{h}</div>', unsafe_allow_html=True)

for i in range(3):
    c = st.columns([1, 1.5, 1.5, 1.5, 1.5])
    if i in results_by_idx:
        r = results_by_idx[i]
        c[0].markdown(f'<div class="grid-row-label">{r["name"]}</div>', unsafe_allow_html=True)
        with c[1]: st.markdown(f'<div class="metric-card c-green" style="margin-bottom:0;"><div class="mc-label">Monatliche Rate</div><div class="mc-value">{fmt_eur(r["monthly_payment"])}</div><div class="mc-sub">fest für {r["fixed_years"]} Jahre</div></div>', unsafe_allow_html=True)
        with c[2]: st.markdown(f'<div class="metric-card c-red" style="margin-bottom:0;"><div class="mc-label">Zinskosten</div><div class="mc-value">{fmt_eur(r["total_interest"])}</div><div class="mc-sub">Zinsen während Zinsbindung</div></div>', unsafe_allow_html=True)
        with c[3]: st.markdown(f'<div class="metric-card c-amber" style="margin-bottom:0;"><div class="mc-label">Restschuld</div><div class="mc-value">{fmt_eur(r["balance_end"])}</div><div class="mc-sub">nach {r["actual_months"]} Monaten</div></div>', unsafe_allow_html=True)
        with c[4]: st.markdown(f'<div class="metric-card c-blue" style="margin-bottom:0;"><div class="mc-label">Getilgter Betrag</div><div class="mc-value">{fmt_eur(r["total_principal"])}</div><div class="mc-sub">Tilgung während Zinsbindung</div></div>', unsafe_allow_html=True)
    else:
        c[0].markdown(f'<div class="grid-row-label" style="color:#4a5568;">🏦 Bank {i+1}</div>', unsafe_allow_html=True)
        for j in range(1, 5):
            c[j].markdown('<div class="grid-placeholder" style="height:72px;"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PDF Print Button (raw HTML to avoid Streamlit rerun)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="no-print" style="text-align: right; margin: 16px 0;">
    <button class="ep-print-btn" onclick="window.print()">🖨️ PDF-Report drucken / speichern</button>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Section 3: Tabs (Comparison Charts & Tables)
# ─────────────────────────────────────────────────────────────────────────────
if results_by_idx:
    st.markdown('<div class="ep-section">03 — Tilgungsdiagramm & Übersichten</div>', unsafe_allow_html=True)
    tab_tg, tab_rs, tab_yr, tab_mo = st.tabs([
        "📈 Tilgungsdiagramm",
        "📉 Restschuld-Verlauf",
        "📅 Jahresübersicht",
        "🗓️ Monatstabelle",
    ])

    def bank_header(name):
        st.markdown(f'<div class="print-only" style="margin: 24px 0 8px; font-weight: 600;">{name}</div>', unsafe_allow_html=True)

    # Tab 1: Tilgungsdiagramm — base principal line + annotation bubbles for extras
    with tab_tg:
        fig1 = go.Figure()
        for idx, i in enumerate(sorted(results_by_idx.keys())):
            r = results_by_idx[i]
            col = BANK_COLORS[idx]
            base_principal = r["df"]["Principal"] - r["df"]["Extra"]

            fig1.add_trace(go.Scatter(
                name=f"{r['name']} — Zinsen",
                x=r["df"]["Month"], y=r["df"]["Interest"],
                mode="lines", line=dict(color=col["interest"], width=2),
                hovertemplate=f"{r['name']} — Zinsen<br>Monat %{{x}}<<br>€%{{y:,.2f}}<<extra></extra>"
            ))
            fig1.add_trace(go.Scatter(
                name=f"{r['name']} — Tilgung",
                x=r["df"]["Month"], y=base_principal,
                mode="lines", line=dict(color=col["principal"], width=2),
                hovertemplate=f"{r['name']} — Tilgung<br>Monat %{{x}}<<br>€%{{y:,.2f}}<<extra></extra>"
            ))
            # Annotation bubbles for Sondertilgung (without adding to line)
            extra_df = r["df"][r["df"]["Extra"] > 0]
            if not extra_df.empty:
                fig1.add_trace(go.Scatter(
                    x=extra_df["Month"],
                    y=base_principal.iloc[extra_df.index],
                    mode="markers+text",
                    text=[f"+{fmt_eur_int(v)}" for v in extra_df["Extra"]],
                    textposition="top center",
                    marker=dict(size=8, color=col["marker"], symbol="diamond",
                                line=dict(width=1, color=BRT)),
                    textfont=dict(family=MONO, size=9, color=col["marker"]),
                    hovertemplate=f"{r['name']} — Sondertilgung<br>Monat %{{x}}<<br>%{{text}}<<extra></extra>",
                    showlegend=False,
                ))
        fig1.update_layout(**make_chart_layout("Monatliche Zinsen & Tilgung — Zinsbindungsperiode"))
        apply_axes(fig1, x_title="Monat", y_title="Betrag (€)")
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    # Tab 2: Restschuld-Verlauf
    with tab_rs:
        fig2 = go.Figure()
        for idx, i in enumerate(sorted(results_by_idx.keys())):
            r = results_by_idx[i]
            col = BANK_COLORS[idx]
            fig2.add_trace(go.Scatter(
                name=f"{r['name']} — Restschuld",
                x=r["df"]["Month"], y=r["df"]["Balance"],
                mode="lines", line=dict(color=col["balance"], width=2.5),
                hovertemplate=f"{r['name']} — Restschuld<br>Monat %{{x}}<<br>€%{{y:,.2f}}<<extra></extra>"
            ))
            fig2.add_trace(go.Scatter(
                name=f"{r['name']} — Kum. Tilgung",
                x=r["df"]["Month"], y=r["df"]["Principal"].cumsum(),
                mode="lines", line=dict(color=col["cum_prin"], width=1.8, dash="dash"),
                hovertemplate=f"{r['name']} — Kum. Tilgung<br>Monat %{{x}}<<br>€%{{y:,.2f}}<<extra></extra>"
            ))
            fig2.add_trace(go.Scatter(
                name=f"{r['name']} — Kum. Zinsen",
                x=r["df"]["Month"], y=r["df"]["Interest"].cumsum(),
                mode="lines", line=dict(color=col["cum_int"], width=1.8, dash="dot"),
                hovertemplate=f"{r['name']} — Kum. Zinsen<br>Monat %{{x}}<<br>€%{{y:,.2f}}<<extra></extra>"
            ))
        fig2.update_layout(**make_chart_layout("Restschuld-Verlauf — monatlich"))
        apply_axes(fig2, x_title="Monat", y_title="Betrag (€)")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # Tab 3: Jahresübersicht
    with tab_yr:
        for i in sorted(results_by_idx.keys()):
            r = results_by_idx[i]
            bank_header(r["name"])
            yr = r["annual"].copy()
            zinsanteil = (yr["Interest"] / (yr["Interest"] + yr["Principal"]) * 100)
            zinsanteil = zinsanteil.fillna(0).map("{:.1f}%".format)
            yr_display = pd.DataFrame({
                "Jahr": [f"Jahr {y:02d}" for y in yr["Year"]],
                "Jahresrate": yr["Total"].apply(fmt_eur),
                "Zinsen": yr["Interest"].apply(fmt_eur),
                "Tilgung": yr["Principal"].apply(fmt_eur),
                "Restschuld": yr["Balance"].apply(fmt_eur),
                "Zinsanteil": zinsanteil
            })
            render_styled_table(yr_display, height=min(400, 56 + len(yr_display)*36))

    # Tab 4: Monatstabelle
    with tab_mo:
        for i in sorted(results_by_idx.keys()):
            r = results_by_idx[i]
            bank_header(r["name"])
            mo_display = pd.DataFrame({
                "Monat": r["df"]["Month"].astype(int),
                "Jahr": r["df"]["Year"].astype(int),
                "Rate": r["df"]["Payment"].apply(fmt_eur),
                "Zinsen": r["df"]["Interest"].apply(fmt_eur),
                "Tilgung": r["df"]["Principal"].apply(fmt_eur),
                "Restschuld": r["df"]["Balance"].apply(fmt_eur),
            })
            render_styled_table(mo_display, height=480)

# ─────────────────────────────────────────────────────────────────────────────
# Disclaimer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ep-disclaimer">
⚠ Bei den Berechnungen handelt es sich um eine unverbindliche Indikation.
Die Ergebnisse stellen keinen Finanzierungsvorschlag dar.
Die zukünftige Zinsentwicklung kann nicht aus der Vergangenheit abgeleitet werden.
</div>
""", unsafe_allow_html=True)
