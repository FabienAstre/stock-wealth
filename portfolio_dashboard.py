import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
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

# ══════════════════════════════════════════════════════════════════════════════
# STATIC MAPPINGS
# ══════════════════════════════════════════════════════════════════════════════

PORTFOLIO = {
    "AAPL.TO":   {"shares": 29.99,    "ac": 32.86},
    "ABCL":      {"shares": 159.9965, "ac": 4.2607},
    "AEHR":      {"shares": 15,       "ac": 20.56},
    "AMZN.TO":   {"shares": 90,       "ac": 8.51},
    "APLD":      {"shares": 25,       "ac": 24.72},
    "APPS.TO":   {"shares": 39.842,   "ac": 17.68},
    "ASML.TO":   {"shares": 45,       "ac": 26.20},
    "BAM.TO":    {"shares": 10.08,    "ac": 72.44},
    "BBAI":      {"shares": 60,       "ac": 7.655},
    "BEP-UN.TO": {"shares": 30.3548,  "ac": 39.07},
    "BRK.TO":    {"shares": 20,       "ac": 33.38},
    "CEGS.TO":   {"shares": 50,       "ac": 21.78},
    "CLBT":      {"shares": 40,       "ac": 18.65},
    "CMPS":      {"shares": 80,       "ac": 5.00},
    "COPP.TO":   {"shares": 17,       "ac": 51.35},
    "CRCL":      {"shares": 14,       "ac": 95.28},
    "CRWV":      {"shares": 12.9979,  "ac": 109.50},
    "CU.TO":     {"shares": 30.26,    "ac": 37.39},
    "DRUG.CN":   {"shares": 8,        "ac": 73.92},
    "ENB.TO":    {"shares": 20,       "ac": 62.53},
    "EOSE":      {"shares": 60,       "ac": 12.09},
    "HELP":      {"shares": 80,       "ac": 8.47},
    "IMVT":      {"shares": 20,       "ac": 26.48},
    "ISRG.NE":   {"shares": 25,       "ac": 26.86},
    "JOBY":      {"shares": 60,       "ac": 11.27},
    "LMT.TO":    {"shares": 30.14,    "ac": 31.03},
    "LUNR":      {"shares": 45,       "ac": 11.08},
    "MDA.TO":    {"shares": 50,       "ac": 30.38},
    "META.TO":   {"shares": 30,       "ac": 34.75},
    "MSFT.TO":   {"shares": 60.11,    "ac": 27.40},
    "NNE":       {"shares": 10,       "ac": 42.58},
    "NU":        {"shares": 40,       "ac": 14.98},
    "NVDA.TO":   {"shares": 80,       "ac": 22.96},
    "NVTS":      {"shares": 60,       "ac": 7.84},
    "NXT":       {"shares": 8,        "ac": 72.18},
    "OKLO":      {"shares": 9,        "ac": 121.28},
    "ONE.V":     {"shares": 400,      "ac": 0.8275},
    "PHOS.CN":   {"shares": 500,      "ac": 0.5943},
    "PNG.V":     {"shares": 200,      "ac": 5.41},
    "QBTS":      {"shares": 25,       "ac": 25.34},
    "RARE":      {"shares": 20,       "ac": 29.56},
    "RDDT":      {"shares": 7,        "ac": 114.74},
    "RDW":       {"shares": 50,       "ac": 10.33},
    "RGTI":      {"shares": 20,       "ac": 31.16},
    "RXRX":      {"shares": 200,      "ac": 4.61},
    "SCD.V":     {"shares": 2500,     "ac": 0.2285},
    "SOUN":      {"shares": 50,       "ac": 9.50},
    "TEM":       {"shares": 10,       "ac": 63.64},
    "TMC":       {"shares": 100,      "ac": 5.27},
    "TOI.V":     {"shares": 5,        "ac": 115.85},
    "TSLA.TO":   {"shares": 31.1267,  "ac": 35.72},
    "VEE.TO":    {"shares": 32,       "ac": 41.06},
    "VDY.TO":    {"shares": 5,        "ac": 68.97},
    "VFV.TO":    {"shares": 32.8581,  "ac": 128.76},
    "VNM":       {"shares": 40,       "ac": 17.67},
    "WELL.TO":   {"shares": 180,      "ac": 4.05},
    "WPM.TO":    {"shares": 6,        "ac": 146.66},
    "XEF.TO":    {"shares": 29.43,    "ac": 41.71},
    "XID.TO":    {"shares": 13.7926,  "ac": 49.38},
    "XSU.TO":    {"shares": 12.18,    "ac": 46.39},
    "ZCN.TO":    {"shares": 25.13,    "ac": 34.91},
    "ZJPN.TO":   {"shares": 13.21,    "ac": 45.04},
}

THEMES = {
    "MSFT.TO":   "AI Infrastructure",
    "AMZN.TO":   "AI Infrastructure",
    "META.TO":   "AI Infrastructure",
    "APLD":      "AI Infrastructure",
    "CRWV":      "AI Infrastructure",
    "BBAI":      "AI Applications",
    "SOUN":      "AI Applications",
    "TEM":       "AI Applications",
    "VFV.TO":    "Core ETFs",
    "ZCN.TO":    "Core ETFs",
    "XEF.TO":    "Core ETFs",
    "VEE.TO":    "Core ETFs",
    "XID.TO":    "Core ETFs",
    "XSU.TO":    "Core ETFs",
    "ZJPN.TO":   "Core ETFs",
    "VNM":       "Core ETFs",
    "NNE":       "Nuclear & Uranium",
    "OKLO":      "Nuclear & Uranium",
    "CEGS.TO":   "Nuclear & Uranium",
    "LUNR":      "Space, Aerospace & Defence",
    "RDW":       "Space, Aerospace & Defence",
    "MDA.TO":    "Space, Aerospace & Defence",
    "LMT.TO":    "Space, Aerospace & Defence",
    "JOBY":      "Space, Aerospace & Defence",
    "QBTS":      "Quantum Computing",
    "RGTI":      "Quantum Computing",
    "WPM.TO":    "Precious Metals & Mining",
    "COPP.TO":   "Precious Metals & Mining",
    "PNG.V":     "Precious Metals & Mining",
    "ABCL":      "Biotech & Health Tech",
    "RXRX":      "Biotech & Health Tech",
    "CMPS":      "Biotech & Health Tech",
    "RARE":      "Biotech & Health Tech",
    "IMVT":      "Biotech & Health Tech",
    "DRUG.CN":   "Biotech & Health Tech",
    "HELP":      "Biotech & Health Tech",
    "WELL.TO":   "Biotech & Health Tech",
    "ISRG.NE":   "Biotech & Health Tech",
    "NU":        "Fintech, Platforms & Compounders",
    "RDDT":      "Fintech, Platforms & Compounders",
    "BAM.TO":    "Fintech, Platforms & Compounders",
    "BRK.TO":    "Fintech, Platforms & Compounders",
    "TOI.V":     "Fintech, Platforms & Compounders",
    "CRCL":      "Fintech, Platforms & Compounders",
    "ENB.TO":    "Energy & Utilities",
    "CU.TO":     "Energy & Utilities",
    "BEP-UN.TO": "Energy & Utilities",
    "EOSE":      "Energy & Utilities",
    "NXT":       "Energy & Utilities",
    "ONE.V":     "Speculative / Micro-Cap",
    "PHOS.CN":   "Speculative / Micro-Cap",
    "SCD.V":     "Speculative / Micro-Cap",
    "TMC":       "Speculative / Micro-Cap",
    "CLBT":      "Speculative / Micro-Cap",
    "AAPL.TO":   "Tech / Software",
    "TSLA.TO":   "Tech / Software",
    "APPS.TO":   "Tech / Software",
    "NVDA.TO":   "Semiconductors",
    "ASML.TO":   "Semiconductors",
    "NVTS":      "Semiconductors",
    "AEHR":      "Semiconductors",
    "VDW.TO":    "Core ETFs",
}

