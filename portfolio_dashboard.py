"""
TFSA Terminal — Premium Edition
Features: sortable tables · earnings & consensus · 8 trading tools · live signals
Style:    Bloomberg-meets-cyberpunk terminal aesthetic
No AI / no trades manager
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TFSA Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Bloomberg terminal × cyberpunk
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;600&display=swap');

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
[data-testid="stSidebar"] .stRadio label {
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    color: #cbd5e1 !important;
}

/* animated grid background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(56,189,248,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56,189,248,0.025) 1px, transparent 1px);
    background-size: 40px 40px;
}

#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding: 1.5rem 2rem 2rem !important; position: relative; z-index: 1; }

/* metric containers */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1424 0%, #111827 100%) !important;
    border: 1px solid #1e293b !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    position: relative; overflow: hidden;
    transition: border-color 0.2s;
}
div[data-testid="metric-container"]::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
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
    font-size: 20px !important; font-weight: 700 !important;
    color: #e2e8f0 !important;
}

/* inputs */
.stSelectbox > div > div, .stTextInput input, .stNumberInput input {
    background: #0d1424 !important; border: 1px solid #1e293b !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* buttons */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
    color: #fff !important; border: none !important;
    border-radius: 8px !important; font-family: 'Space Mono', monospace !important;
    font-size: 11px !important; font-weight: 700 !important;
    letter-spacing: .06em !important; padding: 8px 20px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(14,165,233,0.35) !important;
}

/* tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #080c18 !important; border-radius: 10px !important;
    padding: 4px !important; border: 1px solid #1e293b !important; gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #475569 !important;
    border-radius: 8px !important; padding: 7px 16px !important;
    font-family: 'Space Mono', monospace !important; font-size: 11px !important;
    font-weight: 700 !important; letter-spacing: .04em; border: none !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#0ea5e9,#6366f1) !important;
    color: #fff !important;
}

/* multiselect */
.stMultiSelect > div > div {
    background: #0d1424 !important; border: 1px solid #1e293b !important;
    border-radius: 8px !important;
}

/* slider */
.stSlider [data-baseweb="slider"] { padding: 0 !important; }

/* scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #080c18; }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #38bdf8; }

/* ── custom classes ── */
.term-header {
    font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #f472b6 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -.02em; margin-bottom: 3px;
}
.term-sub {
    font-family: 'JetBrains Mono', monospace; font-size: 10px;
    color: #334155; letter-spacing: .1em; text-transform: uppercase;
    margin-bottom: 1.4rem;
}
.section-title {
    font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700;
    color: #e2e8f0; border-left: 3px solid #38bdf8; padding-left: 10px;
    margin: 1.4rem 0 .8rem;
}
.glass-card {
    background: linear-gradient(135deg,rgba(13,20,36,.95),rgba(17,24,39,.95));
    border: 1px solid #1e293b; border-radius: 14px;
    padding: 16px 20px; margin-bottom: 10px;
    transition: border-color 0.2s, transform 0.15s;
}
.glass-card:hover { border-color: #334155; transform: translateY(-1px); }

/* signal pills */
.sig-pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 600; letter-spacing: .07em; white-space: nowrap;
}
.p-STRONG-BUY  { background:rgba(0,230,118,.1);  color:#00e676; border:1px solid rgba(0,230,118,.35); }
.p-BUY         { background:rgba(105,240,174,.08);color:#69f0ae; border:1px solid rgba(105,240,174,.3);}
.p-HOLD        { background:rgba(255,215,64,.08); color:#ffd740; border:1px solid rgba(255,215,64,.3); }
.p-SELL        { background:rgba(255,82,82,.1);   color:#ff5252; border:1px solid rgba(255,82,82,.3);  }
.p-STRONG-SELL { background:rgba(213,0,0,.12);    color:#ff1744; border:1px solid rgba(213,0,0,.3);    }

/* sortable table */
.s-table { width:100%; border-collapse:collapse; font-size:12px; }
.s-table th {
    padding:9px 11px; text-align:left; border-bottom:1px solid #1e293b;
    font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:.1em;
    text-transform:uppercase; color:#334155; background:#080c18;
    cursor:pointer; user-select:none; position:sticky; top:0; white-space:nowrap;
}
.s-table th:hover { color:#94a3b8; background:#0d1220; }
.s-table td { padding:7px 11px; border-bottom:.5px solid #0f1624; }
.s-table tr:hover td { background:#0d1424; }
.mono { font-family:'JetBrains Mono',monospace; font-size:11px; }
.tk   { font-family:'Space Mono',monospace; font-size:12px; font-weight:700; }

/* earn / info boxes */
.earn-box {
    background:#0d1424; border:1px solid #1e293b; border-radius:10px;
    padding:13px 16px; margin:6px 0;
    transition: border-color 0.2s;
}
.earn-box:hover { border-color: #334155; }

/* news */
.news-card {
    background:#0d1424; border:1px solid #1e293b; border-left:3px solid #38bdf8;
    border-radius:0 10px 10px 0; padding:11px 15px; margin-bottom:7px;
    transition: border-color 0.2s, transform 0.15s;
}
.news-card:hover { border-color:#818cf8; transform:translateX(3px); }
.news-title {
    font-family:'Syne',sans-serif; font-size:12px; font-weight:600;
    color:#cbd5e1; line-height:1.45; margin-bottom:3px;
}
.news-date { font-family:'JetBrains Mono',monospace; font-size:10px; color:#334155; }

/* row cards */
.p-row {
    display:flex; align-items:center; justify-content:space-between;
    padding:9px 14px; border-radius:9px; margin-bottom:5px;
    background:#0d1424; border:1px solid #1e293b;
    transition: background 0.15s, border-color 0.15s;
}
.p-row:hover { background:#111827; border-color:#334155; }
.divider { border:none; border-top:1px solid #1e293b; margin:1.1rem 0; }
.no-data {
    font-family:'JetBrains Mono',monospace; font-size:12px;
    color:#1e293b; text-align:center; padding:2rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PORTFOLIO
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
    "DRUG.CN": {"shares": 6,        "ac": 59.93},
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

SECTOR_MAP = {
    "VFV.TO":"Core ETF","ZCN.TO":"Core ETF","XEF.TO":"Core ETF","VEE.TO":"Core ETF",
    "ZJPN.TO":"Core ETF","XSU.TO":"Core ETF","XID.TO":"Core ETF",
    "NVDA.TO":"AI / Semis","ASML.TO":"AI / Semis","AEHR":"AI / Semis","NVTS":"AI / Semis",
    "AMZN.TO":"Mega Tech","MSFT.TO":"Mega Tech","AAPL.TO":"Mega Tech","META.TO":"Mega Tech",
    "CRWV":"AI Infra","APLD":"AI Infra","BBAI":"AI Infra","SOUN":"AI Infra",
    "HELP":"AI Infra","NXT":"AI Infra",
    "OKLO":"Nuclear","NNE":"Nuclear","CEGS.TO":"Nuclear",
    "RGTI":"Quantum","QBTS":"Quantum",
    "RXRX":"Biotech","CMPS":"Biotech","RARE":"Biotech","IMVT":"Biotech",
    "ABCL":"Biotech","DRUG.CN":"Biotech","TEM":"Biotech",
    "LUNR":"Space","RDW":"Space","MDA.TO":"Space","JOBY":"Space",
    "LMT.TO":"Defense",
    "ENB.TO":"Energy","BEP-UN.TO":"Energy","CU.TO":"Energy","EOSE":"Energy",
    "BAM.TO":"Financials","BRK.TO":"Financials","NU":"Financials","TOI.V":"Financials",
    "WPM.TO":"Precious Metals","CGL.TO":"Precious Metals",
    "COPP.TO":"Materials","TMC":"Materials","PHOS.CN":"Materials",
    "PNG.V":"Materials","ONE.V":"Materials","SCD.V":"Materials",
    "RDDT":"Consumer","TSLA.TO":"Consumer",
    "ISRG.NE":"MedTech","VNM":"Emerging Mkts",
    "CLBT":"Other","APPS.NE":"Other","CRCL":"Other","WELL.TO":"Other",
}

# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def compute_signals(hist):
    if hist is None or len(hist) < 26:
        return {"signal": "HOLD", "score": 0, "details": {}, "confidence": 0}
    close  = hist["Close"].squeeze()
    score, max_sc, ind = 0, 0, {}

    # RSI
    d = close.diff()
    g = d.clip(lower=0).rolling(14).mean()
    l = (-d.clip(upper=0)).rolling(14).mean()
    rs = g / l.replace(0, np.nan)
    rsi_s = 100 - (100/(1+rs))
    rv = float(rsi_s.iloc[-1]) if len(rsi_s.dropna()) >= 1 else 50.0
    ind["RSI"] = round(rv, 1)
    max_sc += 2
    if rv < 30: score += 2
    elif rv < 45: score += 1
    elif rv > 70: score -= 2
    elif rv > 55: score -= 1

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    sig_l = macd.ewm(span=9, adjust=False).mean()
    mh = macd - sig_l
    mv = float(mh.iloc[-1]); mp = float(mh.iloc[-2]) if len(mh) > 1 else mv
    ind["MACD_hist"] = round(mv, 4)
    max_sc += 2
    if mv > 0 and mp <= 0: score += 2
    elif mv < 0 and mp >= 0: score -= 2
    elif mv > 0: score += 1
    elif mv < 0: score -= 1

    # SMA 50/200
    sma50 = close.rolling(50).mean(); sma200 = close.rolling(200).mean()
    price = float(close.iloc[-1])
    s50  = float(sma50.dropna().iloc[-1])  if len(sma50.dropna())  >= 1 else price
    s200 = float(sma200.dropna().iloc[-1]) if len(sma200.dropna()) >= 1 else price
    ind.update({"SMA50": round(s50,2), "SMA200": round(s200,2), "Price": round(price,2)})
    max_sc += 3
    score += 1 if price > s50  else -1
    score += 1 if price > s200 else -1
    score += 1 if s50   > s200 else -1

    # Bollinger
    sma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
    upper = sma20 + 2*std20; lower = sma20 - 2*std20
    bb_p = (price - float(lower.iloc[-1])) / (float(upper.iloc[-1]) - float(lower.iloc[-1]) + 1e-9)
    ind["BB_pos"] = round(bb_p, 2)
    max_sc += 1
    if bb_p < 0.2: score += 1
    elif bb_p > 0.8: score -= 1

    # Volume
    if "Volume" in hist.columns:
        vol  = hist["Volume"].squeeze()
        avgv = float(vol.rolling(20).mean().iloc[-1])
        vr   = float(vol.iloc[-1]) / avgv if avgv > 0 else 1.0
        ind["Vol_ratio"] = round(vr, 2)
        max_sc += 1
        if vr > 1.5 and price > float(close.iloc[-2]): score += 1

    # Momentum
    if len(close) >= 6:
        mom = (price / float(close.iloc[-6]) - 1) * 100
        ind["Mom_5d"] = round(mom, 2)
        max_sc += 1
        if mom > 5: score += 1
        elif mom < -5: score -= 1

    conf = round(abs(score) / max(max_sc, 1) * 100)
    if   score >= 5:  verdict = "STRONG BUY"
    elif score >= 2:  verdict = "BUY"
    elif score <= -5: verdict = "STRONG SELL"
    elif score <= -2: verdict = "SELL"
    else:             verdict = "HOLD"

    return {"signal": verdict, "score": score, "details": ind, "confidence": conf}


# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCHERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_ticker(ticker):
    try:
        t    = yf.Ticker(ticker)
        inf  = t.info or {}
        hist = t.history(period="1y", interval="1d")
        price = (inf.get("currentPrice") or inf.get("regularMarketPrice")
                 or inf.get("previousClose"))
        if price is None and not hist.empty:
            price = float(hist["Close"].iloc[-1])
        sig = compute_signals(hist)
        return {"ticker": ticker, "price": price, "info": inf, "hist": hist,
                "signal": sig["signal"], "score": sig["score"],
                "confidence": sig["confidence"], "indicators": sig["details"]}
    except Exception as e:
        return {"ticker": ticker, "price": None, "error": str(e),
                "signal": "HOLD", "score": 0, "confidence": 0,
                "indicators": {}, "hist": pd.DataFrame(), "info": {}}


@st.cache_data(ttl=600)
def fetch_news(ticker):
    try:
        items = []
        for n in (yf.Ticker(ticker).news or [])[:6]:
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


@st.cache_data(ttl=1800)
def fetch_earnings_consensus(ticker):
    result = {"next_earnings": None, "rec_key": None, "rec_mean": None,
              "num_analysts": 0, "target_mean": None,
              "target_high": None, "target_low": None, "upside": None}
    try:
        t = yf.Ticker(ticker)
        inf = t.info or {}
        next_earn = None

        # Path 1: earningsTimestamp
        et = inf.get("earningsTimestamp")
        if et and isinstance(et, (int, float)) and et > 0:
            try:
                dt = datetime.utcfromtimestamp(et)
                if dt > datetime.utcnow() - timedelta(days=1):
                    next_earn = dt.strftime("%Y-%m-%d")
            except: pass

        # Path 2: earningsDate list
        if not next_earn:
            ed_raw = inf.get("earningsDate")
            if ed_raw:
                if isinstance(ed_raw, (list, tuple)) and len(ed_raw) > 0:
                    try:
                        v = ed_raw[0]
                        dt = datetime.utcfromtimestamp(v) if isinstance(v,(int,float)) else pd.Timestamp(v).to_pydatetime()
                        if dt > datetime.utcnow() - timedelta(days=1):
                            next_earn = dt.strftime("%Y-%m-%d")
                    except: pass
                elif isinstance(ed_raw, str):
                    next_earn = ed_raw[:10]

        # Path 3: t.calendar
        if not next_earn:
            try:
                cal = t.calendar
                if isinstance(cal, dict):
                    ed = cal.get("Earnings Date") or cal.get("earningsDate")
                    if ed:
                        dates = [d for d in (ed if isinstance(ed,(list,tuple)) else [ed]) if pd.notna(d)]
                        if dates: next_earn = str(dates[0])[:10]
                elif isinstance(cal, pd.DataFrame) and not cal.empty:
                    for col in cal.columns:
                        for rk in ["Earnings Date","earningsDate"]:
                            try:
                                val = cal.at[rk, col]
                                if pd.notna(val): next_earn = str(val)[:10]; break
                            except: pass
                        if next_earn: break
            except: pass

        # Path 4: earnings_dates
        if not next_earn:
            try:
                ed_df = t.earnings_dates
                if ed_df is not None and not ed_df.empty:
                    future = ed_df[ed_df.index > pd.Timestamp.now(tz="UTC")]
                    if not future.empty:
                        next_earn = future.index[-1].strftime("%Y-%m-%d")
            except: pass

        result["next_earnings"] = next_earn
        result["rec_mean"]      = inf.get("recommendationMean")
        result["rec_key"]       = (inf.get("recommendationKey") or "").replace("_"," ").upper()
        result["num_analysts"]  = inf.get("numberOfAnalystOpinions") or 0
        result["target_mean"]   = inf.get("targetMeanPrice")
        result["target_high"]   = inf.get("targetHighPrice")
        result["target_low"]    = inf.get("targetLowPrice")
        price = inf.get("currentPrice") or inf.get("regularMarketPrice")
        if result["target_mean"] and price:
            result["upside"] = (result["target_mean"] / price - 1) * 100
    except Exception as e:
        result["error"] = str(e)
    return result


@st.cache_data(ttl=300)
def build_summary():
    rows = []
    for tk, pos in PORTFOLIO.items():
        d = fetch_ticker(tk)
        price = d.get("price")
        if not price: continue
        cv   = price * pos["shares"]
        cb   = pos["ac"] * pos["shares"]
        pnl  = cv - cb
        pnlp = pnl / cb * 100 if cb else 0
        ind  = d.get("indicators", {})
        rows.append({
            "Ticker":    tk,
            "Price":     round(price, 2),
            "Shares":    pos["shares"],
            "Avg Cost":  pos["ac"],
            "Mkt Value": round(cv, 2),
            "Cost":      round(cb, 2),
            "P&L $":     round(pnl, 2),
            "P&L %":     round(pnlp, 2),
            "Signal":    d.get("signal", "HOLD"),
            "Score":     d.get("score", 0),
            "Conf %":    d.get("confidence", 0),
            "RSI":       ind.get("RSI", "-"),
            "MACD":      ind.get("MACD_hist", "-"),
            "BB Pos":    ind.get("BB_pos", "-"),
            "Mom 5d%":   ind.get("Mom_5d", "-"),
            "SMA50":     ind.get("SMA50", "-"),
            "SMA200":    ind.get("SMA200", "-"),
            "Vol Ratio": ind.get("Vol_ratio", "-"),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
SIG_COLOR = {"STRONG BUY":"#00e676","BUY":"#69f0ae","HOLD":"#ffd740",
             "SELL":"#ff5252","STRONG SELL":"#ff1744"}

def sig_pill(sig):
    c   = sig.replace(" ","-")
    dot = SIG_COLOR.get(sig,"#94a3b8")
    return (f'<span class="sig-pill p-{c}">'
            f'<span style="width:5px;height:5px;border-radius:50%;'
            f'background:{dot};display:inline-block"></span>{sig}</span>')

def tk_col(tk, sig):
    c = SIG_COLOR.get(sig,"#94a3b8")
    return f'<span class="tk" style="color:{c}">{tk}</span>'

def pnl_span(val, fmt="+.1f%"):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return '<span style="color:#334155">—</span>'
    c = "#00e676" if val >= 0 else "#ff5252"
    t = f"{val:+.1f}%" if "%" in fmt else f"${val:+,.0f}"
    return f'<span class="mono" style="color:{c};font-weight:700">{t}</span>'

def fmt_v(v, f="$.2f"):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "N/A"
    if f == "$.2f":  return f"${v:,.2f}"
    if f == "$.1fB": return f"${v/1e9:,.1f}B"
    if f == "+.1f%": return f"{v:+.1f}%"
    if f == ".1f":   return f"{v:.1f}"
    if f == ".2f":   return f"{v:.2f}"
    return str(v)

def consensus_style(rk):
    r = (rk or "").upper()
    if "STRONG BUY" in r or "STRONGBUY" in r: return ("#00e676","STRONG BUY")
    if "BUY"  in r: return ("#69f0ae","BUY")
    if "SELL" in r: return ("#ff5252","SELL")
    if "HOLD" in r or "NEUTRAL" in r: return ("#ffd740","HOLD")
    return ("#94a3b8", rk or "N/A")


# ─────────────────────────────────────────────────────────────────────────────
# SORTABLE TABLE
# ─────────────────────────────────────────────────────────────────────────────
def sortable_table(df_in, table_id="tbl", height=600):
    cols = list(df_in.columns)
    head = "".join(
        f'<th onclick="doSort(\'{table_id}\',{i})">{c} <span style="opacity:.4">⇅</span></th>'
        for i, c in enumerate(cols))

    def cell(col, val, sig="HOLD"):
        if col == "Ticker":
            return f"<td>{tk_col(val, sig)}</td>"
        if col == "Signal":
            return f"<td>{sig_pill(val)}</td>"
        if col == "P&L %":
            c = "#00e676" if isinstance(val,(int,float)) and val>=0 else "#ff5252"
            t = f"{val:+.2f}%" if isinstance(val,(int,float)) else val
            return f'<td class="mono" style="color:{c};font-weight:700">{t}</td>'
        if col == "P&L $":
            c = "#00e676" if isinstance(val,(int,float)) and val>=0 else "#ff5252"
            t = f"${val:+,.0f}" if isinstance(val,(int,float)) else val
            return f'<td class="mono" style="color:{c}">{t}</td>'
        if col in ("Mkt Value","Cost","Price","Avg Cost"):
            t = f"${val:,.2f}" if isinstance(val,(int,float)) else val
            return f'<td class="mono" style="color:#94a3b8">{t}</td>'
        if col == "Shares":
            return f'<td class="mono" style="color:#475569">{val:.4f}</td>'
        return f'<td class="mono" style="color:#64748b">{val}</td>'

    rows_html = ""
    for _, row in df_in.iterrows():
        sig = row.get("Signal","HOLD")
        rows_html += "<tr>" + "".join(cell(c, row[c], sig) for c in cols) + "</tr>"

    html = f"""
