import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG — must be first
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TFSA Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  — Bloomberg-meets-cyberpunk trading terminal
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;600&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #050810 !important;
    color: #e2e8f0 !important;
    font-family: 'Syne', sans-serif;
}
[data-testid="stSidebar"] {
    background: #080c18 !important;
    border-right: 1px solid #1a2035 !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] .stRadio label { color: #cbd5e1 !important; font-family: 'Space Mono', monospace; font-size: 12px; }

/* ── Animated grid background ── */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(56,189,248,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56,189,248,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding: 1.5rem 2rem 2rem !important; position: relative; z-index: 1; }

/* ── Metric containers ── */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1424 0%, #111827 100%) !important;
    border: 1px solid #1e293b !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    position: relative; overflow: hidden;
    transition: border-color 0.2s ease;
}
div[data-testid="metric-container"]::before {
    content: ''; position: absolute; top: 0; left: 0;
    right: 0; height: 2px;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #38bdf8);
}
div[data-testid="metric-container"]:hover { border-color: #38bdf8 !important; }
div[data-testid="metric-container"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important; letter-spacing: .12em !important;
    color: #475569 !important; text-transform: uppercase;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 22px !important; font-weight: 700 !important;
    color: #e2e8f0 !important;
}

/* ── Selectbox & inputs ── */
.stSelectbox > div > div {
    background: #0d1424 !important; border: 1px solid #1e293b !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput input, .stNumberInput input {
    background: #0d1424 !important; border: 1px solid #1e293b !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important; font-family: 'Space Mono', monospace !important;
    font-size: 12px !important; font-weight: 700 !important;
    letter-spacing: .06em !important; padding: 8px 20px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(14,165,233,0.35) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #080c18 !important; border-radius: 10px !important;
    padding: 4px !important; border: 1px solid #1e293b !important; gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #475569 !important;
    border-radius: 8px !important; padding: 8px 18px !important;
    font-family: 'Space Mono', monospace !important; font-size: 11px !important;
    font-weight: 700 !important; letter-spacing: .05em;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#0ea5e9,#6366f1) !important;
    color: #fff !important;
}

/* ── Dataframe ── */
.stDataFrame { border-radius: 12px !important; overflow: hidden; }
.stDataFrame iframe { border-radius: 12px !important; }

/* ── Spinner ── */
.stSpinner > div { border-color: #38bdf8 transparent transparent !important; }

/* ── Multiselect ── */
.stMultiSelect > div > div {
    background: #0d1424 !important; border: 1px solid #1e293b !important;
    border-radius: 8px !important;
}

/* ── Radio buttons ── */
.stRadio [data-testid="stMarkdownContainer"] p {
    font-family: 'Space Mono', monospace !important; font-size: 11px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #080c18; }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #38bdf8; }

/* ── Custom components ── */
.terminal-header {
    font-family: 'Syne', sans-serif;
    font-size: 28px; font-weight: 800;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #f472b6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -.02em; margin-bottom: 4px;
}
.terminal-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; color: #334155; letter-spacing: .08em;
    text-transform: uppercase; margin-bottom: 1.5rem;
}
.glass-card {
    background: linear-gradient(135deg, rgba(13,20,36,0.9), rgba(17,24,39,0.9));
    border: 1px solid #1e293b; border-radius: 14px;
    padding: 18px 22px; margin-bottom: 12px;
    backdrop-filter: blur(12px); position: relative; overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
}
.glass-card:hover { border-color: #334155; transform: translateY(-1px); }
.glass-card::after {
    content: ''; position: absolute; inset: 0; border-radius: 14px;
    background: radial-gradient(600px circle at var(--mouse-x,50%) var(--mouse-y,50%),
        rgba(56,189,248,0.04), transparent 40%);
    pointer-events: none;
}
.sig-pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 12px; border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 600; letter-spacing: .08em;
    white-space: nowrap;
}
.pill-STRONG-BUY  { background:rgba(0,230,118,.12); color:#00e676; border:1px solid rgba(0,230,118,.3); }
.pill-BUY         { background:rgba(105,240,174,.1); color:#69f0ae; border:1px solid rgba(105,240,174,.3); }
.pill-HOLD        { background:rgba(255,215,64,.1);  color:#ffd740; border:1px solid rgba(255,215,64,.3); }
.pill-SELL        { background:rgba(255,82,82,.12);  color:#ff5252; border:1px solid rgba(255,82,82,.3); }
.pill-STRONG-SELL { background:rgba(213,0,0,.15);    color:#ff1744; border:1px solid rgba(213,0,0,.3); }
.pill-Neutral     { background:rgba(148,163,184,.1); color:#94a3b8; border:1px solid rgba(148,163,184,.3); }
.pill-Positive-Trend { background:rgba(0,230,118,.12); color:#00e676; border:1px solid rgba(0,230,118,.3); }
.pill-Weak-Trend  { background:rgba(255,82,82,.12);  color:#ff5252; border:1px solid rgba(255,82,82,.3); }
.pill-No-Signal   { background:rgba(148,163,184,.1); color:#94a3b8; border:1px solid rgba(148,163,184,.3); }

.risk-HIGH   { color:#ff5252; font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700; }
.risk-MEDIUM { color:#ffd740; font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700; }
.risk-LOW    { color:#00e676; font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700; }
.risk-Unknown{ color:#94a3b8; font-family:'JetBrains Mono',monospace; font-size:11px; }

.stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; letter-spacing: .1em; text-transform: uppercase; color: #334155;
    margin-bottom: 3px;
}
.stat-value {
    font-family: 'Space Mono', monospace;
    font-size: 18px; font-weight: 700; color: #e2e8f0;
}
.stat-value.pos { color: #00e676; }
.stat-value.neg { color: #ff5252; }

.ticker-label {
    font-family: 'Space Mono', monospace;
    font-size: 13px; font-weight: 700; letter-spacing: .04em;
}
.mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; }

.section-title {
    font-family: 'Syne', sans-serif; font-size: 16px; font-weight: 700;
    color: #e2e8f0; letter-spacing: -.01em;
    border-left: 3px solid #38bdf8; padding-left: 10px;
    margin: 1.5rem 0 1rem;
}
.divider {
    border: none; border-top: 1px solid #1e293b; margin: 1.2rem 0;
}
.news-card {
    background: #0d1424; border: 1px solid #1e293b; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 8px;
    border-left: 3px solid #38bdf8;
    transition: border-color 0.2s, transform 0.15s;
}
.news-card:hover { border-color: #818cf8; transform: translateX(3px); }
.news-title {
    font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 600;
    color: #cbd5e1; line-height: 1.4; margin-bottom: 4px;
}
.news-date { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #334155; }
.tool-header {
    font-family: 'Syne', sans-serif; font-size: 20px; font-weight: 800;
    color: #e2e8f0; margin-bottom: 4px;
}
.tool-sub { font-family:'JetBrains Mono',monospace; font-size:11px; color:#475569; margin-bottom:1.2rem; }
.sparkline-pos { color: #00e676; font-size: 18px; }
.sparkline-neg { color: #ff5252; font-size: 18px; }
.portfolio-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 16px; border-radius: 10px; margin-bottom: 6px;
    background: #0d1424; border: 1px solid #1e293b;
    transition: background 0.15s, border-color 0.15s;
}
.portfolio-row:hover { background: #111827; border-color: #334155; }
.no-data { font-family:'JetBrains Mono',monospace; font-size:12px; color:#334155;
           text-align:center; padding: 2rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PORTFOLIO DATA
# ─────────────────────────────────────────────────────────────────────────────
PORTFOLIO = {
    "AAPL.TO": {"shares": 29.99,    "ac": 32.86},
    "ABCL":    {"shares": 159.9965, "ac": 4.2607},
    "AEHR":    {"shares": 15,       "ac": 20.56},
    "AMZN.TO": {"shares": 79.99,    "ac": 17.19},
    "APLD":    {"shares": 25,       "ac": 24.72},
    "APPS.NE": {"shares": 39.842,   "ac": 17.68},
    "ASML.TO": {"shares": 45,       "ac": 26.20},
    "BAM.TO":  {"shares": 10.08,    "ac": 72.44},
    "BBAI":    {"shares": 60,       "ac": 7.655},
    "BEP-UN.TO":{"shares":30.3548,  "ac": 39.07},
    "BRK.TO":  {"shares": 20,       "ac": 33.38},
    "CEGS.TO": {"shares": 43.05,    "ac": 22.01},
    "CGL.TO":  {"shares": 15,       "ac": 22.19},
    "CLBT":    {"shares": 40,       "ac": 18.65},
    "CMPS":    {"shares": 80,       "ac": 5.00},
    "COPP.TO": {"shares": 17,       "ac": 51.35},
    "CRCL":    {"shares": 14,       "ac": 95.28},
    "CRWV":    {"shares": 12.9979,  "ac": 109.50},
    "CU.TO":   {"shares": 30.26,    "ac": 37.39},
    "DRUG.CN": {"shares": 8,        "ac": 73.92},
    "ENB.TO":  {"shares": 20,       "ac": 62.53},
    "EOSE":    {"shares": 60,       "ac": 12.09},
    "HELP":    {"shares": 80,       "ac": 8.47},
    "IMVT":    {"shares": 10,       "ac": 26.47},
    "ISRG.NE": {"shares": 25,       "ac": 26.86},
    "JOBY":    {"shares": 45,       "ac": 12.14},
    "LMT.TO":  {"shares": 30.14,    "ac": 31.03},
    "LUNR":    {"shares": 45,       "ac": 11.08},
    "MDA.TO":  {"shares": 50,       "ac": 30.38},
    "META.TO": {"shares": 30,       "ac": 34.75},
    "MSFT.TO": {"shares": 60.11,    "ac": 27.40},
    "NNE":     {"shares": 10,       "ac": 42.58},
    "NU":      {"shares": 40,       "ac": 14.98},
    "NVDA.TO": {"shares": 80,       "ac": 22.96},
    "NVTS":    {"shares": 60,       "ac": 7.21},
    "NXT":     {"shares": 8,        "ac": 72.18},
    "OKLO":    {"shares": 9,        "ac": 121.28},
    "ONE.V":   {"shares": 400,      "ac": 0.8275},
    "PHOS.CN": {"shares": 500,      "ac": 0.5943},
    "PNG.V":   {"shares": 200,      "ac": 5.41},
    "QBTS":    {"shares": 25,       "ac": 25.34},
    "RARE":    {"shares": 20,       "ac": 29.56},
    "RDDT":    {"shares": 7,        "ac": 114.74},
    "RDW":     {"shares": 40,       "ac": 10.25},
    "RGTI":    {"shares": 20,       "ac": 31.16},
    "RXRX":    {"shares": 200,      "ac": 4.61},
    "SCD.V":   {"shares": 2500,     "ac": 0.2285},
    "SOUN":    {"shares": 50,       "ac": 9.50},
    "TEM":     {"shares": 10,       "ac": 63.64},
    "TMC":     {"shares": 100,      "ac": 5.27},
    "TOI.V":   {"shares": 5,        "ac": 115.85},
    "TSLA.TO": {"shares": 31.1267,  "ac": 35.72},
    "VEE.TO":  {"shares": 32,       "ac": 41.06},
    "VFV.TO":  {"shares": 32.8581,  "ac": 128.76},
    "VNM":     {"shares": 40,       "ac": 17.67},
    "WELL.TO": {"shares": 180,      "ac": 4.05},
    "WPM.TO":  {"shares": 6,        "ac": 146.66},
    "XEF.TO":  {"shares": 29.43,    "ac": 41.71},
    "XID.TO":  {"shares": 13.7926,  "ac": 49.38},
    "XSU.TO":  {"shares": 12.18,    "ac": 46.39},
    "ZCN.TO":  {"shares": 25.13,    "ac": 34.91},
    "ZJPN.TO": {"shares": 13.21,    "ac": 45.04},
}

# ─────────────────────────────────────────────────────────────────────────────
# DATA & INDICATORS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_price_data(ticker):
    try:
        return yf.Ticker(ticker).history(period="6mo")
    except:
        return None

def get_last_price(df):
    if df is None or df.empty:
        return None
    return float(df["Close"].iloc[-1])

def rsi(series, period=14):
    delta = series.diff()
    gain  = delta.where(delta > 0, 0).rolling(period).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def compute_indicators(df):
    df = df.copy()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    df["RSI"]  = rsi(df["Close"])
    return df

def signal_logic(price, ma20, ma50, rsi_val):
    if any(pd.isna(v) for v in [ma20, ma50, rsi_val]):
        return "No Signal"
    if ma20 > ma50 and rsi_val < 30:
        return "STRONG BUY"
    elif ma20 > ma50 and rsi_val < 50:
        return "BUY"
    elif ma20 > ma50 and rsi_val < 70:
        return "Positive Trend"
    elif ma20 < ma50 and rsi_val > 70:
        return "STRONG SELL"
    elif ma20 < ma50 and rsi_val > 60:
        return "Weak Trend"
    elif ma20 < ma50:
        return "SELL"
    return "Neutral"

def risk_score(row):
    if pd.isna(row.get("Volatility %")):
        return "Unknown"
    if row["Cost"] > 3000 and row["Volatility %"] > 3:
        return "High"
    elif row["Volatility %"] > 2:
        return "Medium"
    return "Low"

@st.cache_data(ttl=300)
def build_df():
    rows = []
    for t, v in PORTFOLIO.items():
        df_raw = get_price_data(t)
        price  = get_last_price(df_raw)
        shares, ac = v["shares"], v["ac"]
        cost   = shares * ac
        market = pnl = ret_pct = ma20 = ma50 = rsi_val = signal = vol = None

        if price:
            market  = shares * price
            pnl     = market - cost
            ret_pct = pnl / cost * 100

        if df_raw is not None and not df_raw.empty:
            df_ind  = compute_indicators(df_raw)
            last    = df_ind.iloc[-1]
            ma20, ma50, rsi_val = last["MA20"], last["MA50"], last["RSI"]
            signal  = signal_logic(price, ma20, ma50, rsi_val)
            vol     = df_ind["Close"].pct_change().std() * 100

        rows.append({
            "Ticker": t, "Shares": shares, "AC": ac, "Cost": cost,
            "Price": price, "Market Value": market,
            "PnL": pnl, "Return %": ret_pct,
            "RSI": round(rsi_val, 1) if rsi_val and not np.isnan(rsi_val) else None,
            "MA20": round(ma20, 2) if ma20 and not np.isnan(ma20) else None,
            "MA50": round(ma50, 2) if ma50 and not np.isnan(ma50) else None,
            "Signal": signal or "No Signal",
            "Volatility %": round(vol, 2) if vol else None,
        })

    df_out = pd.DataFrame(rows)
    df_out["Risk"] = df_out.apply(risk_score, axis=1)
    return df_out

@st.cache_data(ttl=600)
def fetch_news(ticker):
    try:
        items = []
        for n in (yf.Ticker(ticker).news or [])[:5]:
            ct    = n.get("content", {})
            title = ct.get("title") or n.get("title", "")
            link  = ct.get("canonicalUrl", {}).get("url") or n.get("link", "")
            pub   = ct.get("pubDate") or ""
            if pub:
                try: pub = datetime.fromisoformat(pub.replace("Z","")).strftime("%b %d, %Y")
                except: pass
            if title:
                items.append({"title": title, "link": link, "date": pub})
        return items
    except:
        return []

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
SIG_COLOR = {
    "STRONG BUY":  "#00e676",
    "BUY":         "#69f0ae",
    "Positive Trend":"#69f0ae",
    "HOLD":        "#ffd740",
    "Neutral":     "#94a3b8",
    "No Signal":   "#475569",
    "Weak Trend":  "#ff5252",
    "SELL":        "#ff5252",
    "STRONG SELL": "#ff1744",
}

def sig_pill(sig):
    css = (sig or "No Signal").replace(" ", "-")
    dot_c = SIG_COLOR.get(sig or "No Signal", "#94a3b8")
    return (f'<span class="sig-pill pill-{css}">'
            f'<span style="width:5px;height:5px;border-radius:50%;'
            f'background:{dot_c};display:inline-block"></span>{sig}</span>')

def color_val(val, fmt="$.0f"):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return '<span style="color:#334155">—</span>'
    c = "#00e676" if val >= 0 else "#ff5252"
    if fmt == "$.0f":   txt = f"${abs(val):,.0f}"
    elif fmt == "+.1f": txt = f"{val:+.1f}%"
    elif fmt == "$.2f": txt = f"${val:.2f}"
    else:               txt = str(val)
    sign = "+" if val > 0 else ("-" if val < 0 else "")
    if fmt == "$.0f" and val < 0: txt = f"-${abs(val):,.0f}"
    return f'<span style="color:{c};font-family:\'Space Mono\',monospace;font-weight:700">{txt}</span>'

def mono(val, fmt=""):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return '<span style="color:#334155">—</span>'
    if fmt == "$.2f": txt = f"${val:,.2f}"
    elif fmt == ".1f": txt = f"{val:.1f}"
    elif fmt == "$.0f": txt = f"${val:,.0f}"
    else: txt = str(val)
    return f'<span class="mono" style="color:#94a3b8">{txt}</span>'

def risk_badge(r):
    c = {"High":"#ff5252","Medium":"#ffd740","Low":"#00e676"}.get(r,"#475569")
    return f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;font-weight:700;color:{c}">{r}</span>'

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 0 16px">
      <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;
           background:linear-gradient(135deg,#38bdf8,#818cf8);
           -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        TFSA TERMINAL
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
           color:#334155;letter-spacing:.1em;text-transform:uppercase;margin-top:2px">
        v3.0 · LIVE DATA
      </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "📊  Overview",
        "🔍  Ticker Dive",
        "📰  News Feed",
        "📉  Signals",
        "🛠️  Tools",
    ], label_visibility="collapsed")

    st.markdown('<hr style="border:none;border-top:1px solid #1e293b;margin:16px 0">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#1e293b;
         text-align:center;padding-top:4px">
      {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>""", unsafe_allow_html=True)

    if "📊" in page or "📉" in page or "🛠️" in page:
        if st.button("⟳  Refresh data"):
            st.cache_data.clear()
            st.rerun()

    if "🔍" in page or "📰" in page:
        selected_tk = st.selectbox("Ticker", sorted(PORTFOLIO.keys()),
                                   label_visibility="collapsed")

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA (cached)
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("Syncing market data…"):
    df = build_df()

df_valid = df[df["Market Value"].notna()].copy()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if "📊" in page:
    # Header
    st.markdown("""
    <div class="terminal-header">PORTFOLIO OVERVIEW</div>
    <div class="terminal-sub">TFSA · LIVE MARKET DATA · AUTO-REFRESH 5 MIN</div>
    """, unsafe_allow_html=True)

    # KPI strip
    tv   = df_valid["Market Value"].sum()
    tc   = df_valid["Cost"].sum()
    tpnl = df_valid["PnL"].sum()
    tret = tpnl / tc * 100 if tc else 0
    winners = (df_valid["PnL"] > 0).sum()
    losers  = (df_valid["PnL"] < 0).sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("PORTFOLIO VALUE",  f"${tv:,.0f}")
    k2.metric("COST BASIS",       f"${tc:,.0f}")
    pnl_delta = f"{tret:+.2f}%"
    k3.metric("TOTAL P&L",  f"${tpnl:+,.0f}", delta=pnl_delta)
    k4.metric("WINNERS / LOSERS", f"{winners} / {losers}")
    k5.metric("POSITIONS",        str(len(df_valid)))

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Signal distribution bar
    sig_counts = df_valid["Signal"].value_counts()
    sig_order  = ["STRONG BUY","BUY","Positive Trend","Neutral","No Signal","Weak Trend","SELL","STRONG SELL"]
    total_sigs = len(df_valid)

    sig_html = '<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:1.5rem">'
    for s in sig_order:
        cnt = sig_counts.get(s, 0)
        if cnt == 0: continue
        c   = SIG_COLOR.get(s, "#475569")
        sig_html += (
            f'<div style="background:rgba(13,20,36,.9);border:1px solid {c}33;'
            f'border-radius:8px;padding:8px 14px;min-width:80px;text-align:center">'
            f'<div style="font-family:\'Space Mono\',monospace;font-size:20px;'
            f'font-weight:700;color:{c}">{cnt}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
            f'color:{c}99;letter-spacing:.08em;text-transform:uppercase">{s}</div></div>'
        )
    sig_html += '</div>'
    st.markdown(sig_html, unsafe_allow_html=True)

    # ── Top movers ──
    col_w, col_l = st.columns(2)
    with col_w:
        st.markdown('<div class="section-title">🏆 Top Winners</div>', unsafe_allow_html=True)
        top5 = df_valid.nlargest(5, "Return %")
        for _, r in top5.iterrows():
            sig = r.get("Signal","No Signal")
            sc  = SIG_COLOR.get(sig,"#475569")
            st.markdown(
                f'<div class="portfolio-row">'
                f'<span class="ticker-label" style="color:{sc}">{r["Ticker"]}</span>'
                f'{color_val(r["Return %"],"+.1f")}'
                f'{sig_pill(sig)}'
                f'<span class="mono" style="color:#334155">${r["Market Value"]:,.0f}</span>'
                f'</div>', unsafe_allow_html=True)

    with col_l:
        st.markdown('<div class="section-title">⚠️ Top Losers</div>', unsafe_allow_html=True)
        bot5 = df_valid.nsmallest(5, "Return %")
        for _, r in bot5.iterrows():
            sig = r.get("Signal","No Signal")
            st.markdown(
                f'<div class="portfolio-row">'
                f'<span class="ticker-label" style="color:#ff5252">{r["Ticker"]}</span>'
                f'{color_val(r["Return %"],"+.1f")}'
                f'{sig_pill(sig)}'
                f'<span class="mono" style="color:#334155">${r["Market Value"]:,.0f}</span>'
                f'</div>', unsafe_allow_html=True)

    # ── Full table ──
    st.markdown('<div class="section-title">📋 Full Portfolio</div>', unsafe_allow_html=True)

    # Build styled HTML table
    disp = df_valid.sort_values("Market Value", ascending=False)
    rows_html = ""
    for _, r in disp.iterrows():
        sig  = r.get("Signal","No Signal")
        sc   = SIG_COLOR.get(sig,"#475569")
        risk = r.get("Risk","Unknown")
        rc   = {"High":"#ff5252","Medium":"#ffd740","Low":"#00e676"}.get(risk,"#475569")
        rsi_c= ""
        rsi_v= r.get("RSI")
        if rsi_v:
            if rsi_v < 30:   rsi_c = "color:#00e676"
            elif rsi_v > 70: rsi_c = "color:#ff5252"
            else:             rsi_c = "color:#94a3b8"

        ret_v = r.get("Return %")
        ret_c = "#00e676" if ret_v and ret_v >= 0 else "#ff5252"
        pnl_v = r.get("PnL")
        pnl_c = "#00e676" if pnl_v and pnl_v >= 0 else "#ff5252"

        rows_html += f"""
        <tr>
          <td><span class="ticker-label" style="color:{sc}">{r['Ticker']}</span></td>
          <td class="mono" style="color:#475569">{r['Shares']:.2f}</td>
          <td class="mono" style="color:#475569">${r['AC']:.2f}</td>
          <td class="mono">${r['Price']:.2f}</td>
          <td class="mono">${r['Market Value']:,.0f}</td>
          <td class="mono" style="color:{ret_c};font-weight:700">{ret_v:+.1f}%</td>
          <td class="mono" style="color:{pnl_c}">${pnl_v:+,.0f}</td>
          <td>{sig_pill(sig)}</td>
          <td class="mono" style="{rsi_c}">{rsi_v if rsi_v else '—'}</td>
          <td><span style="color:{rc};font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700">{risk}</span></td>
        </tr>"""

    table_html = f"""
    <div style="overflow-x:auto;border-radius:12px;border:1px solid #1e293b">
    <table style="width:100%;border-collapse:collapse;font-size:12px">
      <thead>
        <tr style="border-bottom:1px solid #1e293b">
          {''.join(f'<th style="padding:10px 12px;text-align:left;font-family:JetBrains Mono,monospace;font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:#334155;background:#080c18;white-space:nowrap">{h}</th>'
                   for h in ["Ticker","Shares","Avg Cost","Price","Mkt Value","Return %","P&L $","Signal","RSI","Risk"])}
        </tr>
      </thead>
      <tbody style="background:#0d1424">{rows_html}</tbody>
    </table>
    </div>"""
    st.markdown(table_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — TICKER DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
elif "🔍" in page:
    ticker = selected_tk
    pos    = PORTFOLIO[ticker]
    row    = df[df["Ticker"] == ticker]

    st.markdown(f"""
    <div style="display:flex;align-items:baseline;gap:14px;margin-bottom:4px">
      <div class="terminal-header">{ticker}</div>
      {''.join(row["Signal"].map(sig_pill).values) if not row.empty else ""}
    </div>
    <div class="terminal-sub">TICKER ANALYSIS · 6-MONTH WINDOW</div>
    """, unsafe_allow_html=True)

    if row.empty or row["Price"].isna().all():
        st.markdown('<div class="no-data">No market data available for this ticker.</div>',
                    unsafe_allow_html=True)
    else:
        r     = row.iloc[0]
        price = r["Price"]
        cv    = r["Market Value"]
        cb    = r["Cost"]
        pnl   = r["PnL"]
        pnlp  = r["Return %"]
        sig   = r["Signal"]
        sc    = SIG_COLOR.get(sig,"#475569")

        m1,m2,m3,m4,m5,m6 = st.columns(6)
        m1.metric("PRICE",       f"${price:.2f}")
        m2.metric("AVG COST",    f"${pos['ac']:.2f}")
        m3.metric("MKT VALUE",   f"${cv:,.0f}")
        m4.metric("P&L",         f"${pnl:+,.0f}", delta=f"{pnlp:+.1f}%")
        m5.metric("RSI (14)",    str(r["RSI"]) if r["RSI"] else "—")
        m6.metric("VOLATILITY",  f"{r['Volatility %']:.2f}%" if r["Volatility %"] else "—")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # Indicator cards
        ic1,ic2,ic3,ic4 = st.columns(4)
        with ic1:
            ma20_v = r["MA20"]
            ma_c   = "#00e676" if (price and ma20_v and price > ma20_v) else "#ff5252"
            st.markdown(
                f'<div class="glass-card">'
                f'<div class="stat-label">MA 20</div>'
                f'<div class="stat-value" style="color:{ma_c}">${ma20_v:.2f}</div>'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:{ma_c};margin-top:4px">'
                f'{"▲ PRICE ABOVE" if price > ma20_v else "▼ PRICE BELOW"}</div>'
                f'</div>', unsafe_allow_html=True)
        with ic2:
            ma50_v = r["MA50"]
            ma_c2  = "#00e676" if (price and ma50_v and price > ma50_v) else "#ff5252"
            st.markdown(
                f'<div class="glass-card">'
                f'<div class="stat-label">MA 50</div>'
                f'<div class="stat-value" style="color:{ma_c2}">${ma50_v:.2f}</div>'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:{ma_c2};margin-top:4px">'
                f'{"▲ PRICE ABOVE" if price > ma50_v else "▼ PRICE BELOW"}</div>'
                f'</div>', unsafe_allow_html=True)
        with ic3:
            rsi_n  = r["RSI"]
            rsi_c_ = "#00e676" if rsi_n and rsi_n<30 else ("#ff5252" if rsi_n and rsi_n>70 else "#ffd740")
            rsi_lb = "OVERSOLD" if rsi_n and rsi_n<30 else ("OVERBOUGHT" if rsi_n and rsi_n>70 else "NEUTRAL")
            st.markdown(
                f'<div class="glass-card">'
                f'<div class="stat-label">RSI (14)</div>'
                f'<div class="stat-value" style="color:{rsi_c_}">{rsi_n if rsi_n else "—"}</div>'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:{rsi_c_};margin-top:4px">{rsi_lb}</div>'
                f'</div>', unsafe_allow_html=True)
        with ic4:
            risk_v = r["Risk"]
            risk_c = {"High":"#ff5252","Medium":"#ffd740","Low":"#00e676"}.get(risk_v,"#475569")
            st.markdown(
                f'<div class="glass-card">'
                f'<div class="stat-label">RISK LEVEL</div>'
                f'<div class="stat-value" style="color:{risk_c}">{risk_v}</div>'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:{risk_c};margin-top:4px">'
                f'VOL: {r["Volatility %"]:.2f}%</div>'
                f'</div>', unsafe_allow_html=True)

        # Chart
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Price History</div>', unsafe_allow_html=True)
        hist = get_price_data(ticker)
        if hist is not None and not hist.empty:
            chart_df = hist["Close"].squeeze().reset_index()
            chart_df.columns = ["Date","Close"]
            st.line_chart(chart_df.set_index("Date"), color="#38bdf8")

        # News
        st.markdown('<div class="section-title">📰 Latest News</div>', unsafe_allow_html=True)
        news = fetch_news(ticker)
        if news:
            for n in news:
                lh = (f'<a href="{n["link"]}" target="_blank" '
                      f'style="color:#cbd5e1;text-decoration:none">{n["title"]}</a>'
                      if n.get("link") else n["title"])
                st.markdown(
                    f'<div class="news-card">'
                    f'<div class="news-title">{lh}</div>'
                    f'<div class="news-date">{n.get("date","")}</div>'
                    f'</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data">No recent news found.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — NEWS FEED
# ══════════════════════════════════════════════════════════════════════════════
elif "📰" in page:
    st.markdown("""
    <div class="terminal-header">NEWS FEED</div>
    <div class="terminal-sub">LIVE HEADLINES PER TICKER</div>
    """, unsafe_allow_html=True)

    tks = st.multiselect("Select tickers", sorted(PORTFOLIO.keys()),
                          default=list(sorted(PORTFOLIO.keys()))[:6],
                          label_visibility="collapsed")
    if not tks:
        st.warning("Select at least one ticker.")
        st.stop()

    for tk in tks:
        news = fetch_news(tk)
        if not news: continue
        row_  = df[df["Ticker"] == tk]
        sig_  = row_.iloc[0]["Signal"] if not row_.empty else "No Signal"
        sc_   = SIG_COLOR.get(sig_,"#475569")
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;'
            f'margin:20px 0 8px;padding-bottom:6px;border-bottom:1px solid #1e293b">'
            f'<span class="ticker-label" style="color:{sc_}">{tk}</span>'
            f'{sig_pill(sig_)}</div>', unsafe_allow_html=True)
        for n in news[:3]:
            lh = (f'<a href="{n["link"]}" target="_blank" '
                  f'style="color:#cbd5e1;text-decoration:none">{n["title"]}</a>'
                  if n.get("link") else n["title"])
            st.markdown(
                f'<div class="news-card">'
                f'<div class="news-title">{lh}</div>'
                f'<div class="news-date">{n.get("date","")}</div>'
                f'</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — SIGNALS SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
elif "📉" in page:
    st.markdown("""
    <div class="terminal-header">SIGNALS SUMMARY</div>
    <div class="terminal-sub">RULE-BASED TECHNICAL SIGNALS · ALL POSITIONS</div>
    """, unsafe_allow_html=True)

    sf  = st.selectbox("Filter signal",
                        ["ALL","STRONG BUY","BUY","Positive Trend","Neutral",
                         "Weak Trend","SELL","STRONG SELL","No Signal"],
                        label_visibility="collapsed")
    flt = df_valid if sf == "ALL" else df_valid[df_valid["Signal"] == sf]
    flt = flt.sort_values("Return %", ascending=False)

    rows_h = ""
    for _, r in flt.iterrows():
        sig  = r.get("Signal","No Signal")
        sc   = SIG_COLOR.get(sig,"#475569")
        risk = r.get("Risk","Unknown")
        rc   = {"High":"#ff5252","Medium":"#ffd740","Low":"#00e676"}.get(risk,"#475569")
        rsi_n= r.get("RSI")
        rsi_c= "#00e676" if rsi_n and rsi_n<30 else ("#ff5252" if rsi_n and rsi_n>70 else "#94a3b8")
        ret_v= r.get("Return %", 0)
        ret_c= "#00e676" if ret_v >= 0 else "#ff5252"
        rows_h += f"""
        <tr>
          <td><span class="ticker-label" style="color:{sc}">{r['Ticker']}</span></td>
          <td>{sig_pill(sig)}</td>
          <td><span style="color:{rc};font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700">{risk}</span></td>
          <td class="mono" style="color:{rsi_c}">{rsi_n if rsi_n else '—'}</td>
          <td class="mono" style="color:{ret_c};font-weight:700">{ret_v:+.1f}%</td>
          <td class="mono" style="color:#475569">${r.get('Market Value',0):,.0f}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto;border-radius:12px;border:1px solid #1e293b">
    <table style="width:100%;border-collapse:collapse;font-size:12px">
      <thead><tr style="border-bottom:1px solid #1e293b">
        {''.join(f'<th style="padding:10px 12px;text-align:left;font-family:JetBrains Mono,monospace;font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:#334155;background:#080c18">{h}</th>'
                 for h in ["Ticker","Signal","Risk","RSI","Return %","Mkt Value"])}
      </tr></thead>
      <tbody style="background:#0d1424">{rows_h}</tbody>
    </table></div>
    """, unsafe_allow_html=True)

    # Action lists
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    ca, cb_ = st.columns(2)
    with ca:
        st.markdown('<div class="section-title">🟢 Buy Signals</div>', unsafe_allow_html=True)
        buys = df_valid[df_valid["Signal"].isin(["STRONG BUY","BUY","Positive Trend"])]
        buys = buys.sort_values("Return %", ascending=False)
        for _, r in buys.iterrows():
            sc = SIG_COLOR.get(r["Signal"],"#69f0ae")
            ret= r.get("Return %",0)
            rc = "#00e676" if ret>=0 else "#ff5252"
            st.markdown(
                f'<div class="portfolio-row">'
                f'<span class="ticker-label" style="color:{sc}">{r["Ticker"]}</span>'
                f'{sig_pill(r["Signal"])}'
                f'<span class="mono" style="color:{rc}">{ret:+.1f}%</span>'
                f'</div>', unsafe_allow_html=True)
    with cb_:
        st.markdown('<div class="section-title">🔴 Sell Signals</div>', unsafe_allow_html=True)
        sells = df_valid[df_valid["Signal"].isin(["STRONG SELL","SELL","Weak Trend"])]
        sells = sells.sort_values("Return %")
        for _, r in sells.iterrows():
            ret= r.get("Return %",0)
            rc = "#00e676" if ret>=0 else "#ff5252"
            st.markdown(
                f'<div class="portfolio-row">'
                f'<span class="ticker-label" style="color:#ff5252">{r["Ticker"]}</span>'
                f'{sig_pill(r["Signal"])}'
                f'<span class="mono" style="color:{rc}">{ret:+.1f}%</span>'
                f'</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — TRADING TOOLS
# ══════════════════════════════════════════════════════════════════════════════
elif "🛠️" in page:
    st.markdown("""
    <div class="terminal-header">TRADING TOOLS</div>
    <div class="terminal-sub">ANALYTICS · RISK · PERFORMANCE</div>
    """, unsafe_allow_html=True)

    tool = st.selectbox("", [
        "📊 Performance Distribution",
        "🎯 Risk Exposure Breakdown",
        "🏆 Top Trades to Execute",
        "📐 Position Sizer",
        "🛑 Stop-Loss Calculator",
    ], label_visibility="collapsed")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Performance distribution ──────────────────────────────────
    if "Performance" in tool:
        st.markdown('<div class="tool-header">Performance Distribution</div>', unsafe_allow_html=True)
        st.markdown('<div class="tool-sub">Return % across all positions — sorted descending</div>', unsafe_allow_html=True)

        sorted_df = df_valid.sort_values("Return %", ascending=False)

        for _, r in sorted_df.iterrows():
            ret = r["Return %"]
            bar_w = min(abs(ret) / max(abs(sorted_df["Return %"].max()), 1) * 100, 100)
            bar_c = "#00e676" if ret >= 0 else "#ff5252"
            sig   = r.get("Signal","No Signal")
            sc    = SIG_COLOR.get(sig,"#475569")
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;'
                f'padding:5px 0;border-bottom:.5px solid #1a2035">'
                f'<span class="ticker-label" style="color:{sc};width:85px;flex-shrink:0">{r["Ticker"]}</span>'
                f'<div style="flex:1;height:8px;background:#0d1424;border-radius:4px;overflow:hidden">'
                f'<div style="width:{bar_w:.0f}%;height:100%;background:{bar_c};border-radius:4px;'
                f'transition:width .3s ease"></div></div>'
                f'<span class="mono" style="color:{bar_c};font-weight:700;width:65px;text-align:right">'
                f'{ret:+.1f}%</span>'
                f'</div>', unsafe_allow_html=True)

    # ── Risk breakdown ─────────────────────────────────────────────
    elif "Risk" in tool:
        st.markdown('<div class="tool-header">Risk Exposure Breakdown</div>', unsafe_allow_html=True)
        st.markdown('<div class="tool-sub">Classified by volatility + position size</div>', unsafe_allow_html=True)

        risk_groups = {"High": [], "Medium": [], "Low": [], "Unknown": []}
        for _, r in df_valid.iterrows():
            risk_groups.get(r["Risk"], risk_groups["Unknown"]).append(r)

        for risk_lbl, rows_ in risk_groups.items():
            if not rows_: continue
            rc   = {"High":"#ff5252","Medium":"#ffd740","Low":"#00e676"}.get(risk_lbl,"#475569")
            total= sum(r["Market Value"] for r in rows_)
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;'
                f'margin:12px 0 6px;padding-bottom:4px;border-bottom:1px solid {rc}22">'
                f'<span style="font-family:\'Space Mono\',monospace;font-size:14px;'
                f'font-weight:700;color:{rc}">{risk_lbl}</span>'
                f'<span class="mono" style="color:#334155">{len(rows_)} positions · '
                f'${total:,.0f}</span></div>', unsafe_allow_html=True)
            for r in sorted(rows_, key=lambda x: x["Market Value"], reverse=True):
                ret = r.get("Return %",0)
                ret_c = "#00e676" if ret>=0 else "#ff5252"
                sig = r.get("Signal","No Signal")
                sc  = SIG_COLOR.get(sig,"#475569")
                st.markdown(
                    f'<div class="portfolio-row">'
                    f'<span class="ticker-label" style="color:{sc}">{r["Ticker"]}</span>'
                    f'<span class="mono" style="color:#475569">${r["Market Value"]:,.0f}</span>'
                    f'<span class="mono" style="color:{ret_c}">{ret:+.1f}%</span>'
                    f'<span class="mono" style="color:#334155">vol {r.get("Volatility %","—")}%</span>'
                    f'{sig_pill(sig)}'
                    f'</div>', unsafe_allow_html=True)

    # ── Top trades ─────────────────────────────────────────────────
    elif "Top Trades" in tool:
        st.markdown('<div class="tool-header">Top Trades to Execute</div>', unsafe_allow_html=True)
        st.markdown('<div class="tool-sub">Highest return positions — sorted by Return %</div>', unsafe_allow_html=True)

        top8 = df_valid.sort_values("Return %", ascending=False).head(8)
        for i, (_, r) in enumerate(top8.iterrows()):
            sig  = r.get("Signal","No Signal")
            sc   = SIG_COLOR.get(sig,"#475569")
            ret  = r.get("Return %",0)
            pnl  = r.get("PnL",0)
            ret_c= "#00e676" if ret>=0 else "#ff5252"
            rank_c = ["#ffd700","#c0c0c0","#cd7f32"] + ["#334155"]*10
            st.markdown(
                f'<div class="glass-card">'
                f'<div style="display:flex;align-items:center;gap:14px">'
                f'<span style="font-family:\'Space Mono\',monospace;font-size:22px;'
                f'font-weight:800;color:{rank_c[i]};min-width:36px">#{i+1}</span>'
                f'<span class="ticker-label" style="font-size:16px;color:{sc}">{r["Ticker"]}</span>'
                f'{sig_pill(sig)}'
                f'<div style="margin-left:auto;text-align:right">'
                f'<div class="mono" style="color:{ret_c};font-size:16px;font-weight:700">{ret:+.1f}%</div>'
                f'<div class="mono" style="color:{ret_c};font-size:11px">${pnl:+,.0f}</div>'
                f'</div></div></div>',
                unsafe_allow_html=True)

    # ── Position sizer ─────────────────────────────────────────────
    elif "Position" in tool:
        st.markdown('<div class="tool-header">Position Sizer</div>', unsafe_allow_html=True)
        st.markdown('<div class="tool-sub">Calculate optimal shares based on risk % of portfolio</div>', unsafe_allow_html=True)

        tv_ = df_valid["Market Value"].sum()
        pc1,pc2,pc3 = st.columns(3)
        port_v   = pc1.number_input("Portfolio value ($)", value=int(tv_), step=1000)
        risk_p   = pc2.number_input("Risk per trade (%)", value=2.0, step=0.5, min_value=0.1, max_value=10.0)
        entry_p  = pc3.number_input("Entry price ($)", value=100.0, step=1.0)
        stop_p   = pc1.number_input("Stop-loss price ($)", value=93.0, step=0.5)
        target_p = pc2.number_input("Target price ($)", value=115.0, step=1.0)

        if entry_p > stop_p > 0:
            risk_amt = port_v * risk_p / 100
            risk_per = entry_p - stop_p
            shares_  = risk_amt / risk_per
            pos_size = shares_ * entry_p
            pos_pct  = pos_size / port_v * 100
            rr       = (target_p - entry_p) / risk_per if risk_per > 0 else 0
            profit_  = (target_p - entry_p) * shares_

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            r1,r2,r3,r4 = st.columns(4)
            r1.metric("SHARES TO BUY",  f"{shares_:.1f}")
            r2.metric("POSITION SIZE",  f"${pos_size:,.0f}")
            r3.metric("% OF PORTFOLIO", f"{pos_pct:.1f}%")
            r4.metric("RISK/REWARD",    f"{rr:.2f}×")
            r5,r6 = st.columns(2)
            r5.metric("MAX LOSS",       f"-${risk_amt:,.0f}")
            r6.metric("MAX PROFIT",     f"+${profit_:,.0f}")

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            if rr < 1.5:
                st.warning("⚠️ R/R below 1.5× — consider a tighter stop or higher target.")
            elif rr >= 3:
                st.success("✅ Excellent R/R ratio (≥3×).")
            if pos_pct > 5:
                st.warning(f"⚠️ {pos_pct:.1f}% of portfolio in one trade — consider reducing size.")

    # ── Stop-loss calc ─────────────────────────────────────────────
    elif "Stop" in tool:
        st.markdown('<div class="tool-header">Stop-Loss Calculator</div>', unsafe_allow_html=True)
        st.markdown('<div class="tool-sub">ATR-based or percentage stop-loss with TP levels</div>', unsafe_allow_html=True)

        sl_tk   = st.selectbox("Position", sorted(PORTFOLIO.keys()))
        sl_pos  = PORTFOLIO[sl_tk]
        sl_row  = df[df["Ticker"] == sl_tk]
        sl_price= float(sl_row["Price"].iloc[0]) if not sl_row.empty and sl_row["Price"].notna().any() else sl_pos["ac"]

        method = st.selectbox("Method", ["% below entry","Trailing %"])
        entry_ = st.number_input("Entry price", value=sl_price, step=0.5)
        rr_sel = st.selectbox("R/R target", ["2×","2.5×","3×","4×"])
        rr_m   = float(rr_sel.replace("×",""))

        if method == "% below entry":
            sl_pct_ = st.slider("Stop-loss %", 2.0, 20.0, 7.0, 0.5)
        else:
            sl_pct_ = st.slider("Trailing stop %", 2.0, 20.0, 8.0, 0.5)

        sl_p_   = entry_ * (1 - sl_pct_/100)
        rsk_per = entry_ - sl_p_
        tp1_    = entry_ + rr_m * rsk_per
        tp2_    = entry_ + rr_m * 1.5 * rsk_per
        sh_held = sl_pos["shares"]

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        sc1,sc2,sc3 = st.columns(3)
        sc1.metric("STOP-LOSS",        f"${sl_p_:.2f}", delta=f"-{sl_pct_:.1f}%")
        sc2.metric(f"TP1 ({rr_sel})",  f"${tp1_:.2f}", delta=f"+{(tp1_/entry_-1)*100:.1f}%")
        sc3.metric(f"TP2 ({rr_m*1.5:.1f}×)", f"${tp2_:.2f}", delta=f"+{(tp2_/entry_-1)*100:.1f}%")

        st.markdown(f"""
        <div class="glass-card" style="margin-top:16px">
          <div class="stat-label" style="margin-bottom:10px">P&L on {sh_held:.2f} shares</div>
          <div style="display:flex;gap:24px;flex-wrap:wrap">
            <div><div class="stat-label">If stop hit</div>
                 <div class="mono" style="color:#ff5252;font-size:14px">-${rsk_per*sh_held:,.0f}</div></div>
            <div><div class="stat-label">If TP1 hit</div>
                 <div class="mono" style="color:#00e676;font-size:14px">+${(tp1_-entry_)*sh_held:,.0f}</div></div>
            <div><div class="stat-label">If TP2 hit</div>
                 <div class="mono" style="color:#00e676;font-size:14px">+${(tp2_-entry_)*sh_held:,.0f}</div></div>
          </div>
        </div>""", unsafe_allow_html=True)