THEME_COLORS = {
    "AI Infrastructure":               "#378ADD",
    "AI Applications":                 "#7F77DD",
    "Core ETFs":                       "#639922",
    "Nuclear & Uranium":               "#EF9F27",
    "Space, Aerospace & Defence":      "#5DCAA5",
    "Quantum Computing":               "#D4537E",
    "Precious Metals & Mining":        "#BA7517",
    "Biotech & Health Tech":           "#E24B4A",
    "Fintech, Platforms & Compounders":"#1D9E75",
    "Energy & Utilities":              "#888780",
    "Speculative / Micro-Cap":         "#F09595",
    "Tech / Software":                 "#AFA9EC",
    "Semiconductors":                  "#FAC775",
}

# Factor map — all 62 tickers across 6 factors
FACTORS = {
    # Growth
    "NVDA.TO":   "Growth", "MSFT.TO":  "Growth", "AMZN.TO":  "Growth",
    "META.TO":   "Growth", "ASML.TO":  "Growth", "TSLA.TO":  "Growth",
    "AAPL.TO":   "Growth", "CRWV":     "Growth", "APLD":     "Growth",
    "RDDT":      "Growth", "NU":       "Growth",  "TOI.V":    "Growth",
    "APPS.TO":   "Growth", "MDA.TO":   "Growth",  "WELL.TO":  "Growth",
    "ISRG.NE":   "Growth", "BAM.TO":   "Growth",
    # Speculative
    "BBAI":      "Speculative", "SOUN":   "Speculative", "TEM":    "Speculative",
    "LUNR":      "Speculative", "RDW":    "Speculative", "JOBY":   "Speculative",
    "QBTS":      "Speculative", "RGTI":   "Speculative", "NVTS":   "Speculative",
    "AEHR":      "Speculative", "NNE":    "Speculative", "OKLO":   "Speculative",
    "ABCL":      "Speculative", "RXRX":   "Speculative", "CMPS":   "Speculative",
    "RARE":      "Speculative", "IMVT":   "Speculative", "DRUG.CN":"Speculative",
    "HELP":      "Speculative", "EOSE":   "Speculative", "CRCL":   "Speculative",
    "ONE.V":     "Speculative", "PHOS.CN":"Speculative", "SCD.V":  "Speculative",
    "TMC":       "Speculative", "CLBT":   "Speculative", "PNG.V":  "Speculative",
    # Income
    "ENB.TO":    "Income", "CU.TO":    "Income", "BEP-UN.TO":"Income",
    "WPM.TO":    "Income",
    # Defensive
    "LMT.TO":    "Defensive", "BRK.TO": "Defensive",
    # Commodity
    "COPP.TO":   "Commodity", "NXT":    "Commodity",
    # Index / Diversified
    "VFV.TO":    "Index / Diversified", "ZCN.TO":  "Index / Diversified",
    "XEF.TO":    "Index / Diversified", "VEE.TO":  "Index / Diversified",
    "XID.TO":    "Index / Diversified", "XSU.TO":  "Index / Diversified",
    "ZJPN.TO":   "Index / Diversified", "VNM":     "Index / Diversified",
    "CEGS.TO":   "Index / Diversified", "VDY.TO":   "Index / Diversified"
}

FACTOR_COLORS = {
    "Growth":              "#378ADD",
    "Speculative":         "#E24B4A",
    "Income":              "#639922",
    "Defensive":           "#5DCAA5",
    "Commodity":           "#BA7517",
    "Index / Diversified": "#888780",
}

BENCHMARK = "VFV.TO"

SIG_COLORS = {
    "STRONG BUY":  "#00e676",
    "BUY":         "#69f0ae",
    "HOLD":        "#ffd740",
    "SELL":        "#ff5252",
    "STRONG SELL": "#ff1744",
}

INDICATOR_EXPLANATIONS = {
    "RSI": """**RSI (Relative Strength Index)** — A temperature gauge for momentum.
- **Below 30** → Deeply oversold. Stock has been beaten down hard — potential buying opportunity.
- **30–45** → Cooling off. Mild bullish lean.
- **45–55** → Neutral. No strong momentum either way.
- **55–70** → Warming up. Mild caution — may be getting stretched.
- **Above 70** → Overbought. Stock has been running hard — due for a rest or pullback.

*Rule of thumb: buy fear (low RSI), be cautious on euphoria (high RSI).*""",

    "MACD": """**MACD (Moving Average Convergence Divergence)** — Measures whether short-term momentum is accelerating or fading vs. the medium term.
- The **histogram** is key: positive bars = buyers in control, negative bars = sellers in control.
- **Bullish crossover**: histogram flips from negative → positive. Strong momentum shift upward.
- **Bearish crossover**: histogram flips from positive → negative. Momentum breaking down.
- Tall bars = strong momentum. Shrinking bars = momentum fading even if still in the same direction.

*Best used as a timing signal, not standalone.*""",

    "SMA": """**SMA 50 / SMA 200 (Simple Moving Averages)** — The structural trend backbone.
- **Price above SMA50** → Short-term trend is up. Bulls in control near-term.
- **Price below SMA50** → Short-term trend is down. Caution.
- **SMA50 above SMA200** → The "Golden Cross." Classic long-term bullish signal. Institutions watch this.
- **SMA50 below SMA200** → The "Death Cross." Long-term bearish signal. Often precedes further weakness.

*The further price is from SMA200, the more stretched the move — in either direction.*""",

    "Bollinger": """**Bollinger Bands** — Shows where price sits within its recent volatility range.
- Calculated as 2 standard deviations above/below the 20-day moving average.
- **Position 0.0** = price at the bottom of the band. Often a bounce setup.
- **Position 0.5** = price at the midpoint. Neutral.
- **Position 1.0** = price at the top of the band. Often a pullback setup.
- During strong trends, price can "walk the band" near 0.8–1.0 for extended periods.

*Low BB position + oversold RSI together = high-conviction mean-reversion setup.*""",

    "Volume": """**Volume Ratio** — Compares today's volume to the 20-day average.
- **Ratio > 1.5** = Significantly above-average volume. Big moves on high volume are more meaningful.
- **Ratio < 0.5** = Low volume. Price moves on thin volume are less reliable.
- High volume on an up day = institutional buying. High volume on a down day = distribution (selling).

*Volume confirms or questions price moves. It's the conviction indicator.*""",

    "Beta": """**Portfolio Beta** — How much your portfolio swings relative to the market (S&P 500 via VFV.TO).
- **Beta = 1.0** → Moves in line with the market.
- **Beta = 1.5** → If the market drops 10%, your portfolio historically drops ~15%.
- **Beta = 0.5** → Half the market's volatility. More defensive.
- **Negative beta** → Moves opposite to the market (rare — gold, inverse ETFs).

*A high-beta portfolio generates outsized gains in bull markets and outsized losses in bear markets. Know your number.*""",

    "Drawdown": """**Drawdown from 52-Week High** — How far a position has fallen from its peak.
- **0% to -10%** → Normal fluctuation.
- **-10% to -25%** → Correction territory. Worth reviewing the thesis.
- **-25% to -50%** → Deep drawdown. Requires strong conviction to hold or add.
- **Below -50%** → The stock needs to double just to get back to where it was.

*Drawdown is the most honest measure of pain. It strips away the "but it was higher" excuse.*""",

    "Sharpe": """**Sharpe Ratio** — Measures return per unit of risk (volatility). The quality of return.
- **Above 1.0** → Good. You're being rewarded adequately for the risk taken.
- **Above 2.0** → Excellent. Strong risk-adjusted return.
- **Below 0** → Negative. You're taking risk for a negative return.
- **0 to 1.0** → Marginal. Mediocre risk/reward.

*Two stocks both up 30%: the one with Sharpe 2.0 got there more smoothly than the one with Sharpe 0.5. The smoother ride is more sustainable and easier to hold.*""",

    "Correlation": """**Correlation Matrix** — Shows how much your positions move together.
- **+1.0** → Perfect correlation. They move in lockstep. No diversification benefit.
- **0.0** → No relationship. True diversification.
- **-1.0** → Perfect inverse. One zigs when the other zags. Maximum hedge.
- Most stocks show 0.3–0.7 correlation, especially within the same sector.

*High correlation within a theme is expected. The real risk is when ALL your themes correlate during a crash — which they tend to do.*""",

    "MaxDrawdown": """**Max Drawdown (Portfolio Level)** — The largest peak-to-trough decline your total portfolio experienced over the past year.
- This is the real pain metric. Not average loss — the worst single decline from any peak.
- A max drawdown of -30% means at some point this year, you were down 30% from your recent high.
- To recover from -50% max drawdown, your portfolio needs to gain +100%.

*This number tells you what you actually lived through — not what the average day felt like.*""",
}