<div style="overflow-x:auto;overflow-y:auto;max-height:{height}px;
     border-radius:12px;border:1px solid #1e293b">
<table class="s-table" id="{table_id}">
  <thead><tr>{head}</tr></thead>
  <tbody id="{table_id}_body">{rows_html}</tbody>
</table>
</div>
<script>
(function(){{
  var _d = {{}};
  window.doSort = function(id,col){{
    var tb = document.getElementById(id+'_body');
    if(!tb) return;
    var rows = Array.from(tb.rows);
    _d[id+col] = !_d[id+col];
    var asc = _d[id+col];
    rows.sort(function(a,b){{
      var av=(a.cells[col]||{{}}).innerText||'', bv=(b.cells[col]||{{}}).innerText||'';
      av=av.replace(/[$%+,]/g,''); bv=bv.replace(/[$%+,]/g,'');
      var an=parseFloat(av), bn=parseFloat(bv);
      if(!isNaN(an)&&!isNaN(bn)) return asc?an-bn:bn-an;
      return asc?av.localeCompare(bv):bv.localeCompare(av);
    }});
    rows.forEach(function(r){{tb.appendChild(r);}});
  }};
}})();
</script>"""
    st.components.v1.html(html, height=height+44, scrolling=False)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 0 14px">
      <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;
           background:linear-gradient(135deg,#38bdf8,#818cf8);
           -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        TFSA TERMINAL
      </div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
           color:#1e293b;letter-spacing:.1em;text-transform:uppercase;margin-top:2px">
        LIVE · {ts}
      </div>
    </div>
    """.format(ts=datetime.now().strftime("%H:%M:%S")), unsafe_allow_html=True)

    page = st.radio("", [
        "📊  Overview",
        "🔍  Ticker Dive",
        "📰  News Feed",
        "📉  Signals",
        "🛠️  Tools",
    ], label_visibility="collapsed")

    st.markdown('<hr style="border:none;border-top:1px solid #1a2035;margin:14px 0">',
                unsafe_allow_html=True)

    if "🔍" in page or "📰" in page:
        selected_tk = st.selectbox("Ticker", sorted(PORTFOLIO.keys()),
                                   label_visibility="collapsed")

    if st.button("⟳  Refresh"):
        st.cache_data.clear()
        st.rerun()

    st.markdown(f"""<div style="font-family:'JetBrains Mono',monospace;font-size:9px;
    color:#1e293b;margin-top:8px">Yahoo Finance · cache 5 min</div>""",
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("Syncing market data…"):
    df = build_summary()

df_v = df[df["Mkt Value"].notna()].copy()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if "📊" in page:
    st.markdown('<div class="term-header">PORTFOLIO OVERVIEW</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="term-sub">TFSA · {len(df_v)} POSITIONS · LIVE DATA</div>',
                unsafe_allow_html=True)

    tv   = df_v["Mkt Value"].sum()
    tc   = df_v["Cost"].sum()
    tpl  = df_v["P&L $"].sum()
    tpp  = tpl/tc*100 if tc else 0
    wins = (df_v["P&L $"] > 0).sum()
    loss = (df_v["P&L $"] < 0).sum()

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("PORTFOLIO VALUE", f"${tv:,.0f}")
    k2.metric("COST BASIS",      f"${tc:,.0f}")
    k3.metric("TOTAL P&L",       f"${tpl:+,.0f}", delta=f"{tpp:+.2f}%")
    k4.metric("WIN / LOSE",      f"{wins} / {loss}")
    k5.metric("POSITIONS",       str(len(df_v)))

    # Signal distribution
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    sc_counts = df_v["Signal"].value_counts()
    sc_html = '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:1.4rem">'
    for sig, col in [("STRONG BUY","#00e676"),("BUY","#69f0ae"),("HOLD","#ffd740"),
                     ("SELL","#ff5252"),("STRONG SELL","#ff1744")]:
        cnt = sc_counts.get(sig, 0)
        sc_html += (f'<div style="background:#0d1424;border:1px solid {col}33;'
                    f'border-radius:10px;padding:10px 16px;min-width:90px;text-align:center">'
                    f'<div style="font-family:\'Space Mono\',monospace;font-size:22px;'
                    f'font-weight:700;color:{col}">{cnt}</div>'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
                    f'color:{col}88;letter-spacing:.08em;text-transform:uppercase">{sig}</div></div>')
    sc_html += '</div>'
    st.markdown(sc_html, unsafe_allow_html=True)

    # Main sortable table
    st.markdown('<div class="section-title">All Positions — click header to sort</div>',
                unsafe_allow_html=True)
    disp = df_v[["Ticker","Price","Shares","Avg Cost","Mkt Value","P&L $","P&L %",
                  "Signal","Score","Conf %","RSI","MACD","BB Pos","Mom 5d%",
                  "SMA50","SMA200","Vol Ratio"]].sort_values("Mkt Value", ascending=False)
    sortable_table(disp, "main_tbl", height=620)

    # Winners / Losers
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    wc, lc = st.columns(2)
    with wc:
        st.markdown('<div class="section-title">🏆 Top 5 Winners</div>', unsafe_allow_html=True)
        for _, r in df_v.nlargest(5,"P&L %").iterrows():
            st.markdown(
                f'<div class="p-row">{tk_col(r["Ticker"],r["Signal"])}'
                f'{pnl_span(r["P&L %"],"+.1f%")}'
                f'{sig_pill(r["Signal"])}'
                f'<span class="mono" style="color:#334155">${r["Mkt Value"]:,.0f}</span>'
                f'</div>', unsafe_allow_html=True)
    with lc:
        st.markdown('<div class="section-title">⚠️ Top 5 Losers</div>', unsafe_allow_html=True)
        for _, r in df_v.nsmallest(5,"P&L %").iterrows():
            st.markdown(
                f'<div class="p-row">{tk_col(r["Ticker"],r["Signal"])}'
                f'{pnl_span(r["P&L %"],"+.1f%")}'
                f'{sig_pill(r["Signal"])}'
                f'<span class="mono" style="color:#334155">${r["Mkt Value"]:,.0f}</span>'
                f'</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — TICKER DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
elif "🔍" in page:
    ticker = selected_tk
    pos    = PORTFOLIO[ticker]

    st.markdown(f'<div class="term-header">{ticker}</div>', unsafe_allow_html=True)
    st.markdown('<div class="term-sub">TICKER DEEP DIVE · 1-YEAR WINDOW</div>',
                unsafe_allow_html=True)

    with st.spinner(f"Loading {ticker}…"):
        d    = fetch_ticker(ticker)
        news = fetch_news(ticker)
        ec   = fetch_earnings_consensus(ticker)

    price = d.get("price")
    if not price:
        st.markdown('<div class="no-data">No market data available.</div>', unsafe_allow_html=True)
        st.stop()

    inf   = d.get("info", {})
    cv    = price * pos["shares"]
    cb    = pos["ac"] * pos["shares"]
    pnl   = cv - cb
    pnlp  = pnl / cb * 100 if cb else 0
    sig   = d.get("signal","HOLD")
    score = d.get("score", 0)
    conf  = d.get("confidence", 0)
    ind   = d.get("indicators", {})
    sc    = SIG_COLOR.get(sig,"#94a3b8")

    # Header metrics
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("PRICE",     f"${price:.2f}")
    m2.metric("AVG COST",  f"${pos['ac']:.2f}")
    m3.metric("MKT VALUE", f"${cv:,.0f}")
    m4.metric("P&L",       f"${pnl:+,.0f}", delta=f"{pnlp:+.1f}%")
    m5.markdown(
        f'<div style="background:#0d1424;border-radius:12px;padding:14px;text-align:center;'
        f'border:1px solid {sc}55;margin-top:4px">'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
        f'color:#334155;letter-spacing:.1em;text-transform:uppercase">Signal · {conf}% conf</div>'
        f'<div style="font-family:\'Space Mono\',monospace;font-size:17px;'
        f'font-weight:900;color:{sc};margin:4px 0">{sig}</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:#334155">'
        f'Score {score:+d}</div></div>', unsafe_allow_html=True)

    # ── Earnings + Consensus ──
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🗓️ Earnings & Analyst Data</div>',
                unsafe_allow_html=True)

    ea1,ea2,ea3,ea4 = st.columns(4)

    ne = ec.get("next_earnings")
    days_away = None
    earn_col  = "#94a3b8"
    if ne:
        try:
            dt = datetime.strptime(ne[:10],"%Y-%m-%d")
            days_away = (dt - datetime.now()).days
            earn_col  = "#ffd740" if 0<=days_away<=30 else ("#ff5252" if days_away<0 else "#69f0ae")
        except: pass
    with ea1:
        st.markdown(
            f'<div class="earn-box">'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
            f'color:#334155;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px">Next Earnings</div>'
            f'<div style="font-family:\'Space Mono\',monospace;font-size:15px;'
            f'font-weight:700;color:{earn_col}">{ne if ne else "Not found"}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#334155;margin-top:3px">'
            f'{"In "+str(days_away)+" days" if days_away is not None and days_away>=0 else ("Past" if days_away is not None else "")}'
            f'</div></div>', unsafe_allow_html=True)

    rec_col, rec_lbl = consensus_style(ec.get("rec_key",""))
    n_anal = ec.get("num_analysts", 0)
    rm     = ec.get("rec_mean")
    with ea2:
        st.markdown(
            f'<div class="earn-box">'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
            f'color:#334155;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px">'
            f'Analyst Consensus ({n_anal})</div>'
            f'<div style="font-family:\'Space Mono\',monospace;font-size:17px;'
            f'font-weight:900;color:{rec_col}">{rec_lbl}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
            f'color:#334155;margin-top:3px">Score: {fmt_v(rm,".2f")}/5</div>'
            f'</div>', unsafe_allow_html=True)

    tgt = ec.get("target_mean"); up = ec.get("upside")
    up_c = "#00e676" if up and up>0 else "#ff5252"
    with ea3:
        st.markdown(
            f'<div class="earn-box">'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
            f'color:#334155;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px">Mean Target</div>'
            f'<div style="font-family:\'Space Mono\',monospace;font-size:17px;'
            f'font-weight:700;color:#e2e8f0">{fmt_v(tgt,"$.2f")}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
            f'color:{up_c};margin-top:3px">{"Upside "+fmt_v(up,"+.1f%") if up is not None else ""}</div>'
            f'</div>', unsafe_allow_html=True)

    tlo = ec.get("target_low"); thi = ec.get("target_high")
    with ea4:
        st.markdown(
            f'<div class="earn-box">'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;'
            f'color:#334155;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px">Target Range</div>'
            f'<div style="font-family:\'Space Mono\',monospace;font-size:15px;'
            f'font-weight:700;color:#e2e8f0">{fmt_v(tlo,"$.2f")} → {fmt_v(thi,"$.2f")}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
            f'color:#334155;margin-top:3px">Low / High</div>'
            f'</div>', unsafe_allow_html=True)

    # ── Chart + Indicators ──
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📈  Price Chart (1Y)", "📊  Indicators"])

    with tab1:
        hist = d.get("hist")
        if hist is not None and not hist.empty:
            cd = hist["Close"].squeeze().reset_index()
            cd.columns = ["Date","Close"]
            st.line_chart(cd.set_index("Date"), color="#38bdf8")
        else:
            st.markdown('<div class="no-data">No chart data.</div>', unsafe_allow_html=True)

    with tab2:
        rsi_v  = ind.get("RSI","N/A")
        sma50  = ind.get("SMA50","N/A")
        sma200 = ind.get("SMA200","N/A")
        macdh  = ind.get("MACD_hist","N/A")
        bbp    = ind.get("BB_pos","N/A")
        volr   = ind.get("Vol_ratio","N/A")
        mom    = ind.get("Mom_5d","N/A")

        tbl_data = [
            ("RSI (14)", rsi_v,
             "🟢 Oversold" if isinstance(rsi_v,(int,float)) and rsi_v<30
             else "🔴 Overbought" if isinstance(rsi_v,(int,float)) and rsi_v>70 else "🟡 Neutral"),
            ("MACD Histogram", macdh,
             "🟢 Bullish" if isinstance(macdh,(int,float)) and macdh>0 else "🔴 Bearish"),
            ("vs SMA 50",
             f"{'ABOVE ▲' if isinstance(sma50,(int,float)) and price>sma50 else 'BELOW ▼'} (${sma50})",
             "🟢" if isinstance(sma50,(int,float)) and price>sma50 else "🔴"),
            ("vs SMA 200",
             f"{'ABOVE ▲' if isinstance(sma200,(int,float)) and price>sma200 else 'BELOW ▼'} (${sma200})",
             "🟢" if isinstance(sma200,(int,float)) and price>sma200 else "🔴"),
            ("Bollinger Pos", bbp,
             "🟢 Buy zone" if isinstance(bbp,(int,float)) and bbp<0.2
             else "🔴 Sell zone" if isinstance(bbp,(int,float)) and bbp>0.8 else "🟡 Mid"),
            ("5d Momentum", f"{mom}%",
             "🟢 Strong" if isinstance(mom,(int,float)) and mom>5
             else "🔴 Weak" if isinstance(mom,(int,float)) and mom<-5 else "🟡 Flat"),
            ("Volume Ratio", volr,
             "🟢 High volume" if isinstance(volr,(int,float)) and volr>1.5 else "🟡 Normal"),
        ]
        st.dataframe(pd.DataFrame(tbl_data, columns=["Indicator","Value","Interpretation"]),
                     use_container_width=True, hide_index=True)

    # ── Company info ──
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    ci1, ci2, ci3 = st.columns(3)
    name   = inf.get("longName") or inf.get("shortName", ticker)
    sector = inf.get("sector","N/A"); industry = inf.get("industry","N/A")
    mktcap = inf.get("marketCap"); pe = inf.get("trailingPE"); fpe = inf.get("forwardPE")
    beta   = inf.get("beta"); divy = inf.get("dividendYield")
    w52h   = inf.get("fiftyTwoWeekHigh"); w52l = inf.get("fiftyTwoWeekLow")
    ci1.markdown(f"**{name}**\n\nSector: {sector}\n\nIndustry: {industry}")
    ci2.markdown(f"Market Cap: {fmt_v(mktcap,'$.1fB')}\n\nP/E trailing: {fmt_v(pe,'.1f')}\n\nP/E forward: {fmt_v(fpe,'.1f')}")
    ci3.markdown(f"Beta: {fmt_v(beta,'.2f')}\n\nDividend: {'{:.2%}'.format(divy) if divy else 'N/A'}\n\n52W: {fmt_v(w52l,'$.2f')} → {fmt_v(w52h,'$.2f')}")

    # ── News ──
    st.markdown(f'<div class="section-title">📰 News — {ticker}</div>', unsafe_allow_html=True)
    for n in (news or []):
        lh = (f'<a href="{n["link"]}" target="_blank" style="color:#cbd5e1;text-decoration:none">{n["title"]}</a>'
              if n.get("link") else n["title"])
        st.markdown(
            f'<div class="news-card"><div class="news-title">{lh}</div>'
            f'<div class="news-date">{n.get("date","")}</div></div>',
            unsafe_allow_html=True)
    if not news:
        st.markdown('<div class="no-data">No recent news.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — NEWS FEED
# ══════════════════════════════════════════════════════════════════════════════
elif "📰" in page:
    st.markdown('<div class="term-header">NEWS FEED</div>', unsafe_allow_html=True)
    st.markdown('<div class="term-sub">LIVE HEADLINES PER TICKER</div>', unsafe_allow_html=True)

    tks = st.multiselect("", sorted(PORTFOLIO.keys()),
                          default=list(sorted(PORTFOLIO.keys()))[:6],
                          label_visibility="collapsed")
    if not tks:
        st.warning("Select at least one ticker.")
        st.stop()

    for tk in tks:
        news = fetch_news(tk)
        if not news: continue
        row_ = df_v[df_v["Ticker"] == tk]
        sig_ = row_.iloc[0]["Signal"] if not row_.empty else "HOLD"
        sc_  = SIG_COLOR.get(sig_,"#94a3b8")
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;'
            f'margin:18px 0 7px;padding-bottom:7px;border-bottom:1px solid #1e293b">'
            f'{tk_col(tk,sig_)}{sig_pill(sig_)}</div>', unsafe_allow_html=True)
        for n in news[:3]:
            lh = (f'<a href="{n["link"]}" target="_blank" style="color:#cbd5e1;text-decoration:none">{n["title"]}</a>'
                  if n.get("link") else n["title"])
            st.markdown(
                f'<div class="news-card"><div class="news-title">{lh}</div>'
                f'<div class="news-date">{n.get("date","")}</div></div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — SIGNALS
# ══════════════════════════════════════════════════════════════════════════════
elif "📉" in page:
    st.markdown('<div class="term-header">SIGNALS SUMMARY</div>', unsafe_allow_html=True)
    st.markdown('<div class="term-sub">COMPOSITE TECHNICAL SIGNALS · ALL POSITIONS</div>',
                unsafe_allow_html=True)

    sf = st.selectbox("", ["ALL","STRONG BUY","BUY","HOLD","SELL","STRONG SELL"],
                      label_visibility="collapsed")
    filt = df_v if sf == "ALL" else df_v[df_v["Signal"] == sf]
    filt = filt.sort_values("Score", ascending=False)

    cols_s = ["Ticker","Price","P&L %","Signal","Score","Conf %",
              "RSI","MACD","BB Pos","Mom 5d%","SMA50","SMA200"]
    sortable_table(filt[cols_s].reset_index(drop=True), "sig_tbl", height=560)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    ca, cb_ = st.columns(2)
    with ca:
        st.markdown('<div class="section-title">🟢 Buy Signals</div>', unsafe_allow_html=True)
        buys = df_v[df_v["Signal"].isin(["BUY","STRONG BUY"])].sort_values("Score",ascending=False)
        for _, r in buys.iterrows():
            st.markdown(
                f'<div class="p-row">{tk_col(r["Ticker"],r["Signal"])}'
                f'{sig_pill(r["Signal"])}'
                f'<span class="mono" style="color:#475569">Score {r["Score"]:+d}</span>'
                f'{pnl_span(r["P&L %"],"+.1f%")}</div>', unsafe_allow_html=True)
    with cb_:
        st.markdown('<div class="section-title">🔴 Sell Signals</div>', unsafe_allow_html=True)
        sells = df_v[df_v["Signal"].isin(["SELL","STRONG SELL"])].sort_values("Score")
        for _, r in sells.iterrows():
            st.markdown(
                f'<div class="p-row">{tk_col(r["Ticker"],r["Signal"])}'
                f'{sig_pill(r["Signal"])}'
                f'<span class="mono" style="color:#475569">Score {r["Score"]:+d}</span>'
                f'{pnl_span(r["P&L %"],"+.1f%")}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — TRADING TOOLS
# ══════════════════════════════════════════════════════════════════════════════
elif "🛠️" in page:
    st.markdown('<div class="term-header">TRADING TOOLS</div>', unsafe_allow_html=True)
    st.markdown('<div class="term-sub">RISK · ANALYTICS · CALCULATORS</div>',
                unsafe_allow_html=True)

    tool = st.selectbox("", [
        "📐 Position Sizer",
        "🛑 Stop-Loss & Take-Profit",
        "📊 Correlation Matrix",
        "💰 Dividend Calendar",
        "🔥 Sector Heatmap",
        "📈 52-Week Range Tracker",
        "⚖️ Risk / Reward Calculator",
        "🧾 Concentration Check",
    ], label_visibility="collapsed")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── POSITION SIZER ────────────────────────────────────────────
    if "Position Sizer" in tool:
        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:18px;font-weight:700;margin-bottom:4px">Position Sizer</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#475569;margin-bottom:1.2rem">Optimal shares based on risk % of portfolio</div>', unsafe_allow_html=True)
        tc1,tc2,tc3 = st.columns(3)
        pv = tc1.number_input("Portfolio value ($)", value=int(df_v["Mkt Value"].sum()), step=1000)
        rp = tc2.number_input("Max risk per trade (%)", value=2.0, step=0.5, min_value=0.1, max_value=10.0)
        ep = tc3.number_input("Entry price ($)", value=100.0, step=1.0)
        sl = tc1.number_input("Stop-loss price ($)", value=92.0, step=1.0)
        tp = tc2.number_input("Target price ($)", value=115.0, step=1.0)
        cm = tc3.number_input("Commission ($)", value=0.0, step=1.0)

        if ep > sl > 0:
            ra  = pv * rp / 100
            rpr = ep - sl
            sh  = ra / rpr
            ps  = sh * ep
            psp = ps / pv * 100
            rr  = (tp - ep) / rpr if rpr > 0 else 0
            prf = (tp - ep) * sh - cm*2
            lmx = ra + cm*2

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            r1,r2,r3,r4 = st.columns(4)
            r1.metric("SHARES",      f"{sh:.1f}")
            r2.metric("POSITION",    f"${ps:,.0f}")
            r3.metric("% PORTFOLIO", f"{psp:.1f}%")
            r4.metric("RISK / REWARD", f"{rr:.2f}×")
            r5,r6 = st.columns(2)
            r5.metric("MAX LOSS",   f"-${lmx:,.0f}",  delta=f"-{rp:.1f}%")
            r6.metric("MAX PROFIT", f"+${prf:,.0f}", delta=f"+{prf/pv*100:.1f}%")
            if rr < 1.5:   st.warning("⚠️ R/R below 1.5× — tighten stop or raise target.")
            elif rr >= 3:  st.success("✅ Excellent R/R (≥3×).")
            if psp > 5:    st.warning(f"⚠️ {psp:.1f}% of portfolio in one trade.")

    # ── STOP-LOSS & TAKE-PROFIT ───────────────────────────────────
    elif "Stop-Loss" in tool:
        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:18px;font-weight:700;margin-bottom:4px">Stop-Loss & Take-Profit</div>', unsafe_allow_html=True)
        tk_s  = st.selectbox("Position", sorted(PORTFOLIO.keys()))
        pos_s = PORTFOLIO[tk_s]
        d_s   = fetch_ticker(tk_s)
        pr_s  = d_s.get("price",0) or pos_s["ac"]

        col1, col2 = st.columns(2)
        method = col1.selectbox("Method", ["% below entry","ATR-based (2×)","Support (manual)","Trailing %"])
        rrt    = col2.selectbox("R/R target", ["1.5×","2×","2.5×","3×","4×"])
        rrm    = float(rrt.replace("×",""))
        entry  = st.number_input("Entry price ($)", value=float(pr_s), step=0.5)

        if method == "% below entry":
            slp = st.slider("Stop-loss %", 2.0, 20.0, 7.0, 0.5)
            slv = entry * (1 - slp/100)
        elif method == "ATR-based (2×)":
            hs  = d_s.get("hist")
            atv = 0
            if hs is not None and len(hs) >= 14:
                h_ = hs["High"].squeeze(); l_ = hs["Low"].squeeze(); c_ = hs["Close"].squeeze()
                tr = pd.concat([h_-l_,(h_-c_.shift()).abs(),(l_-c_.shift()).abs()],axis=1).max(axis=1)
                atv = float(tr.rolling(14).mean().iloc[-1])
            slv = entry - 2*atv
            st.info(f"ATR(14) = ${atv:.2f} · Stop = ${slv:.2f}")
        elif method == "Support (manual)":
            slv = st.number_input("Support price ($)", value=entry*0.93, step=0.5)
        else:
            slp = st.slider("Trailing %", 2.0, 20.0, 8.0, 0.5)
            slv = entry * (1 - slp/100)

        rp_  = entry - slv
        tp1_ = entry + rrm * rp_
        tp2_ = entry + rrm*1.5 * rp_
        sh_  = pos_s["shares"]

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        rc1,rc2,rc3 = st.columns(3)
        rc1.metric("STOP-LOSS",      f"${slv:.2f}", delta=f"{(slv/entry-1)*100:.1f}%")
        rc2.metric(f"TP1 ({rrt})",   f"${tp1_:.2f}", delta=f"+{(tp1_/entry-1)*100:.1f}%")
        rc3.metric(f"TP2 ({rrm*1.5:.1f}×)", f"${tp2_:.2f}", delta=f"+{(tp2_/entry-1)*100:.1f}%")

        st.markdown(f"""
| Scenario | Price | P&L on {sh_:.2f} shares |
|---|---|---|
| Stop hit | ${slv:.2f} | **-${rp_*sh_:,.0f}** |
| TP1 hit  | ${tp1_:.2f} | **+${(tp1_-entry)*sh_:,.0f}** |
| TP2 hit  | ${tp2_:.2f} | **+${(tp2_-entry)*sh_:,.0f}** |
""")

    # ── CORRELATION MATRIX ────────────────────────────────────────
    elif "Correlation" in tool:
        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:18px;font-weight:700;margin-bottom:4px">Correlation Matrix</div>', unsafe_allow_html=True)
        st.caption("🔴 >0.8 = moves together (no diversification) · 🟢 <-0.3 = negative correlation (hedge)")
        sel = st.multiselect("Tickers", sorted(PORTFOLIO.keys()), default=list(sorted(PORTFOLIO.keys()))[:12])
        if len(sel) < 2:
            st.warning("Select at least 2.")
        else:
            with st.spinner("Fetching…"):
                pd_ = {}
                for tk in sel:
                    h = fetch_ticker(tk).get("hist")
                    if h is not None and not h.empty:
                        pd_[tk] = h["Close"].squeeze()
            if pd_:
                corr = pd.DataFrame(pd_).dropna().pct_change().dropna().corr().round(2)
                def cc(v):
                    if v >= 0.8:  return "background-color:#1a0000;color:#ff5252"
                    if v >= 0.5:  return "background-color:#1a1000;color:#ffa726"
                    if v <= -0.3: return "background-color:#001a0d;color:#00e676"
                    return "color:#94a3b8"
                st.dataframe(corr.style.applymap(cc).format("{:.2f}"),
                             use_container_width=True)

    # ── DIVIDEND CALENDAR ─────────────────────────────────────────
    elif "Dividend" in tool:
        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:18px;font-weight:700;margin-bottom:4px">Dividend Calendar</div>', unsafe_allow_html=True)
        divs = []
        with st.spinner("Fetching…"):
            for tk, pos_d in PORTFOLIO.items():
                inf_d = fetch_ticker(tk).get("info",{})
                dy = inf_d.get("dividendYield"); dr = inf_d.get("dividendRate")
                exd = inf_d.get("exDividendDate")
                if dy and dy > 0:
                    ex_s = ""
                    if exd:
                        try: ex_s = datetime.utcfromtimestamp(exd).strftime("%Y-%m-%d")
                        except: pass
                    divs.append({"Ticker": tk, "Yield %": round(dy*100,2),
                                 "Annual Rate": round(dr or 0,4),
                                 "Your Annual $": round((dr or 0)*pos_d["shares"],2),
                                 "Ex-Div Date": ex_s or "N/A",
                                 "Shares": pos_d["shares"]})
        if divs:
            df_div = pd.DataFrame(divs).sort_values("Yield %",ascending=False)
            st.metric("TOTAL ANNUAL INCOME", f"${df_div['Your Annual $'].sum():,.2f}")
            st.dataframe(df_div, use_container_width=True, hide_index=True)
        else:
            st.info("No dividend-paying positions found.")

    # ── SECTOR HEATMAP ────────────────────────────────────────────
    elif "Sector" in tool:
        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:18px;font-weight:700;margin-bottom:12px">Sector Heatmap</div>', unsafe_allow_html=True)
        df_hm = df_v.copy()
        df_hm["Sector"] = df_hm["Ticker"].map(SECTOR_MAP).fillna("Other")
        grp = df_hm.groupby("Sector").agg(
            Value=("Mkt Value","sum"), PnL=("P&L $","sum"),
            PnL_Pct=("P&L %","mean"), Count=("Ticker","count")
        ).reset_index().sort_values("Value",ascending=False)
        total_v = df_hm["Mkt Value"].sum()

        for _, row in grp.iterrows():
            c  = "#00e676" if row["PnL_Pct"] >= 0 else "#ff5252"
            bw = min(row["Value"]/total_v*100*3.5, 100)
            st.markdown(
                f'<div class="glass-card">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px">'
                f'<span style="font-family:\'Syne\',sans-serif;font-size:13px;font-weight:700">{row["Sector"]}</span>'
                f'<span class="mono" style="color:#334155">{int(row["Count"])} pos · ${row["Value"]:,.0f}</span>'
                f'<span class="mono" style="color:{c};font-weight:700">{row["PnL_Pct"]:+.1f}% · ${row["PnL"]:+,.0f}</span>'
                f'</div>'
                f'<div style="height:5px;background:#1e293b;border-radius:3px">'
                f'<div style="width:{bw:.0f}%;height:100%;background:{c};border-radius:3px"></div>'
                f'</div></div>', unsafe_allow_html=True)

    # ── 52-WEEK RANGE ─────────────────────────────────────────────
    elif "52-Week" in tool:
        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:18px;font-weight:700;margin-bottom:4px">52-Week Range Tracker</div>', unsafe_allow_html=True)
        st.caption("🟢 <20% = near lows (value zone) · 🔴 >80% = near highs (extended)")
        rows52 = []
        with st.spinner("Loading…"):
            for tk in sorted(PORTFOLIO.keys()):
                d52   = fetch_ticker(tk)
                inf52 = d52.get("info",{})
                lo  = inf52.get("fiftyTwoWeekLow"); hi = inf52.get("fiftyTwoWeekHigh")
                pr  = d52.get("price")
                if lo and hi and pr and hi > lo:
                    rows52.append({"Ticker":tk,"Price":pr,"52W Low":lo,"52W High":hi,
                                   "Pos %":round((pr-lo)/(hi-lo)*100,1),
                                   "Signal":d52.get("signal","HOLD")})
        if rows52:
            df52 = pd.DataFrame(rows52).sort_values("Pos %")
            for _, r in df52.iterrows():
                p  = r["Pos %"]
                bc = "#ff5252" if p>80 else ("#00e676" if p<20 else "#ffd740")
                sc = SIG_COLOR.get(r["Signal"],"#94a3b8")
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;'
                    f'padding:6px 0;border-bottom:.5px solid #0f1624">'
                    f'<span class="tk" style="color:{sc};width:85px;flex-shrink:0">{r["Ticker"]}</span>'
                    f'<span class="mono" style="color:#334155;width:60px">${r["52W Low"]:.2f}</span>'
                    f'<div style="flex:1;height:8px;background:#1e293b;border-radius:4px;position:relative">'
                    f'<div style="position:absolute;left:{p:.0f}%;top:-3px;width:14px;height:14px;'
                    f'background:{bc};border-radius:50%;transform:translateX(-50%);'
                    f'box-shadow:0 0 6px {bc}88"></div></div>'
                    f'<span class="mono" style="color:#334155;width:60px;text-align:right">${r["52W High"]:.2f}</span>'
                    f'<span class="mono" style="color:{bc};font-weight:700;width:45px;text-align:right">{p:.0f}%</span>'
                    f'</div>', unsafe_allow_html=True)

    # ── RISK / REWARD CALCULATOR ──────────────────────────────────
    elif "Risk / Reward" in tool:
        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:18px;font-weight:700;margin-bottom:4px">Risk / Reward Calculator</div>', unsafe_allow_html=True)
        rc1, rc2 = st.columns(2)
        ep2  = rc1.number_input("Entry price", value=100.0, step=0.5)
        sp2  = rc1.number_input("Stop-loss",   value=92.0,  step=0.5)
        t1   = rc2.number_input("Target 1",    value=115.0, step=0.5)
        t2   = rc2.number_input("Target 2",    value=130.0, step=0.5)
        sh2  = rc1.number_input("Shares",      value=10.0,  step=1.0)
        pw   = rc2.slider("Win probability (%)", 30, 80, 55)

        if ep2 > sp2 > 0:
            risk2 = (ep2 - sp2) * sh2
            rw1   = (t1 - ep2) / (ep2 - sp2)
            rw2   = (t2 - ep2) / (ep2 - sp2)
            ev    = (pw/100 * (t1-ep2)*sh2) - ((1-pw/100) * risk2)
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("MAX RISK",      f"${risk2:,.0f}")
            m2.metric("R/R TO T1",     f"{rw1:.2f}×")
            m3.metric("R/R TO T2",     f"{rw2:.2f}×")
            m4.metric("EXPECTED VALUE",f"${ev:,.0f}", delta="Edge ✓" if ev>0 else "No edge ✗")
            if ev > 0: st.success(f"✅ Positive expected value at {pw}% win rate.")
            else:      st.error("❌ Negative expected value — adjust setup or skip.")

    # ── CONCENTRATION CHECK ───────────────────────────────────────
    elif "Concentration" in tool:
        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:18px;font-weight:700;margin-bottom:4px">Portfolio Concentration</div>', unsafe_allow_html=True)
        df_c  = df_v.copy()
        tv_c  = df_c["Mkt Value"].sum()
        df_c["Weight %"] = (df_c["Mkt Value"]/tv_c*100).round(2)
        df_c  = df_c.sort_values("Weight %", ascending=False)
        t5w   = df_c.head(5)["Weight %"].sum()
        t10w  = df_c.head(10)["Weight %"].sum()

        ca,cb_,cc = st.columns(3)
        ca.metric("TOP 5 WEIGHT",   f"{t5w:.1f}%",    delta="OK" if t5w<40 else "High")
        cb_.metric("TOP 10 WEIGHT", f"{t10w:.1f}%",   delta="OK" if t10w<60 else "High")
        cc.metric("POSITIONS",      str(len(df_c)),   delta="Too many" if len(df_c)>30 else "OK")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        for _, r in df_c.iterrows():
            w  = r["Weight %"]
            bw = min(w*6, 100)
            c  = "#ff5252" if w>8 else ("#ffd740" if w>4 else "#69f0ae")
            sc = SIG_COLOR.get(r.get("Signal","HOLD"),"#94a3b8")
            flag = " ⚠️" if w>8 else (" 👀" if w>4 else "")
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;'
                f'padding:5px 0;border-bottom:.5px solid #0f1624">'
                f'<span class="tk" style="color:{sc};width:90px;flex-shrink:0">{r["Ticker"]}{flag}</span>'
                f'<div style="flex:1;height:7px;background:#1e293b;border-radius:4px">'
                f'<div style="width:{bw:.0f}%;height:100%;background:{c};border-radius:4px"></div></div>'
                f'<span class="mono" style="color:{c};font-weight:700;width:48px;text-align:right">{w:.1f}%</span>'
                f'</div>', unsafe_allow_html=True)
