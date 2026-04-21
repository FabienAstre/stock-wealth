import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TFSA Portfolio Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: #1c1f26;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #2d3139;
        margin-bottom: 8px;
    }
    .news-item {
        background: #1c1f26;
        border-left: 3px solid #3d5afe;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 0 8px 8px 0;
    }
    .alert-card {
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        font-size: 13px;
    }
    .stDataFrame { font-size: 12px; }
    div[data-testid="metric-container"] {
        background-color: #1c1f26;
        border: 1px solid #2d3139;
        border-radius: 10px;
        padding: 12px 16px;
    }
    .explain-box {
        background: #1a1d24;
        border-left: 3px solid #3d5afe;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 6px 0 12px 0;
        font-size: 13px;
        color: #b0b8c8;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ── Theme mapping ──────────────────────────────────────────────────────────────
THEMES = {
    "MSFT.TO":  "AI Infrastructure",
    "AMZN.TO":  "AI Infrastructure",
    "META.TO":  "AI Infrastructure",
    "APLD":     "AI Infrastructure",
    "CRWV":     "AI Infrastructure",
    "BBAI":     "AI Applications",
    "SOUN":     "AI Applications",
    "TEM":      "AI Applications",
    "VFV.TO":   "Core ETFs",
    "ZCN.TO":   "Core ETFs",
    "XEF.TO":   "Core ETFs",
    "VEE.TO":   "Core ETFs",
    "XID.TO":   "Core ETFs",
    "XSU.TO":   "Core ETFs",
    "ZJPN.TO":  "Core ETFs",
    "VNM":      "Core ETFs",
    "NNE":      "Nuclear & Uranium",
    "OKLO":     "Nuclear & Uranium",
    "CEGS.TO":  "Nuclear & Uranium",
    "LUNR":     "Space, Aerospace & Defence",
    "RDW":      "Space, Aerospace & Defence",
    "MDA.TO":   "Space, Aerospace & Defence",
    "LMT.TO":   "Space, Aerospace & Defence",
    "JOBY":     "Space, Aerospace & Defence",
    "QBTS":     "Quantum Computing",
    "RGTI":     "Quantum Computing",
    "WPM.TO":   "Precious Metals & Mining",
    "COPP.TO":  "Precious Metals & Mining",
    "PNG.V":    "Precious Metals & Mining",
    "ABCL":     "Biotech & Health Tech",
    "RXRX":     "Biotech & Health Tech",
    "CMPS":     "Biotech & Health Tech",
    "RARE":     "Biotech & Health Tech",
    "IMVT":     "Biotech & Health Tech",
    "DRUG.CN":  "Biotech & Health Tech",
    "HELP":     "Biotech & Health Tech",
    "WELL.TO":  "Biotech & Health Tech",
    "NU":       "Fintech, Platforms & Compounders",
    "RDDT":     "Fintech, Platforms & Compounders",
    "BAM.TO":   "Fintech, Platforms & Compounders",
    "BRK.TO":   "Fintech, Platforms & Compounders",
    "TOI.V":    "Fintech, Platforms & Compounders",
    "CRCL":     "Fintech, Platforms & Compounders",
    "ENB.TO":   "Energy & Utilities",
    "CU.TO":    "Energy & Utilities",
    "BEP-UN.TO":"Energy & Utilities",
    "EOSE":     "Energy & Utilities",
    "NXT":      "Energy & Utilities",
    "ONE.V":    "Speculative / Micro-Cap",
    "PHOS.CN":  "Speculative / Micro-Cap",
    "SCD.V":    "Speculative / Micro-Cap",
    "TMC":      "Speculative / Micro-Cap",
    "CLBT":     "Speculative / Micro-Cap",
    "AAPL.TO":  "Tech / Software",
    "TSLA.TO":  "Tech / Software",
    "APPS.TO":  "Tech / Software",
    "NVDA.TO":  "Semiconductors",
    "ASML.TO":  "Semiconductors",
    "NVTS":     "Semiconductors",
    "AEHR":     "Semiconductors",
    "ISRG.NE":  "Space, Aerospace & Defence",
}

THEME_COLORS = {
    "AI Infrastructure":              "#378ADD",
    "AI Applications":                "#7F77DD",
    "Core ETFs":                      "#639922",
    "Nuclear & Uranium":              "#EF9F27",
    "Space, Aerospace & Defence":     "#5DCAA5",
    "Quantum Computing":              "#D4537E",
    "Precious Metals & Mining":       "#BA7517",
    "Biotech & Health Tech":          "#E24B4A",
    "Fintech, Platforms & Compounders":"#1D9E75",
    "Energy & Utilities":             "#888780",
    "Speculative / Micro-Cap":        "#F09595",
    "Tech / Software":                "#AFA9EC",
    "Semiconductors":                 "#FAC775",
}

# ── Portfolio data ─────────────────────────────────────────────────────────────
PORTFOLIO = {
    "AAPL.TO": {"shares": 29.99,   "ac": 32.86},
    "ABCL":    {"shares": 159.9965,"ac": 4.2607},
    "AEHR":    {"shares": 15,      "ac": 20.56},
    "AMZN.TO": {"shares": 90,      "ac": 8.51},
    "APLD":    {"shares": 25,      "ac": 24.72},
    "APPS.TO": {"shares": 39.842,  "ac": 17.68},
    "ASML.TO": {"shares": 45,      "ac": 26.20},
    "BAM.TO":  {"shares": 10.08,   "ac": 72.44},
    "BBAI":    {"shares": 60,      "ac": 7.655},
    "BEP-UN.TO":{"shares":30.3548, "ac": 39.07},
    "BRK.TO":  {"shares": 20,      "ac": 33.38},
    "CEGS.TO": {"shares": 50,      "ac": 21.78},
    "CLBT":    {"shares": 40,      "ac": 18.65},
    "CMPS":    {"shares": 80,      "ac": 5.00},
    "COPP.TO": {"shares": 17,      "ac": 51.35},
    "CRCL":    {"shares": 14,      "ac": 95.28},
    "CRWV":    {"shares": 12.9979, "ac": 109.50},
    "CU.TO":   {"shares": 30.26,   "ac": 37.39},
    "DRUG.CN": {"shares": 8,       "ac": 73.92},
    "ENB.TO":  {"shares": 20,      "ac": 62.53},
    "EOSE":    {"shares": 60,      "ac": 12.09},
    "HELP":    {"shares": 80,      "ac": 8.47},
    "IMVT":    {"shares": 20,      "ac": 26.48},
    "ISRG.NE": {"shares": 25,      "ac": 26.86},
    "JOBY":    {"shares": 60,      "ac": 11.27},
    "LMT.TO":  {"shares": 30.14,   "ac": 31.03},
    "LUNR":    {"shares": 45,      "ac": 11.08},
    "MDA.TO":  {"shares": 50,      "ac": 30.38},
    "META.TO": {"shares": 30,      "ac": 34.75},
    "MSFT.TO": {"shares": 60.11,   "ac": 27.40},
    "NNE":     {"shares": 10,      "ac": 42.58},
    "NU":      {"shares": 40,      "ac": 14.98},
    "NVDA.TO": {"shares": 80,      "ac": 22.96},
    "NVTS":    {"shares": 60,      "ac": 7.84},
    "NXT":     {"shares": 8,       "ac": 72.18},
    "OKLO":    {"shares": 9,       "ac": 121.28},
    "ONE.V":   {"shares": 400,     "ac": 0.8275},
    "PHOS.CN": {"shares": 500,     "ac": 0.5943},
    "PNG.V":   {"shares": 200,     "ac": 5.41},
    "QBTS":    {"shares": 25,      "ac": 25.34},
    "RARE":    {"shares": 20,      "ac": 29.56},
    "RDDT":    {"shares": 7,       "ac": 114.74},
    "RDW":     {"shares": 50,      "ac": 10.33},
    "RGTI":    {"shares": 20,      "ac": 31.16},
    "RXRX":    {"shares": 200,     "ac": 4.61},
    "SCD.V":   {"shares": 2500,    "ac": 0.2285},
    "SOUN":    {"shares": 50,      "ac": 9.50},
    "TEM":     {"shares": 10,      "ac": 63.64},
    "TMC":     {"shares": 100,     "ac": 5.27},
    "TOI.V":   {"shares": 5,       "ac": 115.85},
    "TSLA.TO": {"shares": 31.1267, "ac": 35.72},
    "VEE.TO":  {"shares": 32,      "ac": 41.06},
    "VFV.TO":  {"shares": 32.8581, "ac": 128.76},
    "VNM":     {"shares": 40,      "ac": 17.67},
    "WELL.TO": {"shares": 180,     "ac": 4.05},
    "WPM.TO":  {"shares": 6,       "ac": 146.66},
    "XEF.TO":  {"shares": 29.43,   "ac": 41.71},
    "XID.TO":  {"shares": 13.7926, "ac": 49.38},
    "XSU.TO":  {"shares": 12.18,   "ac": 46.39},
    "ZCN.TO":  {"shares": 25.13,   "ac": 34.91},
    "ZJPN.TO": {"shares": 13.21,   "ac": 45.04},
}

BENCHMARK = "VFV.TO"

# ── Indicator explanations ─────────────────────────────────────────────────────
INDICATOR_EXPLANATIONS = {
    "RSI": """**RSI (Relative Strength Index)** — Think of it as a temperature gauge for momentum.
- **Below 30** → Stock has been beaten down hard. Possibly oversold — a potential buying opportunity.
- **30–45** → Cooling off. Mild bullish lean.
- **45–55** → Neutral. No strong momentum either way.
- **55–70** → Warming up. Mild bearish lean (may be getting stretched).
- **Above 70** → Stock has been running hard. Possibly overbought — due for a pullback or rest.
*Rule of thumb: buy fear (low RSI), be cautious on euphoria (high RSI).*""",

    "MACD": """**MACD (Moving Average Convergence Divergence)** — Measures whether short-term momentum is accelerating or fading.
- The **histogram** is the key: positive bars = buyers in control right now, negative bars = sellers in control.
- **Bullish crossover**: histogram flips from negative to positive → momentum shift upward. Strong signal.
- **Bearish crossover**: histogram flips from positive to negative → momentum shift downward.
- Height of bars matters: tall positive bars = strong bullish momentum, shrinking bars = momentum fading.
*Best used as a timing signal, not standalone.*""",

    "SMA": """**SMA 50 / SMA 200 (Simple Moving Averages)** — The trend backbone.
- **Price above SMA50** → Short-term trend is up. Bulls are in control near-term.
- **Price below SMA50** → Short-term trend is down. Caution.
- **SMA50 above SMA200** → The "Golden Cross." Classic long-term bullish signal. Institutions pay attention to this.
- **SMA50 below SMA200** → The "Death Cross." Long-term bearish signal. Often precedes further weakness.
*The further price is from SMA200, the more stretched the move — in either direction.*""",

    "Bollinger": """**Bollinger Bands** — Shows where price sits within its recent volatility range.
- Calculated as 2 standard deviations above/below the 20-day moving average.
- **Position 0.0** = price is at the bottom of the band (lower band). Often a bounce setup.
- **Position 0.5** = price is at the midpoint. Neutral.
- **Position 1.0** = price is at the top of the band (upper band). Often a pullback setup.
- During strong trends, price can "walk the band" — staying near 0.8–1.0 for extended periods.
*Low BB position + oversold RSI together = high-conviction buy setup for mean-reversion trades.*""",

    "Volume": """**Volume Ratio** — Compares today's volume to the 20-day average volume.
- **Ratio > 1.5** = significantly above-average volume. Big moves on high volume are more meaningful.
- **Ratio < 0.5** = low volume. Price moves on thin volume are less reliable signals.
- High volume on an up day = institutional buying. High volume on a down day = distribution.
*Volume confirms or questions price moves — it's the "conviction" indicator.*""",

    "Beta": """**Portfolio Beta** — How much your portfolio swings relative to the market (S&P 500 via VFV.TO).
- **Beta = 1.0** → Moves in line with the market.
- **Beta = 1.5** → If the market drops 10%, your portfolio historically drops ~15%.
- **Beta = 0.5** → Half the market's volatility. More defensive.
- **Negative beta** → Moves opposite to the market (rare — gold, inverse ETFs).
*A high-beta portfolio can generate outsized gains in bull markets and outsized losses in bear markets. Know your number.*""",

    "Drawdown": """**Drawdown from 52-Week High** — How far a position has fallen from its peak.
- **0% to -10%** → Normal fluctuation. No action needed unless thesis is broken.
- **-10% to -25%** → Correction territory. Worth reviewing the thesis.
- **-25% to -50%** → Deep drawdown. Requires strong conviction to hold or add.
- **Below -50%** → The stock needs to double just to get back to where it was. High risk.
*Drawdown is the most honest measure of pain. It strips away the "but it was higher" excuse.*""",

    "Correlation": """**Correlation Matrix** — Shows how much your positions move together.
- **+1.0** → Perfect correlation. They move in lockstep. No diversification benefit.
- **0.0** → No relationship. True diversification.
- **-1.0** → Perfect inverse correlation. One zigs when the other zags. Maximum hedge.
- In practice, most stocks show 0.3–0.7 correlation with each other, especially in the same sector.
*High correlation within a theme is expected. The risk is when ALL your themes correlate during a market crash — which they tend to do.*""",
}

# ── Technical signal engine ────────────────────────────────────────────────────
def compute_signals(hist: pd.DataFrame) -> dict:
    if hist is None or len(hist) < 30:
        return {"signal": "HOLD", "score": 0, "details": {}}
    close  = hist["Close"].squeeze()
    signals = {}
    score   = 0

    # RSI
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = 100 - (100 / (1 + rs))
    rsi_val = float(rsi.iloc[-1]) if not rsi.empty else 50
    signals["RSI"] = round(rsi_val, 1)
    if   rsi_val < 30: score += 2
    elif rsi_val < 45: score += 1
    elif rsi_val > 70: score -= 2
    elif rsi_val > 55: score -= 1

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    signal_line = macd.ewm(span=9, adjust=False).mean()
    macd_hist   = macd - signal_line
    signals["MACD_hist"] = round(float(macd_hist.iloc[-1]), 4) if not macd_hist.empty else 0
    if len(macd_hist) >= 2:
        if macd_hist.iloc[-1] > 0 and macd_hist.iloc[-2] <= 0: score += 2
        elif macd_hist.iloc[-1] < 0 and macd_hist.iloc[-2] >= 0: score -= 2
        elif macd_hist.iloc[-1] > 0: score += 1
        elif macd_hist.iloc[-1] < 0: score -= 1

    # SMA
    sma50  = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    price  = float(close.iloc[-1])
    s50    = float(sma50.iloc[-1])  if not sma50.empty  else price
    s200   = float(sma200.iloc[-1]) if not sma200.empty else price
    signals["SMA50"]  = round(s50,  2)
    signals["SMA200"] = round(s200, 2)
    signals["Price"]  = round(price, 2)
    if price > s50:  score += 1
    else:             score -= 1
    if price > s200: score += 1
    else:             score -= 1
    if s50 > s200:   score += 1
    else:             score -= 1

    # Bollinger
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    upper = sma20 + 2 * std20
    lower = sma20 - 2 * std20
    bb_pos = (price - float(lower.iloc[-1])) / (float(upper.iloc[-1]) - float(lower.iloc[-1]) + 1e-9)
    signals["BB_pos"] = round(bb_pos, 2)
    if   bb_pos < 0.2: score += 1
    elif bb_pos > 0.8: score -= 1

    # Volume
    if "Volume" in hist.columns:
        vol     = hist["Volume"].squeeze()
        avg_vol = float(vol.rolling(20).mean().iloc[-1])
        last_vol= float(vol.iloc[-1])
        if avg_vol > 0:
            vol_ratio = last_vol / avg_vol
            signals["Vol_ratio"] = round(vol_ratio, 2)
            if vol_ratio > 1.5 and price > float(close.iloc[-2]): score += 1

    # 52W high/low
    high_52w = float(close.rolling(252).max().iloc[-1]) if len(close) >= 20 else price
    low_52w  = float(close.rolling(252).min().iloc[-1]) if len(close) >= 20 else price
    signals["High_52W"] = round(high_52w, 2)
    signals["Low_52W"]  = round(low_52w,  2)
    signals["Drawdown"] = round((price - high_52w) / high_52w * 100, 1) if high_52w > 0 else 0

    # Daily / weekly returns
    if len(close) >= 2:
        signals["Return_1D"] = round((float(close.iloc[-1]) / float(close.iloc[-2]) - 1) * 100, 2)
    else:
        signals["Return_1D"] = 0.0
    if len(close) >= 6:
        signals["Return_1W"] = round((float(close.iloc[-1]) / float(close.iloc[-6]) - 1) * 100, 2)
    else:
        signals["Return_1W"] = signals["Return_1D"]

    if   score >= 5:  verdict = "STRONG BUY"
    elif score >= 2:  verdict = "BUY"
    elif score <= -5: verdict = "STRONG SELL"
    elif score <= -2: verdict = "SELL"
    else:             verdict = "HOLD"

    return {"signal": verdict, "score": score, "details": signals}


# ── Data fetchers ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_ticker_data(ticker: str):
    try:
        t        = yf.Ticker(ticker)
        hist_1y  = t.history(period="1y",  interval="1d")
        hist_5d  = t.history(period="5d",  interval="15m")
        hist_1d  = t.history(period="1d",  interval="5m")
        price    = None
        try:
            inf   = t.info or {}
            price = (inf.get("currentPrice") or inf.get("regularMarketPrice") or inf.get("previousClose"))
        except Exception:
            inf = {}
        if price is None and not hist_1y.empty:
            price = float(hist_1y["Close"].squeeze().iloc[-1])
        if price is None:
            try: price = t.fast_info.get("last_price") or t.fast_info.get("lastPrice")
            except: pass
        sig = compute_signals(hist_1y)
        return {
            "ticker": ticker, "price": price, "info": inf,
            "hist_1y": hist_1y, "hist_5d": hist_5d, "hist_1d": hist_1d,
            "signal": sig["signal"], "score": sig["score"], "indicators": sig["details"],
        }
    except Exception as e:
        return {
            "ticker": ticker, "price": None, "error": str(e),
            "signal": "HOLD", "score": 0, "indicators": {}, "info": {},
            "hist_1y": pd.DataFrame(), "hist_5d": pd.DataFrame(), "hist_1d": pd.DataFrame(),
        }

@st.cache_data(ttl=600)
def fetch_news(ticker: str):
    try:
        t = yf.Ticker(ticker)
        news = t.news or []
        items = []
        for n in news[:5]:
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

@st.cache_data(ttl=300)
def build_portfolio_summary():
    rows = []
    for ticker, pos in PORTFOLIO.items():
        d     = fetch_ticker_data(ticker)
        price = d.get("price")
        if price is None:
            continue
        shares = pos["shares"]
        ac     = pos["ac"]
        cv     = price * shares
        cb     = ac * shares
        pnl    = cv - cb
        pnl_p  = (pnl / cb * 100) if cb else 0
        ind    = d.get("indicators", {})
        rows.append({
            "Ticker":    ticker,
            "Theme":     THEMES.get(ticker, "Other"),
            "Price":     price,
            "Shares":    shares,
            "AC":        ac,
            "Mkt Value": cv,
            "Cost":      cb,
            "P&L $":     pnl,
            "P&L %":     pnl_p,
            "1D %":      ind.get("Return_1D", 0),
            "1W %":      ind.get("Return_1W", 0),
            "Signal":    d.get("signal", "HOLD"),
            "Score":     d.get("score", 0),
            "RSI":       ind.get("RSI", "-"),
            "SMA50":     ind.get("SMA50", "-"),
            "SMA200":    ind.get("SMA200", "-"),
            "Drawdown":  ind.get("Drawdown", 0),
            "High_52W":  ind.get("High_52W", price),
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=600)
def build_correlation_matrix():
    closes = {}
    for ticker in PORTFOLIO:
        d = fetch_ticker_data(ticker)
        h = d.get("hist_1y")
        if h is not None and not h.empty:
            s = h["Close"].squeeze()
            if hasattr(s, "name"):
                s.name = ticker
            closes[ticker] = s
    if len(closes) < 2:
        return pd.DataFrame()
    df = pd.DataFrame(closes)
    df = df.dropna(axis=1, how="all").ffill().dropna()
    return df.pct_change().dropna().corr()

@st.cache_data(ttl=600)
def compute_portfolio_beta():
    bench_data = fetch_ticker_data(BENCHMARK)
    bench_hist = bench_data.get("hist_1y")
    if bench_hist is None or bench_hist.empty:
        return None
    bench_ret = bench_hist["Close"].squeeze().pct_change().dropna()
    weighted_beta = 0.0
    total_val     = 0.0
    for ticker, pos in PORTFOLIO.items():
        d     = fetch_ticker_data(ticker)
        price = d.get("price")
        if price is None:
            continue
        val  = price * pos["shares"]
        hist = d.get("hist_1y")
        if hist is None or hist.empty:
            continue
        tk_ret = hist["Close"].squeeze().pct_change().dropna()
        combined = pd.concat([tk_ret, bench_ret], axis=1).dropna()
        if len(combined) < 20:
            continue
        combined.columns = ["tk", "bench"]
        cov  = combined["tk"].cov(combined["bench"])
        var  = combined["bench"].var()
        beta = cov / var if var != 0 else 1.0
        weighted_beta += beta * val
        total_val     += val
    return round(weighted_beta / total_val, 2) if total_val > 0 else None


# ── Helpers ───────────────────────────────────────────────────────────────────
SIG_COLORS = {
    "STRONG BUY": "#00e676", "BUY": "#69f0ae",
    "HOLD": "#ffd740",
    "SELL": "#ff5252", "STRONG SELL": "#ff1744",
}

def sig_badge(sig):
    c = SIG_COLORS.get(sig, "#aaa")
    return f'<span style="color:{c};font-weight:800">{sig}</span>'

def pnl_color(v):
    return "#00e676" if v >= 0 else "#ff5252"

def fmt_ret(v):
    c = "#00e676" if v >= 0 else "#ff5252"
    arrow = "▲" if v >= 0 else "▼"
    return f'<span style="color:{c}">{arrow}{abs(v):.2f}%</span>'


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    page = st.radio("View", [
        "📊 Overview",
        "🎯 Allocation & Themes",
        "🚨 Risk & Alerts",
        "🔍 Ticker Deep Dive",
        "📰 News Feed",
        "📉 Signals Summary",
    ])
    st.markdown("---")
    if page == "🔍 Ticker Deep Dive":
        selected = st.selectbox("Select ticker", sorted(PORTFOLIO.keys()))
    st.markdown("---")
    st.caption("Data via Yahoo Finance · Refreshes every 5 min")
    if st.button("🔄 Force Refresh"):
        st.cache_data.clear()
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Overview
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown("# 📊 TFSA Portfolio Dashboard")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    with st.spinner("Loading all positions…"):
        df = build_portfolio_summary()

    if df.empty:
        st.error("No data loaded.")
        st.stop()

    total_val   = df["Mkt Value"].sum()
    total_cost  = df["Cost"].sum()
    total_pnl   = df["P&L $"].sum()
    total_pnl_p = (total_pnl / total_cost * 100) if total_cost else 0
    daily_pnl   = (df["1D %"] * df["Mkt Value"] / 100).sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Portfolio Value",   f"${total_val:,.0f}")
    c2.metric("Cost Basis",        f"${total_cost:,.0f}")
    c3.metric("Total P&L",         f"${total_pnl:,.0f}",  delta=f"{total_pnl_p:+.1f}%")
    c4.metric("Today's P&L (est)", f"${daily_pnl:+,.0f}")
    c5.metric("Positions",         f"{len(df)} / {len(PORTFOLIO)}")

    # Signal distribution
    st.markdown("---")
    st.markdown("### 🚦 Signal Distribution")
    sig_counts = df["Signal"].value_counts()
    cols = st.columns(5)
    for i, (sig, color) in enumerate([
        ("STRONG BUY","#00e676"),("BUY","#69f0ae"),
        ("HOLD","#ffd740"),("SELL","#ff5252"),("STRONG SELL","#ff1744")
    ]):
        cnt = sig_counts.get(sig, 0)
        cols[i].markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:12px;'
            f'text-align:center;border-top:3px solid {color}">'
            f'<div style="font-size:22px;font-weight:700;color:{color}">{cnt}</div>'
            f'<div style="font-size:11px;color:#aaa">{sig}</div></div>',
            unsafe_allow_html=True)

    # Main table with 1D / 1W returns
    st.markdown("---")
    st.markdown("### 📋 All Positions")
    display_df = df[[
        "Ticker","Theme","Price","Shares","AC",
        "Mkt Value","P&L $","P&L %","1D %","1W %","Signal","RSI"
    ]].copy().sort_values("Mkt Value", ascending=False)

    display_df["Mkt Value"] = display_df["Mkt Value"].map("${:,.0f}".format)
    display_df["P&L $"]     = display_df["P&L $"].map("${:,.0f}".format)
    display_df["P&L %"]     = display_df["P&L %"].map("{:+.1f}%".format)
    display_df["1D %"]      = display_df["1D %"].map("{:+.2f}%".format)
    display_df["1W %"]      = display_df["1W %"].map("{:+.2f}%".format)
    display_df["Price"]     = display_df["Price"].map("${:.2f}".format)
    display_df["AC"]        = display_df["AC"].map("${:.2f}".format)
    display_df["Shares"]    = display_df["Shares"].map("{:.2f}".format)
    st.dataframe(display_df, use_container_width=True, height=700)

    # Winners / Losers
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏆 Top 5 Winners")
        top5 = df.nlargest(5, "P&L %")[["Ticker","P&L %","P&L $","1D %","Signal"]]
        top5["P&L %"] = top5["P&L %"].map("{:+.1f}%".format)
        top5["P&L $"] = top5["P&L $"].map("${:,.0f}".format)
        top5["1D %"]  = top5["1D %"].map("{:+.2f}%".format)
        st.dataframe(top5, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("### ⚠️ Top 5 Losers")
        bot5 = df.nsmallest(5, "P&L %")[["Ticker","P&L %","P&L $","1D %","Signal"]]
        bot5["P&L %"] = bot5["P&L %"].map("{:+.1f}%".format)
        bot5["P&L $"] = bot5["P&L $"].map("${:,.0f}".format)
        bot5["1D %"]  = bot5["1D %"].map("{:+.2f}%".format)
        st.dataframe(bot5, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Allocation & Themes
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Allocation & Themes":
    st.markdown("# 🎯 Allocation & Themes")

    with st.spinner("Building allocation data…"):
        df = build_portfolio_summary()

    if df.empty:
        st.error("No data loaded.")
        st.stop()

    # ── Theme allocation donut ──
    st.markdown("### 🍩 Portfolio by Theme")
    theme_df = df.groupby("Theme").agg(
        Value=("Mkt Value","sum"),
        Cost=("Cost","sum"),
    ).reset_index()
    theme_df["Weight %"] = theme_df["Value"] / theme_df["Value"].sum() * 100
    theme_df["P&L %"]    = (theme_df["Value"] - theme_df["Cost"]) / theme_df["Cost"] * 100
    theme_df = theme_df.sort_values("Value", ascending=False)

    col1, col2 = st.columns([1.2, 1])
    with col1:
        fig_donut = px.pie(
            theme_df, values="Value", names="Theme",
            color="Theme",
            color_discrete_map=THEME_COLORS,
            hole=0.5,
        )
        fig_donut.update_traces(
            textposition="outside", textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Value: $%{value:,.0f}<br>Weight: %{percent}<extra></extra>"
        )
        fig_donut.update_layout(
            showlegend=False, height=480,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        st.markdown("#### Theme Summary")
        th_disp = theme_df[["Theme","Weight %","P&L %","Value"]].copy()
        th_disp["Value"]    = th_disp["Value"].map("${:,.0f}".format)
        th_disp["Weight %"] = th_disp["Weight %"].map("{:.1f}%".format)
        th_disp["P&L %"]    = th_disp["P&L %"].map("{:+.1f}%".format)
        st.dataframe(th_disp, use_container_width=True, hide_index=True, height=420)

    # ── Position sizing treemap ──
    st.markdown("---")
    st.markdown("### 🗺️ Position Sizing Treemap")
    st.caption("Size = market value · Color = theme · Hover for details")

    total_val = df["Mkt Value"].sum()
    df["Weight %"] = df["Mkt Value"] / total_val * 100
    equal_w = 100 / len(df)

    fig_tree = px.treemap(
        df,
        path=["Theme","Ticker"],
        values="Mkt Value",
        color="Theme",
        color_discrete_map=THEME_COLORS,
        custom_data=["P&L %","Signal","Weight %","1D %"],
        hover_name="Ticker",
    )
    fig_tree.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Market Value: $%{value:,.0f}<br>"
            "Weight: %{customdata[2]:.1f}%<br>"
            "P&L: %{customdata[0]:+.1f}%<br>"
            "1D: %{customdata[3]:+.2f}%<br>"
            "Signal: %{customdata[1]}<extra></extra>"
        ),
        textinfo="label",
    )
    fig_tree.update_layout(
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ccc",
        margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_tree, use_container_width=True)

    # ── Cost basis progress bars ──
    st.markdown("---")
    st.markdown("### 📏 Cost Basis Progress — Distance from Breakeven")
    st.caption("Green = in profit · Red = underwater · Bar shows current price as % of avg cost")

    df_sorted = df.sort_values("P&L %", ascending=False)

    for _, row in df_sorted.iterrows():
        pct   = row["P&L %"]
        color = "#00e676" if pct >= 0 else "#ff5252"
        bar_w = min(abs(pct) / max(df["P&L %"].abs().max(), 1) * 100, 100)
        label = f"+{pct:.1f}%" if pct >= 0 else f"{pct:.1f}%"
        theme_c = THEME_COLORS.get(row["Theme"], "#aaa")

        st.markdown(
            f'<div style="display:flex;align-items:center;margin-bottom:5px;gap:8px">'
            f'<div style="width:80px;font-size:12px;font-weight:700;color:#ddd">{row["Ticker"]}</div>'
            f'<div style="width:90px;font-size:10px;color:{theme_c}">{row["Theme"][:18]}</div>'
            f'<div style="flex:1;background:#2a2d35;border-radius:4px;height:14px;position:relative">'
            f'<div style="width:{bar_w}%;background:{color};height:100%;border-radius:4px;opacity:0.85"></div>'
            f'</div>'
            f'<div style="width:60px;font-size:12px;font-weight:700;color:{color};text-align:right">{label}</div>'
            f'<div style="width:80px;font-size:11px;color:#888;text-align:right">${row["Price"]:.2f} / ${row["AC"]:.2f}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Risk & Alerts
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🚨 Risk & Alerts":
    st.markdown("# 🚨 Risk & Alerts")

    with st.spinner("Computing risk metrics…"):
        df   = build_portfolio_summary()
        beta = compute_portfolio_beta()

    if df.empty:
        st.error("No data loaded.")
        st.stop()

    # ── Portfolio Beta ──
    st.markdown("### 📐 Portfolio Beta")
    with st.expander("ℹ️ What is Beta?"):
        st.markdown(INDICATOR_EXPLANATIONS["Beta"])

    b1, b2, b3 = st.columns(3)
    if beta is not None:
        beta_color = "#ff5252" if beta > 1.5 else ("#ffd740" if beta > 1.0 else "#00e676")
        b1.markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:16px;text-align:center;border-top:3px solid {beta_color}">'
            f'<div style="font-size:11px;color:#aaa">PORTFOLIO BETA (vs VFV.TO)</div>'
            f'<div style="font-size:32px;font-weight:900;color:{beta_color}">{beta}</div>'
            f'<div style="font-size:11px;color:#aaa">{"High risk / High reward" if beta>1.5 else ("Above market" if beta>1.0 else "Defensive")}</div>'
            f'</div>', unsafe_allow_html=True)
        b2.markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:16px;text-align:center;border-top:3px solid #3d5afe">'
            f'<div style="font-size:11px;color:#aaa">IF MARKET DROPS 10%</div>'
            f'<div style="font-size:32px;font-weight:900;color:#ff5252">-{beta*10:.1f}%</div>'
            f'<div style="font-size:11px;color:#aaa">Expected portfolio move</div>'
            f'</div>', unsafe_allow_html=True)
        b3.markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:16px;text-align:center;border-top:3px solid #3d5afe">'
            f'<div style="font-size:11px;color:#aaa">IF MARKET GAINS 10%</div>'
            f'<div style="font-size:32px;font-weight:900;color:#00e676">+{beta*10:.1f}%</div>'
            f'<div style="font-size:11px;color:#aaa">Expected portfolio move</div>'
            f'</div>', unsafe_allow_html=True)
    else:
        st.warning("Could not compute beta.")

    # ── Alert Flags ──
    st.markdown("---")
    st.markdown("### 🚦 Alert Flags")

    alerts = []
    for _, row in df.iterrows():
        rsi   = row["RSI"]
        price = row["Price"]
        s50   = row["SMA50"]
        s200  = row["SMA200"]
        dd    = row["Drawdown"]
        tk    = row["Ticker"]
        pnl   = row["P&L %"]

        if isinstance(rsi, (int, float)):
            if rsi < 25:
                alerts.append({"type":"RSI Oversold",   "ticker":tk, "value":f"RSI {rsi}",
                                "msg":"Deeply oversold — potential entry / add opportunity",
                                "color":"#00e676", "priority":1})
            elif rsi > 75:
                alerts.append({"type":"RSI Overbought", "ticker":tk, "value":f"RSI {rsi}",
                                "msg":"Overbought — consider trimming or tightening stop",
                                "color":"#ff5252", "priority":1})

        if isinstance(price,(int,float)) and isinstance(s50,(int,float)) and s50 > 0:
            pct_from_50 = (price - s50) / s50 * 100
            if -2 < pct_from_50 < 0:
                alerts.append({"type":"SMA50 Breakdown", "ticker":tk,
                                "value":f"Price ${price:.2f} vs SMA50 ${s50:.2f}",
                                "msg":"Just broke below SMA50 — momentum breakdown signal",
                                "color":"#ff5252", "priority":2})
            elif 0 < pct_from_50 < 2:
                alerts.append({"type":"SMA50 Reclaim",  "ticker":tk,
                                "value":f"Price ${price:.2f} vs SMA50 ${s50:.2f}",
                                "msg":"Just reclaimed SMA50 — momentum recovery signal",
                                "color":"#00e676", "priority":2})

        if isinstance(dd,(int,float)):
            if dd < -50:
                alerts.append({"type":"Deep Drawdown",  "ticker":tk, "value":f"{dd:.1f}% from 52W high",
                                "msg":"Down over 50% from peak — needs to double to recover",
                                "color":"#ff1744", "priority":1})
            elif dd < -30:
                alerts.append({"type":"Drawdown Warning","ticker":tk,"value":f"{dd:.1f}% from 52W high",
                                "msg":"Significant drawdown — review thesis",
                                "color":"#ff5252", "priority":2})

        if isinstance(price,(int,float)) and isinstance(row["High_52W"],(int,float)):
            pct_from_high = (price - row["High_52W"]) / row["High_52W"] * 100
            if pct_from_high > -5:
                alerts.append({"type":"Near 52W High",  "ticker":tk,
                                "value":f"{pct_from_high:+.1f}% from 52W high",
                                "msg":"Near breakout territory — watch for continuation",
                                "color":"#ffd740", "priority":3})

    alerts = sorted(alerts, key=lambda x: x["priority"])

    if alerts:
        a1, a2, a3 = st.columns(3)
        cols_map = {
            "RSI Oversold": a1, "RSI Overbought": a1,
            "SMA50 Breakdown": a2, "SMA50 Reclaim": a2,
            "Deep Drawdown": a3, "Drawdown Warning": a3, "Near 52W High": a3,
        }
        rendered = {"a1": False, "a2": False, "a3": False}
        col_labels = {a1: "**RSI Alerts**", a2: "**SMA50 Alerts**", a3: "**Drawdown / 52W Alerts**"}
        for al in alerts:
            col = cols_map.get(al["type"], a1)
            key = {a1:"a1", a2:"a2", a3:"a3"}[col]
            if not rendered[key]:
                col.markdown(col_labels[col])
                rendered[key] = True
            col.markdown(
                f'<div style="background:#1c1f26;border-left:3px solid {al["color"]};'
                f'border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:6px">'
                f'<div style="font-size:13px;font-weight:700;color:{al["color"]}">{al["ticker"]} — {al["type"]}</div>'
                f'<div style="font-size:11px;color:#aaa">{al["value"]}</div>'
                f'<div style="font-size:11px;color:#888;margin-top:2px">{al["msg"]}</div>'
                f'</div>', unsafe_allow_html=True)
    else:
        st.success("No active alerts at this time.")

    # ── Drawdown tracker ──
    st.markdown("---")
    st.markdown("### 📉 Drawdown Tracker — Distance from 52-Week High")
    with st.expander("ℹ️ What is Drawdown?"):
        st.markdown(INDICATOR_EXPLANATIONS["Drawdown"])

    dd_df = df[["Ticker","Theme","Drawdown","P&L %","Signal"]].copy()
    dd_df = dd_df.sort_values("Drawdown")

    fig_dd = px.bar(
        dd_df, x="Ticker", y="Drawdown",
        color="Theme", color_discrete_map=THEME_COLORS,
        labels={"Drawdown":"Drawdown from 52W High (%)"},
        custom_data=["P&L %","Signal","Theme"],
    )
    fig_dd.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>Drawdown: %{y:.1f}%<br>"
            "P&L: %{customdata[0]:+.1f}%<br>"
            "Signal: %{customdata[1]}<br>"
            "Theme: %{customdata[2]}<extra></extra>"
        )
    )
    fig_dd.add_hline(y=-25, line_dash="dash", line_color="#ff5252",
                     annotation_text="-25% warning", annotation_font_color="#ff5252")
    fig_dd.add_hline(y=-50, line_dash="dash", line_color="#ff1744",
                     annotation_text="-50% critical", annotation_font_color="#ff1744")
    fig_dd.update_layout(
        height=400, xaxis_tickangle=-45,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ccc", showlegend=True,
        margin=dict(t=20, b=80),
        yaxis=dict(gridcolor="#2d3139"),
        xaxis=dict(gridcolor="#2d3139"),
    )
    st.plotly_chart(fig_dd, use_container_width=True)

    # ── Correlation matrix ──
    st.markdown("---")
    st.markdown("### 🔗 Correlation Matrix (1Y Daily Returns)")
    with st.expander("ℹ️ What does Correlation mean?"):
        st.markdown(INDICATOR_EXPLANATIONS["Correlation"])

    with st.spinner("Computing correlations…"):
        corr = build_correlation_matrix()

    if not corr.empty:
        # Limit to positions we have data for — cap at 50 tickers for readability
        tickers_in = list(corr.columns)[:50]
        corr_sub   = corr.loc[tickers_in, tickers_in]

        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_sub.values,
            x=corr_sub.columns.tolist(),
            y=corr_sub.index.tolist(),
            colorscale=[
                [0.0,  "#ff1744"],
                [0.25, "#ff5252"],
                [0.5,  "#1c1f26"],
                [0.75, "#69f0ae"],
                [1.0,  "#00e676"],
            ],
            zmin=-1, zmax=1,
               hovertemplate="<b>%{y} / %{x}</b><br>Correlation: %{z:.2f}<extra></extra>",
            colorbar=dict(title="Correlation", tickfont=dict(color="#ccc"), titlefont=dict(color="#ccc")),
        fig_corr.update_layout(
            height=700,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc",
            xaxis=dict(tickfont=dict(size=9), tickangle=-45),
            yaxis=dict(tickfont=dict(size=9), autorange="reversed"),
            margin=dict(t=20, b=120, l=120, r=20),
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        st.caption("Green = moves together · Dark = uncorrelated · Red = inverse relationship")
    else:
        st.warning("Not enough data for correlation matrix.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Ticker Deep Dive
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Ticker Deep Dive":
    ticker = selected
    pos    = PORTFOLIO[ticker]
    st.markdown(f"# 🔍 {ticker}")
    theme  = THEMES.get(ticker, "Other")
    theme_c = THEME_COLORS.get(theme, "#aaa")
    st.markdown(
        f'<span style="background:{theme_c}22;color:{theme_c};border:1px solid {theme_c}55;'
        f'border-radius:6px;padding:3px 10px;font-size:12px">{theme}</span>',
        unsafe_allow_html=True)

    with st.spinner(f"Loading {ticker}…"):
        d    = fetch_ticker_data(ticker)
        news = fetch_news(ticker)

    price = d.get("price")
    if price is None:
        st.error(f"Could not fetch data for {ticker}.")
        st.stop()

    inf    = d.get("info", {})
    shares = pos["shares"]
    ac     = pos["ac"]
    cv     = price * shares
    cb     = ac * shares
    pnl    = cv - cb
    pnl_p  = pnl / cb * 100 if cb else 0
    sig    = d.get("signal", "HOLD")
    score  = d.get("score", 0)
    ind    = d.get("indicators", {})
    sig_c  = SIG_COLORS.get(sig, "#aaa")

    # Header metrics
    c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
    c1.metric("Price",        f"${price:.2f}")
    c2.metric("Avg Cost",     f"${ac:.2f}")
    c3.metric("Market Value", f"${cv:,.0f}")
    c4.metric("P&L",          f"${pnl:,.0f}", delta=f"{pnl_p:+.1f}%")
    c5.metric("1D Return",    f"{ind.get('Return_1D',0):+.2f}%")
    c6.metric("1W Return",    f"{ind.get('Return_1W',0):+.2f}%")
    c7.markdown(
        f'<div style="background:#1c1f26;border-radius:10px;padding:10px;text-align:center;'
        f'border:2px solid {sig_c};margin-top:4px">'
        f'<div style="font-size:10px;color:#aaa">SIGNAL</div>'
        f'<div style="font-size:17px;font-weight:900;color:{sig_c}">{sig}</div>'
        f'<div style="font-size:10px;color:#aaa">Score: {score:+d}</div></div>',
        unsafe_allow_html=True)

    # Drawdown banner
    dd = ind.get("Drawdown", 0)
    dd_c = "#ff1744" if dd < -50 else ("#ff5252" if dd < -25 else ("#ffd740" if dd < -10 else "#00e676"))
    st.markdown(
        f'<div style="background:#1c1f26;border-radius:8px;padding:8px 14px;margin:8px 0;'
        f'border-left:4px solid {dd_c};font-size:13px">'
        f'<b style="color:{dd_c}">Drawdown from 52W High: {dd:.1f}%</b>'
        f' &nbsp;·&nbsp; 52W High: ${ind.get("High_52W", price):.2f}'
        f' &nbsp;·&nbsp; 52W Low: ${ind.get("Low_52W", price):.2f}'
        f'</div>', unsafe_allow_html=True)

    # Charts
    st.markdown("---")
    chart_tab, ind_tab, info_tab = st.tabs(["📈 Price Chart", "📊 Indicators", "🏢 Company Info"])

    with chart_tab:
        hist = d.get("hist_1y")
        if hist is not None and not hist.empty:
            close  = hist["Close"].squeeze().reset_index()
            close.columns = ["Date","Close"]
            sma50  = close["Close"].rolling(50).mean()
            sma200 = close["Close"].rolling(200).mean()

            fig_price = go.Figure()
            fig_price.add_trace(go.Scatter(
                x=close["Date"], y=close["Close"],
                name="Price", line=dict(color="#5c7cfa", width=2)))
            fig_price.add_trace(go.Scatter(
                x=close["Date"], y=sma50,
                name="SMA 50", line=dict(color="#ffd740", width=1, dash="dot")))
            fig_price.add_trace(go.Scatter(
                x=close["Date"], y=sma200,
                name="SMA 200", line=dict(color="#ff5252", width=1, dash="dash")))
            fig_price.add_hline(y=ac, line_dash="dash", line_color="#00e676",
                                annotation_text=f"Avg Cost ${ac:.2f}",
                                annotation_font_color="#00e676")
            fig_price.update_layout(
                height=400,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ccc", legend=dict(orientation="h", y=1.1),
                xaxis=dict(gridcolor="#2d3139"),
                yaxis=dict(gridcolor="#2d3139"),
                margin=dict(t=30, b=20),
            )
            st.plotly_chart(fig_price, use_container_width=True)
        else:
            st.info("No historical data available.")

    with ind_tab:
        rsi_v   = ind.get("RSI", "N/A")
        sma50_v = ind.get("SMA50", "N/A")
        sma200_v= ind.get("SMA200","N/A")
        macd_h  = ind.get("MACD_hist","N/A")
        bb_pos  = ind.get("BB_pos","N/A")
        vol_r   = ind.get("Vol_ratio","N/A")

        i1,i2,i3 = st.columns(3)

        with i1:
            st.markdown("#### RSI (14)")
            with st.expander("ℹ️ What is RSI?"):
                st.markdown(INDICATOR_EXPLANATIONS["RSI"])
            rsi_num = rsi_v if isinstance(rsi_v,(int,float)) else 50
            rsi_color = "#00e676" if rsi_num < 30 else ("#ff5252" if rsi_num > 70 else "#ffd740")
            st.markdown(
                f'<div style="font-size:28px;font-weight:900;color:{rsi_color}">{rsi_num}</div>',
                unsafe_allow_html=True)
            if   rsi_num < 30: st.success("Oversold → Bullish signal")
            elif rsi_num > 70: st.warning("Overbought → Bearish signal")
            else:              st.info("Neutral zone")

        with i2:
            st.markdown("#### MACD")
            with st.expander("ℹ️ What is MACD?"):
                st.markdown(INDICATOR_EXPLANATIONS["MACD"])
            macd_num = macd_h if isinstance(macd_h,(int,float)) else 0
            macd_c = "#00e676" if macd_num > 0 else "#ff5252"
            st.markdown(f'<div style="font-size:28px;font-weight:900;color:{macd_c}">{macd_num:+.4f}</div>', unsafe_allow_html=True)
            st.markdown(f"**Histogram:** {'Bullish' if macd_num > 0 else 'Bearish'} momentum")

        with i3:
            st.markdown("#### Bollinger Band Position")
            with st.expander("ℹ️ What are Bollinger Bands?"):
                st.markdown(INDICATOR_EXPLANATIONS["Bollinger"])
            bb_num = bb_pos if isinstance(bb_pos,(int,float)) else 0.5
            bb_c = "#00e676" if bb_num < 0.2 else ("#ff5252" if bb_num > 0.8 else "#ffd740")
            st.markdown(f'<div style="font-size:28px;font-weight:900;color:{bb_c}">{bb_num:.2f}</div>', unsafe_allow_html=True)
            if   bb_num < 0.2: st.success("Near lower band — buy zone")
            elif bb_num > 0.8: st.warning("Near upper band — sell zone")
            else:              st.info("Mid-range")

        st.markdown("---")
        st.markdown("#### Moving Averages")
        with st.expander("ℹ️ What are SMAs?"):
            st.markdown(INDICATOR_EXPLANATIONS["SMA"])

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("SMA 50",  f"${sma50_v:.2f}"  if isinstance(sma50_v,(int,float))  else "N/A")
        m2.metric("SMA 200", f"${sma200_v:.2f}" if isinstance(sma200_v,(int,float)) else "N/A")

        if isinstance(sma50_v,(int,float)):
            pct50 = (price - sma50_v)/sma50_v*100
            m3.metric("vs SMA50", f"{pct50:+.1f}%", delta=f"{'Above' if pct50>0 else 'Below'}")
        if isinstance(sma200_v,(int,float)):
            pct200 = (price - sma200_v)/sma200_v*100
            m4.metric("vs SMA200", f"{pct200:+.1f}%", delta=f"{'Above' if pct200>0 else 'Below'}")

        st.markdown("---")
        st.markdown("#### Volume")
        with st.expander("ℹ️ What does Volume tell us?"):
            st.markdown(INDICATOR_EXPLANATIONS["Volume"])
        vol_num = vol_r if isinstance(vol_r,(int,float)) else 1.0
        vol_c = "#00e676" if vol_num > 1.5 else ("#ffd740" if vol_num > 0.8 else "#888")
        st.markdown(f'<div style="font-size:24px;font-weight:700;color:{vol_c}">×{vol_num:.2f} avg volume</div>', unsafe_allow_html=True)

    with info_tab:
        name     = inf.get("longName") or inf.get("shortName", ticker)
        sector   = inf.get("sector","N/A")
        industry = inf.get("industry","N/A")
        mktcap   = inf.get("marketCap")
        pe       = inf.get("trailingPE")
        fpe      = inf.get("forwardPE")
        ps52h    = inf.get("fiftyTwoWeekHigh")
        ps52l    = inf.get("fiftyTwoWeekLow")
        target   = inf.get("targetMeanPrice")
        analys   = inf.get("recommendationMean")

        ci1,ci2,ci3,ci4 = st.columns(4)
        ci1.markdown(f"**Name:** {name}\n\n**Sector:** {sector}\n\n**Industry:** {industry}")
        ci2.markdown(f"**Market Cap:** {'${:,.1f}B'.format(mktcap/1e9) if mktcap else 'N/A'}\n\n**P/E (trailing):** {round(pe,1) if pe else 'N/A'}\n\n**P/E (forward):** {round(fpe,1) if fpe else 'N/A'}")
        ci3.markdown(f"**52W High:** {'${:.2f}'.format(ps52h) if ps52h else 'N/A'}\n\n**52W Low:** {'${:.2f}'.format(ps52l) if ps52l else 'N/A'}\n\n**Analyst target:** {'${:.2f}'.format(target) if target else 'N/A'}")
        ci4.markdown(f"**Analyst rating:** {round(analys,2) if analys else 'N/A'} (1=Strong Buy, 5=Sell)")

    # News
    st.markdown("---")
    st.markdown(f"### 📰 Latest News — {ticker}")
    if news:
        for n in news:
            link_html = f'<a href="{n["link"]}" target="_blank" style="color:#5c7cfa;text-decoration:none">{n["title"]}</a>' if n.get("link") else n["title"]
            st.markdown(
                f'<div class="news-item">{link_html}'
                f'<div style="font-size:11px;color:#888;margin-top:4px">{n.get("date","")}</div></div>',
                unsafe_allow_html=True)
    else:
        st.info("No recent news found.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — News Feed
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📰 News Feed":
    st.markdown("# 📰 Portfolio News Feed")
    tickers_to_show = st.multiselect(
        "Filter tickers", sorted(PORTFOLIO.keys()), default=list(PORTFOLIO.keys())[:10])
    if not tickers_to_show:
        st.warning("Select at least one ticker.")
        st.stop()
    for ticker in tickers_to_show:
        news = fetch_news(ticker)
        if news:
            st.markdown(f"#### {ticker}")
            for n in news[:3]:
                link_html = f'<a href="{n["link"]}" target="_blank" style="color:#5c7cfa;text-decoration:none">{n["title"]}</a>' if n.get("link") else n["title"]
                st.markdown(
                    f'<div class="news-item">{link_html}'
                    f'<div style="font-size:11px;color:#888;margin-top:4px">{n.get("date","")}</div></div>',
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — Signals Summary
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📉 Signals Summary":
    st.markdown("# 📉 Technical Signals — All Positions")

    with st.spinner("Computing signals…"):
        df = build_portfolio_summary()

    if df.empty:
        st.error("No data loaded.")
        st.stop()

    sig_filter = st.selectbox("Filter by signal",
        ["ALL","STRONG BUY","BUY","HOLD","SELL","STRONG SELL"])
    filtered = df if sig_filter == "ALL" else df[df["Signal"] == sig_filter]
    filtered = filtered.sort_values("Score", ascending=False)

    for _, row in filtered.iterrows():
        sig   = row["Signal"]
        color = SIG_COLORS.get(sig,"#aaa")
        pnl_c = pnl_color(row["P&L %"])
        ret1d_c = pnl_color(row["1D %"])
        st.markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:12px 16px;'
            f'margin-bottom:8px;border-left:4px solid {color}">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div>'
            f'<span style="font-size:18px;font-weight:700;color:#ddd">{row["Ticker"]}</span>'
            f' <span style="font-size:11px;color:#666">{row["Theme"]}</span><br>'
            f'<span style="font-size:12px;color:#aaa">${row["Price"]:.2f} &nbsp;·&nbsp; RSI: {row["RSI"]}'
            f' &nbsp;·&nbsp; 1D: <span style="color:{ret1d_c}">{row["1D %"]:+.2f}%</span>'
            f' &nbsp;·&nbsp; 1W: {row["1W %"]:+.2f}%</span>'
            f'</div>'
            f'<div style="text-align:right">'
            f'<span style="font-size:15px;font-weight:800;color:{color}">{sig}</span><br>'
            f'<span style="font-size:12px;color:{pnl_c}">{row["P&L %"]:+.1f}%</span>'
            f' <span style="font-size:11px;color:#888">Score {row["Score"]:+d}</span>'
            f'</div></div></div>',
            unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚡ Actionable Summary")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🟢 Strong Buy / Buy:**")
        buys = df[df["Signal"].isin(["BUY","STRONG BUY"])].sort_values("Score",ascending=False)
        for _, r in buys.iterrows():
            st.markdown(f"- **{r['Ticker']}** — Score {r['Score']:+d} | RSI {r['RSI']} | {r['P&L %']:+.1f}%")
    with c2:
        st.markdown("**🔴 Sell / Strong Sell:**")
        sells = df[df["Signal"].isin(["SELL","STRONG SELL"])].sort_values("Score")
        for _, r in sells.iterrows():
            st.markdown(f"- **{r['Ticker']}** — Score {r['Score']:+d} | RSI {r['RSI']} | {r['P&L %']:+.1f}%")