# ══════════════════════════════════════════════════════════════════════════════
# DATA LAYER — Central Cache
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def fetch_ticker_data(ticker: str) -> dict:
    """Fetch single ticker — low-level, used only by fetch_all_data."""
    try:
        t       = yf.Ticker(ticker)
        hist_1y = t.history(period="1y", interval="1d")
        hist_1d = t.history(period="1d", interval="5m")
        price   = None
        try:
            inf   = t.info or {}
            price = (inf.get("currentPrice")
                     or inf.get("regularMarketPrice")
                     or inf.get("previousClose"))
        except Exception:
            inf = {}
        if price is None and not hist_1y.empty:
            price = float(hist_1y["Close"].squeeze().iloc[-1])
        if price is None:
            try:
                price = t.fast_info.get("last_price") or t.fast_info.get("lastPrice")
            except Exception:
                pass
        sig = _compute_signals(hist_1y)
        return {
            "ticker":     ticker,
            "price":      price,
            "info":       inf,
            "hist_1y":    hist_1y,
            "hist_1d":    hist_1d,
            "signal":     sig["signal"],
            "score":      sig["score"],
            "indicators": sig["details"],
        }
    except Exception as e:
        return {
            "ticker": ticker, "price": None, "error": str(e),
            "signal": "HOLD", "score": 0, "indicators": {}, "info": {},
            "hist_1y": pd.DataFrame(), "hist_1d": pd.DataFrame(),
        }


@st.cache_data(ttl=300)
def fetch_all_data() -> dict:
    """Central cache — fetch all tickers once, reuse everywhere."""
    return {t: fetch_ticker_data(t) for t in PORTFOLIO}


@st.cache_data(ttl=600)
def fetch_news(ticker: str) -> list:
    try:
        t    = yf.Ticker(ticker)
        news = t.news or []
        items = []
        for n in news[:5]:
            ct    = n.get("content", {})
            title = ct.get("title") or n.get("title", "")
            link  = ct.get("canonicalUrl", {}).get("url") or n.get("link", "")
            pub   = ct.get("pubDate") or ""
            if pub:
                try:
                    pub = datetime.fromisoformat(pub.replace("Z", "")).strftime("%b %d, %Y")
                except Exception:
                    pass
            if title:
                items.append({"title": title, "link": link, "date": pub})
        return items
    except Exception:
        return []


# ── Signal engine (weighted) ───────────────────────────────────────────────────
def _compute_signals(hist: pd.DataFrame) -> dict:
    if hist is None or len(hist) < 30:
        return {"signal": "HOLD", "score": 0, "details": {}}

    close   = hist["Close"].squeeze()
    signals = {}
    score   = 0.0

    # RSI  (weight ×2)
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = 100 - (100 / (1 + rs))
    rsi_v = float(rsi.iloc[-1]) if not rsi.empty else 50
    signals["RSI"] = round(rsi_v, 1)
    rsi_raw = 0
    if   rsi_v < 30: rsi_raw =  2
    elif rsi_v < 45: rsi_raw =  1
    elif rsi_v > 70: rsi_raw = -2
    elif rsi_v > 55: rsi_raw = -1
    score += 2 * rsi_raw

    # MACD  (weight ×3)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd  = ema12 - ema26
    sig_line  = macd.ewm(span=9, adjust=False).mean()
    macd_hist = macd - sig_line
    signals["MACD_hist"] = round(float(macd_hist.iloc[-1]), 4) if not macd_hist.empty else 0
    macd_raw = 0
    if len(macd_hist) >= 2:
        if   macd_hist.iloc[-1] > 0 and macd_hist.iloc[-2] <= 0: macd_raw =  2
        elif macd_hist.iloc[-1] < 0 and macd_hist.iloc[-2] >= 0: macd_raw = -2
        elif macd_hist.iloc[-1] > 0:                              macd_raw =  1
        else:                                                      macd_raw = -1
    score += 3 * macd_raw

    # SMA trend  (weight ×2)
    sma50  = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    price  = float(close.iloc[-1])
    s50    = float(sma50.iloc[-1])  if not sma50.empty  else price
    s200   = float(sma200.iloc[-1]) if not sma200.empty else price
    signals["SMA50"]  = round(s50,  2)
    signals["SMA200"] = round(s200, 2)
    signals["Price"]  = round(price, 2)
    trend_raw = 0
    if price > s50:  trend_raw += 1
    else:            trend_raw -= 1
    if price > s200: trend_raw += 1
    else:            trend_raw -= 1
    if s50 > s200:   trend_raw += 1
    else:            trend_raw -= 1
    score += 2 * trend_raw

    # Bollinger  (weight ×1)
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    upper = sma20 + 2 * std20
    lower = sma20 - 2 * std20
    bb_pos = (price - float(lower.iloc[-1])) / (float(upper.iloc[-1]) - float(lower.iloc[-1]) + 1e-9)
    signals["BB_pos"] = round(bb_pos, 2)
    bb_raw = 0
    if   bb_pos < 0.2: bb_raw =  1
    elif bb_pos > 0.8: bb_raw = -1
    score += 1 * bb_raw

    # Volume  (weight ×1)
    if "Volume" in hist.columns:
        vol      = hist["Volume"].squeeze()
        avg_vol  = float(vol.rolling(20).mean().iloc[-1])
        last_vol = float(vol.iloc[-1])
        if avg_vol > 0:
            vol_ratio = last_vol / avg_vol
            signals["Vol_ratio"] = round(vol_ratio, 2)
            if vol_ratio > 1.5 and price > float(close.iloc[-2]):
                score += 1

    # 52W stats
    high_52w = float(close.rolling(252).max().iloc[-1]) if len(close) >= 20 else price
    low_52w  = float(close.rolling(252).min().iloc[-1]) if len(close) >= 20 else price
    signals["High_52W"] = round(high_52w, 2)
    signals["Low_52W"]  = round(low_52w,  2)
    signals["Drawdown"] = round((price - high_52w) / high_52w * 100, 1) if high_52w > 0 else 0

    # Daily / weekly returns
    signals["Return_1D"] = round((float(close.iloc[-1]) / float(close.iloc[-2]) - 1) * 100, 2) if len(close) >= 2 else 0.0
    signals["Return_1W"] = round((float(close.iloc[-1]) / float(close.iloc[-6]) - 1) * 100, 2) if len(close) >= 6 else signals["Return_1D"]

    # Sharpe (annualised, 1Y)
    ret_series = close.pct_change().dropna()
    if len(ret_series) > 20:
        sharpe = (ret_series.mean() / ret_series.std()) * np.sqrt(252)
        signals["Sharpe"] = round(float(sharpe), 2)
    else:
        signals["Sharpe"] = 0.0

    # Verdict
    s = int(round(score))
    if   s >= 7:  verdict = "STRONG BUY"
    elif s >= 3:  verdict = "BUY"
    elif s <= -7: verdict = "STRONG SELL"
    elif s <= -3: verdict = "SELL"
    else:         verdict = "HOLD"

    return {"signal": verdict, "score": s, "details": signals}


# ── Portfolio-level analytics ──────────────────────────────────────────────────
@st.cache_data(ttl=300)
def build_portfolio_summary() -> pd.DataFrame:
    DATA = fetch_all_data()
    rows = []
    for ticker, pos in PORTFOLIO.items():
        d     = DATA[ticker]
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
        breakeven_dist = ((price - ac) / ac * 100) if ac else 0
        rows.append({
            "Ticker":         ticker,
            "Theme":          THEMES.get(ticker, "Other"),
            "Factor":         FACTORS.get(ticker, "Other"),
            "Price":          price,
            "Shares":         shares,
            "AC":             ac,
            "Mkt Value":      cv,
            "Cost":           cb,
            "P&L $":          pnl,
            "P&L %":          pnl_p,
            "Breakeven %":    breakeven_dist,
            "1D %":           ind.get("Return_1D", 0),
            "1W %":           ind.get("Return_1W", 0),
            "Signal":         d.get("signal", "HOLD"),
            "Score":          d.get("score", 0),
            "RSI":            ind.get("RSI", 50),
            "SMA50":          ind.get("SMA50", price),
            "SMA200":         ind.get("SMA200", price),
            "Drawdown":       ind.get("Drawdown", 0),
            "High_52W":       ind.get("High_52W", price),
            "Sharpe":         ind.get("Sharpe", 0),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=300)
def build_equity_curve() -> pd.DataFrame:
    """Portfolio daily value curve + benchmark, normalised to 1.0."""
    DATA  = fetch_all_data()
    curves = []
    for ticker, pos in PORTFOLIO.items():
        d    = DATA[ticker]
        hist = d.get("hist_1y")
        if hist is None or hist.empty:
            continue
        s = hist["Close"].squeeze() * pos["shares"]
        s.name = ticker
        curves.append(s)
    if not curves:
        return pd.DataFrame()
    port = pd.concat(curves, axis=1).ffill().dropna(how="all")
    port_total = port.sum(axis=1).dropna()

    # Benchmark
    bench_d    = DATA.get(BENCHMARK, {})
    bench_hist = bench_d.get("hist_1y")
    if bench_hist is not None and not bench_hist.empty:
        bench = bench_hist["Close"].squeeze()
        combined = pd.concat([port_total, bench], axis=1).dropna()
        combined.columns = ["Portfolio", "Benchmark"]
        combined["Portfolio"]  = combined["Portfolio"]  / combined["Portfolio"].iloc[0]
        combined["Benchmark"]  = combined["Benchmark"]  / combined["Benchmark"].iloc[0]
    else:
        combined = pd.DataFrame({"Portfolio": port_total / port_total.iloc[0]})
    return combined


def max_drawdown(series: pd.Series) -> float:
    roll_max = series.cummax()
    dd       = (series - roll_max) / roll_max
    return float(dd.min()) * 100


@st.cache_data(ttl=600)
def build_correlation_matrix() -> pd.DataFrame:
    DATA   = fetch_all_data()
    closes = {}
    for ticker in PORTFOLIO:
        d = DATA[ticker]
        h = d.get("hist_1y")
        if h is not None and not h.empty:
            s = h["Close"].squeeze()
            s.name = ticker
            closes[ticker] = s
    if len(closes) < 2:
        return pd.DataFrame()
    df = pd.DataFrame(closes).ffill().dropna()
    return df.pct_change().dropna().corr()


@st.cache_data(ttl=600)
def compute_portfolio_beta() -> float | None:
    DATA       = fetch_all_data()
    bench_hist = DATA.get(BENCHMARK, {}).get("hist_1y")
    if bench_hist is None or bench_hist.empty:
        return None
    bench_ret = bench_hist["Close"].squeeze().pct_change().dropna()
    weighted_beta = 0.0
    total_val     = 0.0
    for ticker, pos in PORTFOLIO.items():
        d     = DATA[ticker]
        price = d.get("price")
        if price is None:
            continue
        val  = price * pos["shares"]
        hist = d.get("hist_1y")
        if hist is None or hist.empty:
            continue
        tk_ret   = hist["Close"].squeeze().pct_change().dropna()
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


@st.cache_data(ttl=300)
def compute_portfolio_sharpe() -> float | None:
    eq = build_equity_curve()
    if eq.empty or "Portfolio" not in eq.columns:
        return None
    ret = eq["Portfolio"].pct_change().dropna()
    if len(ret) < 20 or ret.std() == 0:
        return None
    return round(float(ret.mean() / ret.std() * np.sqrt(252)), 2)


# ── UI helpers ─────────────────────────────────────────────────────────────────
def pnl_color(v: float) -> str:
    return "#00e676" if v >= 0 else "#ff5252"


def dark_card(content_html: str, border_color: str = "#3d5afe") -> str:
    return (
        f'<div style="background:#1c1f26;border-radius:10px;padding:14px 16px;'
        f'border-left:4px solid {border_color};margin-bottom:8px">'
        f'{content_html}</div>'
    )


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
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
    port_sharpe = compute_portfolio_sharpe()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Portfolio Value",   f"${total_val:,.0f}")
    c2.metric("Cost Basis",        f"${total_cost:,.0f}")
    c3.metric("Total P&L",         f"${total_pnl:,.0f}", delta=f"{total_pnl_p:+.1f}%")
    c4.metric("Today's P&L (est)", f"${daily_pnl:+,.0f}")
    c5.metric("Positions",         f"{len(df)} / {len(PORTFOLIO)}")
    c6.metric("Portfolio Sharpe",  f"{port_sharpe:.2f}" if port_sharpe else "N/A")

    # Signal distribution
    st.markdown("---")
    st.markdown("### 🚦 Signal Distribution")
    sig_counts = df["Signal"].value_counts()
    cols = st.columns(5)
    for i, (sig, color) in enumerate([
        ("STRONG BUY", "#00e676"), ("BUY", "#69f0ae"),
        ("HOLD", "#ffd740"), ("SELL", "#ff5252"), ("STRONG SELL", "#ff1744"),
    ]):
        cnt = sig_counts.get(sig, 0)
        cols[i].markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:12px;'
            f'text-align:center;border-top:3px solid {color}">'
            f'<div style="font-size:22px;font-weight:700;color:{color}">{cnt}</div>'
            f'<div style="font-size:11px;color:#aaa">{sig}</div></div>',
            unsafe_allow_html=True)

    # Main table
    st.markdown("---")
    st.markdown("### 📋 All Positions")
    disp = df[[
        "Ticker", "Theme", "Factor", "Price", "Shares","AC",
        "Mkt Value", "P&L $", "P&L %", "Breakeven %",
        "1D %", "1W %", "Sharpe", "Signal", "RSI",
    ]].copy().sort_values("Mkt Value", ascending=False)

    disp["Mkt Value"]   = disp["Mkt Value"].map("${:,.0f}".format)
    disp["P&L $"]       = disp["P&L $"].map("${:,.0f}".format)
    disp["P&L %"]       = disp["P&L %"].map("{:+.1f}%".format)
    disp["Breakeven %"] = disp["Breakeven %"].map("{:+.1f}%".format)
    disp["1D %"]        = disp["1D %"].map("{:+.2f}%".format)
    disp["1W %"]        = disp["1W %"].map("{:+.2f}%".format)
    disp["Price"]       = disp["Price"].map("${:.2f}".format)
    disp["AC"]          = disp["AC"].map("${:.2f}".format)
    disp["Shares"]      = disp["Shares"].map("{:.2f}".format)
    disp["Sharpe"]      = disp["Sharpe"].map("{:.2f}".format)
    st.dataframe(disp, use_container_width=True, height=700)

    # Winners / Losers
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏆 Top 5 Winners")
        top5 = df.nlargest(5, "P&L %")[["Ticker", "P&L %", "P&L $", "1D %", "Sharpe", "Signal"]]
        top5["P&L %"] = top5["P&L %"].map("{:+.1f}%".format)
        top5["P&L $"] = top5["P&L $"].map("${:,.0f}".format)
        top5["1D %"]  = top5["1D %"].map("{:+.2f}%".format)
        top5["Sharpe"]= top5["Sharpe"].map("{:.2f}".format)
        st.dataframe(top5, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("### ⚠️ Top 5 Losers")
        bot5 = df.nsmallest(5, "P&L %")[["Ticker", "P&L %", "P&L $", "1D %", "Sharpe", "Signal"]]
        bot5["P&L %"] = bot5["P&L %"].map("{:+.1f}%".format)
        bot5["P&L $"] = bot5["P&L $"].map("${:,.0f}".format)
        bot5["1D %"]  = bot5["1D %"].map("{:+.2f}%".format)
        bot5["Sharpe"]= bot5["Sharpe"].map("{:.2f}".format)
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

    total_val = df["Mkt Value"].sum()
    df["Weight %"] = df["Mkt Value"] / total_val * 100

    # ── Theme vs Factor donuts ──
    st.markdown("### 🍩 Portfolio Composition")
    dc1, dc2 = st.columns(2)

    # Theme donut
    theme_df = df.groupby("Theme").agg(Value=("Mkt Value", "sum"), Cost=("Cost", "sum")).reset_index()
    theme_df["Weight %"] = theme_df["Value"] / theme_df["Value"].sum() * 100
    theme_df["P&L %"]    = (theme_df["Value"] - theme_df["Cost"]) / theme_df["Cost"] * 100
    theme_df["Concentration Risk"] = theme_df["Weight %"].apply(
        lambda x: "HIGH" if x > 25 else ("MEDIUM" if x > 15 else "LOW"))
    theme_df = theme_df.sort_values("Value", ascending=False)

    with dc1:
        st.markdown("#### By Theme")
        fig_t = px.pie(
            theme_df, values="Value", names="Theme",
            color="Theme", color_discrete_map=THEME_COLORS, hole=0.48,
        )
        fig_t.update_traces(
            textposition="outside", textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
        )
        fig_t.update_layout(
            showlegend=False, height=420,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=20, b=20, l=10, r=10),
        )
        st.plotly_chart(fig_t, use_container_width=True)

    # Factor donut
    factor_df = df.groupby("Factor").agg(Value=("Mkt Value", "sum")).reset_index()
    factor_df["Weight %"] = factor_df["Value"] / factor_df["Value"].sum() * 100
    factor_df = factor_df.sort_values("Value", ascending=False)

    with dc2:
        st.markdown("#### By Factor")
        fig_f = px.pie(
            factor_df, values="Value", names="Factor",
            color="Factor", color_discrete_map=FACTOR_COLORS, hole=0.48,
        )
        fig_f.update_traces(
            textposition="outside", textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
        )
        fig_f.update_layout(
            showlegend=False, height=420,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", margin=dict(t=20, b=20, l=10, r=10),
        )
        st.plotly_chart(fig_f, use_container_width=True)

    # Concentration warnings
    high_conc = theme_df[theme_df["Concentration Risk"] == "HIGH"]
    med_conc  = theme_df[theme_df["Concentration Risk"] == "MEDIUM"]
    if not high_conc.empty:
        for _, r in high_conc.iterrows():
            st.warning(f"⚠️ HIGH concentration: **{r['Theme']}** = {r['Weight %']:.1f}% of portfolio (>{25}% threshold)")
    if not med_conc.empty:
        for _, r in med_conc.iterrows():
            st.info(f"ℹ️ MEDIUM concentration: **{r['Theme']}** = {r['Weight %']:.1f}%")

    # Theme summary table
    st.markdown("---")
    st.markdown("### 📋 Theme Summary")
    th_disp = theme_df[["Theme", "Weight %", "P&L %", "Value", "Concentration Risk"]].copy()
    th_disp["Value"]    = th_disp["Value"].map("${:,.0f}".format)
    th_disp["Weight %"] = th_disp["Weight %"].map("{:.1f}%".format)
    th_disp["P&L %"]    = th_disp["P&L %"].map("{:+.1f}%".format)
    st.dataframe(th_disp, use_container_width=True, hide_index=True)

    # ── Treemap with separator lines ──
    st.markdown("---")
    st.markdown("### 🗺️ Position Sizing Treemap")
    st.caption("Size = market value · Color = theme · Hover for full details")

    fig_tree = px.treemap(
        df,
        path=["Theme", "Ticker"],
        values="Mkt Value",
        color="Theme",
        color_discrete_map=THEME_COLORS,
        custom_data=["P&L %", "Signal", "Weight %", "1D %", "Sharpe", "Factor"],
    )
    fig_tree.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Market Value: $%{value:,.0f}<br>"
            "Weight: %{customdata[2]:.1f}%<br>"
            "P&L: %{customdata[0]:+.1f}%<br>"
            "1D: %{customdata[3]:+.2f}%<br>"
            "Sharpe: %{customdata[4]:.2f}<br>"
            "Signal: %{customdata[1]}<br>"
            "Factor: %{customdata[5]}<extra></extra>"
        ),
        textinfo="label",
        # Separator lines between tiles
        marker=dict(
            line=dict(width=2, color="#0e1117"),
            pad=dict(t=20, l=3, r=3, b=3),
        ),
    )
    fig_tree.update_layout(
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ccc",
        margin=dict(t=10, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_tree, use_container_width=True)

    # ── Cost basis progress bars ──
    st.markdown("---")
    st.markdown("### 📏 Cost Basis — Distance from Breakeven")
    st.caption("Green = in profit · Red = underwater · Bar width = magnitude relative to portfolio range")

    df_sorted  = df.sort_values("P&L %", ascending=False)
    max_abs    = max(df["P&L %"].abs().max(), 1)

    for _, row in df_sorted.iterrows():
        pct     = row["P&L %"]
        color   = "#00e676" if pct >= 0 else "#ff5252"
        bar_w   = min(abs(pct) / max_abs * 100, 100)
        label   = f"{pct:+.1f}%"
        theme_c = THEME_COLORS.get(row["Theme"], "#aaa")
        sharpe_c = "#00e676" if row["Sharpe"] > 1 else ("#ffd740" if row["Sharpe"] > 0 else "#ff5252")

        st.markdown(
            f'<div style="display:flex;align-items:center;margin-bottom:5px;gap:8px">'
            f'<div style="width:80px;font-size:12px;font-weight:700;color:#ddd">{row["Ticker"]}</div>'
            f'<div style="width:100px;font-size:10px;color:{theme_c};white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{row["Theme"][:16]}</div>'
            f'<div style="flex:1;background:#2a2d35;border-radius:4px;height:14px">'
            f'<div style="width:{bar_w}%;background:{color};height:100%;border-radius:4px;opacity:0.85"></div>'
            f'</div>'
            f'<div style="width:58px;font-size:12px;font-weight:700;color:{color};text-align:right">{label}</div>'
            f'<div style="width:72px;font-size:11px;color:#888;text-align:right">${row["Price"]:.2f}/${row["AC"]:.2f}</div>'
            f'<div style="width:60px;font-size:11px;color:{sharpe_c};text-align:right">S:{row["Sharpe"]:.2f}</div>'
            f'</div>',
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Risk & Alerts
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🚨 Risk & Alerts":
    st.markdown("# 🚨 Risk & Alerts")

    with st.spinner("Computing risk metrics…"):
        df    = build_portfolio_summary()
        beta  = compute_portfolio_beta()
        eq    = build_equity_curve()
        psharpe = compute_portfolio_sharpe()

    if df.empty:
        st.error("No data loaded.")
        st.stop()

    port_mdd = max_drawdown(eq["Portfolio"]) if not eq.empty and "Portfolio" in eq.columns else None

    # ── Top risk metrics ──
    st.markdown("### 📐 Portfolio Risk Metrics")
    rm1, rm2, rm3, rm4 = st.columns(4)

    if beta is not None:
        beta_c = "#ff5252" if beta > 1.5 else ("#ffd740" if beta > 1.0 else "#00e676")
        rm1.markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:14px;text-align:center;border-top:3px solid {beta_c}">'
            f'<div style="font-size:11px;color:#aaa">PORTFOLIO BETA</div>'
            f'<div style="font-size:30px;font-weight:900;color:{beta_c}">{beta}</div>'
            f'<div style="font-size:11px;color:#aaa">vs VFV.TO (S&P 500)</div></div>',
            unsafe_allow_html=True)
    if port_mdd is not None:
        mdd_c = "#ff1744" if port_mdd < -30 else ("#ff5252" if port_mdd < -15 else "#ffd740")
        rm2.markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:14px;text-align:center;border-top:3px solid {mdd_c}">'
            f'<div style="font-size:11px;color:#aaa">MAX DRAWDOWN (1Y)</div>'
            f'<div style="font-size:30px;font-weight:900;color:{mdd_c}">{port_mdd:.1f}%</div>'
            f'<div style="font-size:11px;color:#aaa">Worst peak-to-trough</div></div>',
            unsafe_allow_html=True)
    if psharpe is not None:
        sharpe_c = "#00e676" if psharpe > 1 else ("#ffd740" if psharpe > 0 else "#ff5252")
        rm3.markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:14px;text-align:center;border-top:3px solid {sharpe_c}">'
            f'<div style="font-size:11px;color:#aaa">PORTFOLIO SHARPE</div>'
            f'<div style="font-size:30px;font-weight:900;color:{sharpe_c}">{psharpe}</div>'
            f'<div style="font-size:11px;color:#aaa">Return per unit of risk</div></div>',
            unsafe_allow_html=True)
    if beta is not None:
        rm4.markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:14px;text-align:center;border-top:3px solid #3d5afe">'
            f'<div style="font-size:11px;color:#aaa">IF MARKET DROPS 10%</div>'
            f'<div style="font-size:30px;font-weight:900;color:#ff5252">-{beta*10:.1f}%</div>'
            f'<div style="font-size:11px;color:#aaa">Expected portfolio move</div></div>',
            unsafe_allow_html=True)

    with st.expander("ℹ️ Understanding Beta, Max Drawdown & Sharpe"):
        st.markdown(INDICATOR_EXPLANATIONS["Beta"])
        st.markdown("---")
        st.markdown(INDICATOR_EXPLANATIONS["MaxDrawdown"])
        st.markdown("---")
        st.markdown(INDICATOR_EXPLANATIONS["Sharpe"])

    # ── Equity curve vs benchmark ──
    st.markdown("---")
    st.markdown("### 📈 Portfolio vs Benchmark (Normalised, 1Y)")
    if not eq.empty:
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=eq.index, y=eq["Portfolio"],
            name="My Portfolio", line=dict(color="#5c7cfa", width=2.5)))
        if "Benchmark" in eq.columns:
            fig_eq.add_trace(go.Scatter(
                x=eq.index, y=eq["Benchmark"],
                name=f"Benchmark ({BENCHMARK})", line=dict(color="#ffd740", width=1.5, dash="dot")))
        if port_mdd is not None:
            fig_eq.add_annotation(
                x=eq.index[-1], y=eq["Portfolio"].iloc[-1],
                text=f"Max DD: {port_mdd:.1f}%",
                showarrow=False, font=dict(color="#ff5252", size=11),
                xanchor="right", yanchor="bottom",
            )
        fig_eq.update_layout(
            height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccc", legend=dict(orientation="h", y=1.08),
            xaxis=dict(gridcolor="#2d3139"),
            yaxis=dict(gridcolor="#2d3139", tickformat=".0%"),
            margin=dict(t=30, b=20),
            hovermode="x unified",
        )
        st.plotly_chart(fig_eq, use_container_width=True)
        st.caption("Both series start at 1.0 on the first trading day of the 1-year window")
    else:
        st.warning("Not enough data to build equity curve.")

    # ── Factor exposure bar ──
    st.markdown("---")
    st.markdown("### 🧩 Factor Exposure")
    factor_df = df.groupby("Factor").agg(Value=("Mkt Value", "sum")).reset_index()
    factor_df["Weight %"] = factor_df["Value"] / factor_df["Value"].sum() * 100
    factor_df = factor_df.sort_values("Weight %", ascending=True)

    fig_fac = px.bar(
        factor_df, x="Weight %", y="Factor", orientation="h",
        color="Factor", color_discrete_map=FACTOR_COLORS,
        text=factor_df["Weight %"].map("{:.1f}%".format),
    )
    fig_fac.update_traces(textposition="outside")
    fig_fac.update_layout(
        height=320, showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ccc", margin=dict(t=10, b=10, l=10, r=60),
        xaxis=dict(gridcolor="#2d3139"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_fac, use_container_width=True)

    # ── Position sizing alerts ──
    st.markdown("---")
    st.markdown("### ⚖️ Position Sizing Alerts")
    total_val = df["Mkt Value"].sum()
    df["Weight %"] = df["Mkt Value"] / total_val * 100

    overweight  = df[df["Weight %"] > 5].sort_values("Weight %", ascending=False)
    underweight = df[df["Weight %"] < 0.3].sort_values("Weight %")

    ps1, ps2 = st.columns(2)
    with ps1:
        st.markdown("**🔴 Overweight (>5% of portfolio)**")
        if not overweight.empty:
            for _, r in overweight.iterrows():
                w_c = "#ff1744" if r["Weight %"] > 8 else "#ff5252"
                st.markdown(
                    f'<div style="background:#1c1f26;border-left:3px solid {w_c};'
                    f'border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:5px">'
                    f'<b style="color:{w_c}">{r["Ticker"]}</b>'
                    f' <span style="color:#aaa;font-size:12px">— {r["Weight %"]:.1f}% '
                    f'(${r["Mkt Value"]:,.0f})</span>'
                    f'<div style="font-size:11px;color:#666">{r["Theme"]}</div></div>',
                    unsafe_allow_html=True)
        else:
            st.success("No overweight positions.")
    with ps2:
        st.markdown("**🟡 Underweight (<0.3% of portfolio)**")
        if not underweight.empty:
            for _, r in underweight.iterrows():
                st.markdown(
                    f'<div style="background:#1c1f26;border-left:3px solid #ffd740;'
                    f'border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:5px">'
                    f'<b style="color:#ffd740">{r["Ticker"]}</b>'
                    f' <span style="color:#aaa;font-size:12px">— {r["Weight %"]:.2f}% '
                    f'(${r["Mkt Value"]:,.0f})</span>'
                    f'<div style="font-size:11px;color:#666">{r["Theme"]}</div></div>',
                    unsafe_allow_html=True)
        else:
            st.success("No underweight positions.")

    # ── Technical alert flags ──
    st.markdown("---")
    st.markdown("### 🚦 Technical Alert Flags")

    alerts = []
    for _, row in df.iterrows():
        rsi, price, s50 = row["RSI"], row["Price"], row["SMA50"]
        dd, tk          = row["Drawdown"], row["Ticker"]

        if isinstance(rsi, (int, float)):
            if rsi < 25:
                alerts.append({"type": "RSI Oversold",   "ticker": tk, "value": f"RSI {rsi}",
                                "msg": "Deeply oversold — potential entry",      "color": "#00e676", "grp": 0})
            elif rsi > 75:
                alerts.append({"type": "RSI Overbought", "ticker": tk, "value": f"RSI {rsi}",
                                "msg": "Overbought — consider trimming",          "color": "#ff5252", "grp": 0})

        if isinstance(price, (int, float)) and isinstance(s50, (int, float)) and s50 > 0:
            pct50 = (price - s50) / s50 * 100
            if -2 < pct50 < 0:
                alerts.append({"type": "SMA50 Breakdown","ticker": tk,
                                "value": f"Price ${price:.2f} vs SMA50 ${s50:.2f}",
                                "msg": "Just broke below SMA50",                  "color": "#ff5252", "grp": 1})
            elif 0 < pct50 < 2:
                alerts.append({"type": "SMA50 Reclaim",  "ticker": tk,
                                "value": f"Price ${price:.2f} vs SMA50 ${s50:.2f}",
                                "msg": "Just reclaimed SMA50",                    "color": "#00e676", "grp": 1})

        if isinstance(dd, (int, float)):
            if dd < -50:
                alerts.append({"type": "Deep Drawdown",  "ticker": tk, "value": f"{dd:.1f}% from 52W high",
                                "msg": "Needs to double to recover",              "color": "#ff1744", "grp": 2})
            elif dd < -30:
                alerts.append({"type": "Drawdown Warning","ticker": tk,"value": f"{dd:.1f}% from 52W high",
                                "msg": "Significant drawdown — review thesis",    "color": "#ff5252", "grp": 2})

        if isinstance(price, (int, float)) and isinstance(row["High_52W"], (int, float)):
            pct_h = (price - row["High_52W"]) / row["High_52W"] * 100
            if pct_h > -5:
                alerts.append({"type": "Near 52W High",  "ticker": tk,
                                "value": f"{pct_h:+.1f}% from 52W high",
                                "msg": "Near breakout — watch for continuation",  "color": "#ffd740", "grp": 2})

    if alerts:
        a1, a2, a3 = st.columns(3)
        g_cols  = {0: a1, 1: a2, 2: a3}
        g_heads = {0: "**RSI Alerts**", 1: "**SMA50 Alerts**", 2: "**Drawdown / 52W Alerts**"}
        shown   = {0: False, 1: False, 2: False}
        for al in sorted(alerts, key=lambda x: x["grp"]):
            col = g_cols[al["grp"]]
            if not shown[al["grp"]]:
                col.markdown(g_heads[al["grp"]])
                shown[al["grp"]] = True
            col.markdown(
                f'<div style="background:#1c1f26;border-left:3px solid {al["color"]};'
                f'border-radius:0 8px 8px 0;padding:8px 12px;margin-bottom:6px">'
                f'<div style="font-size:13px;font-weight:700;color:{al["color"]}">'
                f'{al["ticker"]} — {al["type"]}</div>'
                f'<div style="font-size:11px;color:#aaa">{al["value"]}</div>'
                f'<div style="font-size:11px;color:#888;margin-top:2px">{al["msg"]}</div>'
                f'</div>', unsafe_allow_html=True)
    else:
        st.success("No active alerts.")

    # ── Drawdown tracker ──
    st.markdown("---")
    st.markdown("### 📉 Drawdown Tracker — Distance from 52-Week High")
    with st.expander("ℹ️ What is Drawdown?"):
        st.markdown(INDICATOR_EXPLANATIONS["Drawdown"])

    dd_df = df[["Ticker", "Theme", "Drawdown", "P&L %", "Signal"]].sort_values("Drawdown")
    fig_dd = px.bar(
        dd_df, x="Ticker", y="Drawdown",
        color="Theme", color_discrete_map=THEME_COLORS,
        custom_data=["P&L %", "Signal", "Theme"],
        labels={"Drawdown": "Drawdown from 52W High (%)"},
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
        tickers_in = list(corr.columns)[:55]
        corr_sub   = corr.loc[tickers_in, tickers_in]
        fig_corr   = go.Figure(data=go.Heatmap(
            z=corr_sub.values,
            x=corr_sub.columns.tolist(),
            y=corr_sub.index.tolist(),
            colorscale=[
                [0.0, "#ff1744"], [0.25, "#ff5252"],
                [0.5, "#1c1f26"],
                [0.75, "#69f0ae"], [1.0, "#00e676"],
            ],
            zmin=-1, zmax=1,
            hovertemplate="<b>%{y} / %{x}</b><br>Correlation: %{z:.2f}<extra></extra>",
            colorbar=dict(
                title=dict(text="Corr", font=dict(color="#ccc")),
                tickfont=dict(color="#ccc"),
            ),
        ))
        fig_corr.update_layout(
            height=700,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
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
    theme  = THEMES.get(ticker, "Other")
    theme_c = THEME_COLORS.get(theme, "#aaa")
    factor  = FACTORS.get(ticker, "Other")
    factor_c = FACTOR_COLORS.get(factor, "#aaa")

    st.markdown(f"# 🔍 {ticker}")
    st.markdown(
        f'<span style="background:{theme_c}22;color:{theme_c};border:1px solid {theme_c}55;'
        f'border-radius:6px;padding:3px 10px;font-size:12px;margin-right:6px">{theme}</span>'
        f'<span style="background:{factor_c}22;color:{factor_c};border:1px solid {factor_c}55;'
        f'border-radius:6px;padding:3px 10px;font-size:12px">{factor}</span>',
        unsafe_allow_html=True)

    with st.spinner(f"Loading {ticker}…"):
        DATA = fetch_all_data()
        d    = DATA[ticker]
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

    c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
    c1.metric("Price",        f"${price:.2f}")
    c2.metric("Avg Cost",     f"${ac:.2f}")
    c3.metric("Market Value", f"${cv:,.0f}")
    c4.metric("P&L",          f"${pnl:,.0f}", delta=f"{pnl_p:+.1f}%")
    c5.metric("1D Return",    f"{ind.get('Return_1D', 0):+.2f}%")
    c6.metric("1W Return",    f"{ind.get('Return_1W', 0):+.2f}%")
    c7.markdown(
        f'<div style="background:#1c1f26;border-radius:10px;padding:10px;text-align:center;'
        f'border:2px solid {sig_c};margin-top:4px">'
        f'<div style="font-size:10px;color:#aaa">SIGNAL</div>'
        f'<div style="font-size:16px;font-weight:900;color:{sig_c}">{sig}</div>'
        f'<div style="font-size:10px;color:#aaa">Score: {score:+d}</div></div>',
        unsafe_allow_html=True)

    # Drawdown + Sharpe banner
    dd      = ind.get("Drawdown", 0)
    sharpe  = ind.get("Sharpe", 0)
    dd_c    = "#ff1744" if dd < -50 else ("#ff5252" if dd < -25 else ("#ffd740" if dd < -10 else "#00e676"))
    sh_c    = "#00e676" if sharpe > 1 else ("#ffd740" if sharpe > 0 else "#ff5252")
    st.markdown(
        f'<div style="background:#1c1f26;border-radius:8px;padding:8px 14px;margin:8px 0;'
        f'border-left:4px solid {dd_c};font-size:13px;display:flex;gap:24px">'
        f'<span style="color:#fff"><b style="color:{dd_c}">Drawdown::{dd:.1f}%</b> from 52W High '
        f'(${ind.get("High_52W", price):.2f})</span>'
        f'<span><b style="color:{sh_c}">Sharpe: {sharpe:.2f}</b></span>'
        f'<span style="color:#fff">52W Low: ${ind.get("Low_52W", price):.2f}</span>'
        f'</div>', unsafe_allow_html=True)

    st.markdown("---")
    chart_tab, ind_tab, info_tab = st.tabs(["📈 Price Chart", "📊 Indicators", "🏢 Company Info"])

    with chart_tab:
        hist = d.get("hist_1y")
        if hist is not None and not hist.empty:
            close  = hist["Close"].squeeze().reset_index()
            close.columns = ["Date", "Close"]
            sma50_s  = close["Close"].rolling(50).mean()
            sma200_s = close["Close"].rolling(200).mean()
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=close["Date"], y=close["Close"],
                name="Price", line=dict(color="#5c7cfa", width=2)))
            fig_p.add_trace(go.Scatter(x=close["Date"], y=sma50_s,
                name="SMA 50", line=dict(color="#ffd740", width=1, dash="dot")))
            fig_p.add_trace(go.Scatter(x=close["Date"], y=sma200_s,
                name="SMA 200", line=dict(color="#ff5252", width=1, dash="dash")))
            fig_p.add_hline(y=ac, line_dash="dash", line_color="#00e676",
                annotation_text=f"Avg Cost ${ac:.2f}", annotation_font_color="#00e676")
            fig_p.update_layout(
                height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ccc", legend=dict(orientation="h", y=1.1),
                xaxis=dict(gridcolor="#2d3139"), yaxis=dict(gridcolor="#2d3139"),
                margin=dict(t=30, b=20), hovermode="x unified",
            )
            st.plotly_chart(fig_p, use_container_width=True)
        else:
            st.info("No historical data available.")

    with ind_tab:
        rsi_v    = ind.get("RSI",       "N/A")
        sma50_v  = ind.get("SMA50",     "N/A")
        sma200_v = ind.get("SMA200",    "N/A")
        macd_h   = ind.get("MACD_hist", "N/A")
        bb_pos   = ind.get("BB_pos",    "N/A")
        vol_r    = ind.get("Vol_ratio", "N/A")

        i1, i2, i3 = st.columns(3)

        with i1:
            st.markdown("#### RSI (14)")
            with st.expander("ℹ️ What is RSI?"):
                st.markdown(INDICATOR_EXPLANATIONS["RSI"])
            rsi_n = rsi_v if isinstance(rsi_v, (int, float)) else 50
            rsi_c = "#00e676" if rsi_n < 30 else ("#ff5252" if rsi_n > 70 else "#ffd740")
            st.markdown(f'<div style="font-size:28px;font-weight:900;color:{rsi_c}">{rsi_n}</div>', unsafe_allow_html=True)
            if   rsi_n < 30: st.success("Oversold → Bullish signal")
            elif rsi_n > 70: st.warning("Overbought → Bearish signal")
            else:            st.info("Neutral zone")

        with i2:
            st.markdown("#### MACD")
            with st.expander("ℹ️ What is MACD?"):
                st.markdown(INDICATOR_EXPLANATIONS["MACD"])
            macd_n = macd_h if isinstance(macd_h, (int, float)) else 0
            macd_c = "#00e676" if macd_n > 0 else "#ff5252"
            st.markdown(f'<div style="font-size:28px;font-weight:900;color:{macd_c}">{macd_n:+.4f}</div>', unsafe_allow_html=True)
            st.markdown(f"**Histogram:** {'Bullish' if macd_n > 0 else 'Bearish'} momentum")

        with i3:
            st.markdown("#### Bollinger Band Position")
            with st.expander("ℹ️ What are Bollinger Bands?"):
                st.markdown(INDICATOR_EXPLANATIONS["Bollinger"])
            bb_n = bb_pos if isinstance(bb_pos, (int, float)) else 0.5
            bb_c = "#00e676" if bb_n < 0.2 else ("#ff5252" if bb_n > 0.8 else "#ffd740")
            st.markdown(f'<div style="font-size:28px;font-weight:900;color:{bb_c}">{bb_n:.2f}</div>', unsafe_allow_html=True)
            if   bb_n < 0.2: st.success("Near lower band — buy zone")
            elif bb_n > 0.8: st.warning("Near upper band — sell zone")
            else:            st.info("Mid-range")

        st.markdown("---")
        st.markdown("#### Moving Averages")
        with st.expander("ℹ️ What are SMAs?"):
            st.markdown(INDICATOR_EXPLANATIONS["SMA"])
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("SMA 50",  f"${sma50_v:.2f}"  if isinstance(sma50_v,  (int, float)) else "N/A")
        m2.metric("SMA 200", f"${sma200_v:.2f}" if isinstance(sma200_v, (int, float)) else "N/A")
        if isinstance(sma50_v, (int, float)):
            p50 = (price - sma50_v) / sma50_v * 100
            m3.metric("vs SMA50",  f"{p50:+.1f}%", delta="Above" if p50 > 0 else "Below")
        if isinstance(sma200_v, (int, float)):
            p200 = (price - sma200_v) / sma200_v * 100
            m4.metric("vs SMA200", f"{p200:+.1f}%", delta="Above" if p200 > 0 else "Below")

        st.markdown("---")
        st.markdown("#### Volume & Sharpe")
        v1, v2 = st.columns(2)
        with v1:
            with st.expander("ℹ️ What does Volume tell us?"):
                st.markdown(INDICATOR_EXPLANATIONS["Volume"])
            vol_n = vol_r if isinstance(vol_r, (int, float)) else 1.0
            vol_c = "#00e676" if vol_n > 1.5 else ("#ffd740" if vol_n > 0.8 else "#888")
            st.markdown(f'<div style="font-size:22px;font-weight:700;color:{vol_c}">×{vol_n:.2f} avg vol</div>', unsafe_allow_html=True)
        with v2:
            with st.expander("ℹ️ What is Sharpe Ratio?"):
                st.markdown(INDICATOR_EXPLANATIONS["Sharpe"])
            sharpe_n = ind.get("Sharpe", 0)
            sh_c2 = "#00e676" if sharpe_n > 1 else ("#ffd740" if sharpe_n > 0 else "#ff5252")
            st.markdown(f'<div style="font-size:22px;font-weight:700;color:{sh_c2}">{sharpe_n:.2f}</div>', unsafe_allow_html=True)
            st.caption("Annualised, 1Y daily returns")

    with info_tab:
        name     = inf.get("longName") or inf.get("shortName", ticker)
        sector   = inf.get("sector",   "N/A")
        industry = inf.get("industry", "N/A")
        mktcap   = inf.get("marketCap")
        pe       = inf.get("trailingPE")
        fpe      = inf.get("forwardPE")
        ps52h    = inf.get("fiftyTwoWeekHigh")
        ps52l    = inf.get("fiftyTwoWeekLow")
        target   = inf.get("targetMeanPrice")
        analys   = inf.get("recommendationMean")

        ci1, ci2, ci3, ci4 = st.columns(4)
        ci1.markdown(f"**Name:** {name}\n\n**Sector:** {sector}\n\n**Industry:** {industry}")
        ci2.markdown(f"**Market Cap:** {'${:,.1f}B'.format(mktcap/1e9) if mktcap else 'N/A'}\n\n**P/E (trailing):** {round(pe,1) if pe else 'N/A'}\n\n**P/E (forward):** {round(fpe,1) if fpe else 'N/A'}")
        ci3.markdown(f"**52W High:** {'${:.2f}'.format(ps52h) if ps52h else 'N/A'}\n\n**52W Low:** {'${:.2f}'.format(ps52l) if ps52l else 'N/A'}\n\n**Analyst target:** {'${:.2f}'.format(target) if target else 'N/A'}")
        ci4.markdown(f"**Analyst rating:** {round(analys,2) if analys else 'N/A'} (1=Strong Buy, 5=Sell)")

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
        "Filter tickers", sorted(PORTFOLIO.keys()),
        default=list(PORTFOLIO.keys())[:10])
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
        ["ALL", "STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"])
    filtered = df if sig_filter == "ALL" else df[df["Signal"] == sig_filter]
    filtered = filtered.sort_values("Score", ascending=False)

    for _, row in filtered.iterrows():
        sig    = row["Signal"]
        color  = SIG_COLORS.get(sig, "#aaa")
        pnl_c  = pnl_color(row["P&L %"])
        ret_c  = pnl_color(row["1D %"])
        sh_c   = "#00e676" if row["Sharpe"] > 1 else ("#ffd740" if row["Sharpe"] > 0 else "#ff5252")
        st.markdown(
            f'<div style="background:#1c1f26;border-radius:10px;padding:12px 16px;'
            f'margin-bottom:8px;border-left:4px solid {color}">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div>'
            f'<span style="font-size:18px;font-weight:700;color:#ddd">{row["Ticker"]}</span>'
            f' <span style="font-size:11px;color:#666">{row["Theme"]}</span>'
            f' <span style="font-size:10px;color:#555">· {row["Factor"]}</span><br>'
            f'<span style="font-size:12px;color:#aaa">${row["Price"]:.2f}'
            f' · RSI {row["RSI"]}'
            f' · 1D <span style="color:{ret_c}">{row["1D %"]:+.2f}%</span>'
            f' · 1W {row["1W %"]:+.2f}%'
            f' · Sharpe <span style="color:{sh_c}">{row["Sharpe"]:.2f}</span>'
            f'</span>'
            f'</div>'
            f'<div style="text-align:right">'
            f'<span style="font-size:15px;font-weight:800;color:{color}">{sig}</span><br>'
            f'<span style="font-size:12px;color:{pnl_c}">{row["P&L %"]:+.1f}%</span>'
            f' <span style="font-size:11px;color:#888">Score {row["Score"]:+d}</span>'
            f'</div></div></div>',
            unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚡ Actionable Summary")
    ac1, ac2 = st.columns(2)
    with ac1:
        st.markdown("**🟢 Strong Buy / Buy:**")
        buys = df[df["Signal"].isin(["BUY", "STRONG BUY"])].sort_values("Score", ascending=False)
        for _, r in buys.iterrows():
            st.markdown(f"- **{r['Ticker']}** — Score {r['Score']:+d} | RSI {r['RSI']} | Sharpe {r['Sharpe']:.2f} | {r['P&L %']:+.1f}%")
    with ac2:
        st.markdown("**🔴 Sell / Strong Sell:**")
        sells = df[df["Signal"].isin(["SELL", "STRONG SELL"])].sort_values("Score")
        for _, r in sells.iterrows():
            st.markdown(f"- **{r['Ticker']}** — Score {r['Score']:+d} | RSI {r['RSI']} | Sharpe {r['Sharpe']:.2f} | {r['P&L %']:+.1f}%")
